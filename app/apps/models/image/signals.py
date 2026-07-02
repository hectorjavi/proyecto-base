import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from PIL import Image as PilImage
from PIL import ImageOps

from .models import Image

MAX_IMAGE_SIDE = 2500
JPEG_QUALITY = 90


def _calculate_target_size(width, height):
    """
    Calcula el tamaño destino manteniendo proporción.

    - Si el lado mayor no supera MAX_IMAGE_SIDE, conserva el tamaño original.
    - Si lo supera, reduce usando el lado mayor como referencia.
    - Nunca amplía la imagen.
    """
    longest_side = max(width, height)

    if longest_side <= MAX_IMAGE_SIDE:
        return width, height

    scale = MAX_IMAGE_SIDE / float(longest_side)
    return (
        max(1, round(width * scale)),
        max(1, round(height * scale)),
    )


def _normalize_to_jpeg(instance):
    """
    Convierte la imagen a JPEG y la redimensiona si supera MAX_IMAGE_SIDE.

    - Siempre guarda en formato JPEG independientemente del formato original.
    - Convierte modos con alpha (RGBA, P) a RGB antes de guardar.
    - Corrige orientación EXIF.
    - Renombra el archivo con extensión .jpg.
    - Solo actúa sobre archivos nuevos no committed.
    - Si la imagen ya es JPEG y está dentro del límite de tamaño, la omite
      para evitar re-codificación innecesaria (ej. cuando la API pipeline ya
      la procesó antes de llegar al signal).
    """
    uploaded_file = getattr(instance, "file", None)
    if not uploaded_file or getattr(uploaded_file, "_committed", True):
        return

    uploaded_file.open()
    try:
        with PilImage.open(uploaded_file) as img:
            width, height = img.size
            already_jpeg = (img.format or "").upper() in ("JPEG", "JPG")
            within_bounds = max(width, height) <= MAX_IMAGE_SIDE

            if already_jpeg and within_bounds:
                uploaded_file.seek(0)
                return

            normalized = ImageOps.exif_transpose(img)
            width, height = normalized.size

            target_width, target_height = _calculate_target_size(width, height)

            if (target_width, target_height) != (width, height):
                output_img = normalized.resize(
                    (target_width, target_height),
                    PilImage.Resampling.LANCZOS,
                )
            else:
                output_img = normalized

            if output_img.mode not in ("RGB", "L"):
                output_img = output_img.convert("RGB")

            icc_profile = img.info.get("icc_profile")
            save_kwargs = {
                "quality": JPEG_QUALITY,
                "optimize": True,
                "progressive": True,
            }
            if icc_profile:
                save_kwargs["icc_profile"] = icc_profile

            output = BytesIO()
            output_img.save(output, format="JPEG", **save_kwargs)
            output.seek(0)

        original_name = os.path.basename(uploaded_file.name)
        base, _ = os.path.splitext(original_name)
        jpg_name = base + ".jpg"

        uploaded_file.save(
            jpg_name,
            ContentFile(output.read()),
            save=False,
        )

        uploaded_file.seek(0)

    finally:
        try:
            uploaded_file.seek(0)
        except Exception:
            pass


@receiver(pre_save, sender=Image)
def set_file_name(sender, instance, **kwargs):
    if not instance.file:
        instance.file_name = ""
        instance.file_extension = ""
        return

    previous = None
    old_file_name = None

    # En create: siempre refresca metadata.
    # En update: solo si cambió el archivo o si es un upload nuevo no committed.
    should_refresh = instance._state.adding

    if instance.file and not getattr(instance.file, "_committed", True):
        should_refresh = True

    if not should_refresh and instance.pk:
        previous = sender.objects.filter(pk=instance.pk).only("file").first()
        old_file_name = previous.file.name if previous and previous.file else None
        should_refresh = not previous or old_file_name != instance.file.name

    _normalize_to_jpeg(instance)

    if should_refresh and instance.file:
        name = os.path.basename(instance.file.name)
        _, ext = os.path.splitext(name)
        instance.file_name = name
        instance.file_extension = ext.lower()

    # Si el archivo cambió, elimina el anterior luego del commit.
    if previous and old_file_name and old_file_name != instance.file.name:
        old_storage = previous.file.storage
        transaction.on_commit(lambda: old_storage.delete(old_file_name))


@receiver(post_delete, sender=Image)
def delete_file_from_storage(sender, instance, **kwargs):
    if instance.file and instance.file.name:
        file_name = instance.file.name
        storage = instance.file.storage
        transaction.on_commit(lambda: storage.delete(file_name))