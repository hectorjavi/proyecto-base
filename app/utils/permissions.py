from rest_framework.permissions import DjangoModelPermissions


class FullModelPermissions(DjangoModelPermissions):
    """
    Model-level ACL permission class built on top of DRF's DjangoModelPermissions.

    Why this is better than manual DB queries:
    - Uses Django's built-in `user.has_perm()` which is cached in `user._perm_cache`
      after the first call → O(1) on repeated checks within the same request.
    - Superusers are always granted access without hitting the database.
    - Group-inherited permissions are resolved automatically by Django's auth backend.
    - Works with custom authentication backends (e.g. LDAP, OAuth).
    - The model is inferred from the view's `queryset`, so no coupling to a specific model.

    HTTP method → required permission mapping:
        GET    / HEAD / OPTIONS → view_<model>
        POST                   → add_<model>
        PUT  / PATCH           → change_<model>
        DELETE                 → delete_<model>

    Usage in any ViewSet:
        permission_classes = [FullModelPermissions]
    """

    # DRF's base DjangoModelPermissions leaves GET/HEAD/OPTIONS unrestricted.
    # We override perms_map to also require 'view_*' for read operations,
    # giving full CRUD-level control out of the box.
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }
