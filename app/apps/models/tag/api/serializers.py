from rest_framework import serializers

from apps.models.tag.models import Tag


class TagSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return TagSerializer(obj.children.all().order_by("name"), many=True, context=self.context).data

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "parent",
            "parent_name",
            "children",
            "created",
            "modified",
        )
