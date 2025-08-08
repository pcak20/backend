from rest_framework import serializers
from core.models.site import Site
from django.core.files.storage import default_storage
import json


class SiteSerializer(serializers.ModelSerializer):
    template_data = serializers.JSONField(write_only=True, required=False)
    template_data_resolved = serializers.SerializerMethodField(read_only=True)
    template_name = serializers.CharField(
        source="template.name", read_only=True)
    business_type = serializers.CharField(  # ✅ renamed to business_type
        source="business.business_type.name",
        read_only=True
    )

    class Meta:
        model = Site
        fields = [
            "id",
            "business",
            "business_type",           # ✅ read-only
            "template",
            "template_name",
            "status",
            "template_data",
            "template_data_resolved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "status",
            "template_data_resolved",
            "business_type",           # ✅ make sure it's read-only
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        raw_data = request.data.get("template_data")

        # ✅ Allow site creation without template_data
        if raw_data:
            try:
                template_data = json.loads(raw_data)
            except Exception:
                raise serializers.ValidationError(
                    {"template_data": "Invalid JSON format."}
                )
        else:
            template_data = {}

        # Process file uploads and inject into template_data
        for key in request.FILES:
            file = request.FILES[key]
            path = f"template_uploads/{file.name}"
            saved_path = default_storage.save(path, file)
            file_url = request.build_absolute_uri(
                default_storage.url(saved_path))
            self._set_nested_key(template_data, key, file_url)

        site = Site.objects.create(
            business=validated_data["business"],
            template=validated_data["template"],
            status=validated_data.get("status", "draft"),
            template_data=template_data,
        )
        return site

    def _set_nested_key(self, data, dotted_key, value):
        """Set value in nested dictionary using dot notation."""
        keys = dotted_key.split(".")
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value

    def get_template_data_resolved(self, obj):
        return obj.template_data
