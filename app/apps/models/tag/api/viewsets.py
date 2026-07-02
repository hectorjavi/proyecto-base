from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, viewsets

from core.swagger_schemas import r401_no_token, r403_forbidden, r404_not_found
from utils.permissions import FullModelPermissions

from ..models import Tag
from .serializers import TagSerializer

_TAG = ["Etiquetas"]


# OpenAPI no modela bien la recursión infinita; repetimos la forma del nodo
# varios niveles y documentamos que cada hijo tiene la misma estructura.
def _tag_tree_node_schema(depth: int = 0, max_depth: int = 4) -> openapi.Schema:
    """Esquema de un nodo de tag con children anidados (recursivo en la API real)."""
    base_props = {
        "id": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
        ),
        "name": openapi.Schema(type=openapi.TYPE_STRING, example="Naturaleza"),
        "parent": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            description="UUID del padre; `null` en raíces.",
            x_nullable=True,
        ),
        "parent_name": openapi.Schema(
            type=openapi.TYPE_STRING,
            x_nullable=True,
        ),
        "created": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
        ),
        "modified": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
        ),
    }
    if depth >= max_depth:
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description=(
                "Nodo de tag; en la API real `children` sigue anidándose con la misma forma."
            ),
            properties={
                **base_props,
                "children": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description=(
                        "Lista de tags hijas; cada elemento repite la estructura completa "
                        "(recursivo)."
                    ),
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Misma forma que un tag (id, name, parent, children, …).",
                    ),
                ),
            },
        )
    child = _tag_tree_node_schema(depth + 1, max_depth)
    props = {
        **base_props,
        "children": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            description="Tags hijas; cada elemento repite la misma estructura (árbol recursivo).",
            items=child,
        ),
    }
    return openapi.Schema(type=openapi.TYPE_OBJECT, properties=props)


_tag_tree_item_schema = _tag_tree_node_schema()

_EXAMPLE_TAG_NODE = {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "name": "Naturaleza",
    "parent": None,
    "parent_name": None,
    "children": [
        {
            "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "name": "Animales",
            "parent": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "parent_name": "Naturaleza",
            "children": [
                {
                    "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                    "name": "Mamíferos",
                    "parent": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                    "parent_name": "Animales",
                    "children": [],
                    "created": "2026-03-23T12:00:00Z",
                    "modified": "2026-03-23T12:00:00Z",
                }
            ],
            "created": "2026-03-23T11:00:00Z",
            "modified": "2026-03-23T11:00:00Z",
        }
    ],
    "created": "2026-03-23T10:00:00Z",
    "modified": "2026-03-23T10:00:00Z",
}

_tag_list_tree_response = openapi.Response(
    description=(
        "Listado de tags raíz en formato árbol. "
        "Cada elemento incluye `children` como lista de nodos con la misma forma (recursivo)."
    ),
    schema=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=_tag_tree_item_schema,
    ),
    # Cuerpo de ejemplo JSON (Swagger 2 / drf-yasg: mime → valor)
    examples={"application/json": [_EXAMPLE_TAG_NODE]},
)

_tag_retrieve_tree_response = openapi.Response(
    description=(
        "Un tag por ID con su subárbol en `children` (misma estructura recursiva que en el listado)."
    ),
    schema=_tag_tree_item_schema,
    examples={"application/json": _EXAMPLE_TAG_NODE},
)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=_TAG,
        operation_id="tags_list",
        operation_summary="Listar etiquetas en árbol",
        operation_description=(
            "Retorna únicamente etiquetas raíz (`parent=null`) y cada nodo incluye "
            "sus `children` de forma recursiva para representar el árbol completo.\n\n"
            "**Parámetros de query:**\n"
            "- `search` — busca por `name` o `parent__name`\n"
            "- `ordering` — ordena por `name`, `created` o `modified`\n\n"
            "**Permisos requeridos:** `view_tag`"
        ),
        responses={
            200: _tag_list_tree_response,
            401: r401_no_token,
            403: r403_forbidden,
        },
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        tags=_TAG,
        operation_id="tags_retrieve",
        operation_summary="Obtener una etiqueta",
        operation_description=(
            "Retorna una etiqueta por ID incluyendo su subárbol en `children` "
            "de forma recursiva.\n\n"
            "**Permisos requeridos:** `view_tag`"
        ),
        responses={
            200: _tag_retrieve_tree_response,
            401: r401_no_token,
            403: r403_forbidden,
            404: r404_not_found,
        },
    ),
)
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [FullModelPermissions]
    serializer_class = TagSerializer
    http_method_names = ["get"]
    queryset = Tag.objects.select_related("parent").prefetch_related("children").order_by("name")
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter)
    search_fields = ["name", "parent__name"]
    filterset_fields = ["parent"]
    ordering_fields = ["name", "created", "modified"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            return queryset.filter(parent__isnull=True)
        return queryset
