from rest_framework import serializers
from core.models.site import Site
from django.core.files.storage import default_storage
import json


class SiteSerializer(serializers.ModelSerializer):
    template_data = serializers.JSONField(write_only=True, required=False)
    template_data_resolved = serializers.SerializerMethodField(read_only=True)
    template_name = serializers.CharField(
        source="template.name", read_only=True)
    business_type = serializers.CharField(
        source="business.business_type.name", read_only=True)

    class Meta:
        model = Site
        fields = [
            "id", "business", "business_type", "template", "template_name",
            "status", "template_data", "template_data_resolved",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at",
                            "status", "template_data_resolved", "business_type"]

    def create(self, validated_data):
        request = self.context.get("request")
        raw_data = request.data.get("template_data")
        template_data = {}

        if raw_data:
            try:
                template_data = json.loads(raw_data)
            except Exception:
                raise serializers.ValidationError(
                    {"template_data": "Invalid JSON format."})

        # Inject uploaded files into template_data
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

    def update(self, instance, validated_data):
        request = self.context.get("request")
        raw_data = request.data.get("template_data")

        # Start with existing template_data
        template_data = dict(instance.template_data or {})

        # Replace with new incoming data (if any)
        if raw_data:
            try:
                template_data = json.loads(raw_data)
            except Exception:
                raise serializers.ValidationError(
                    {"template_data": "Invalid JSON format."})

        # Inject uploaded files
        for key in request.FILES:
            file = request.FILES[key]
            path = f"template_uploads/{file.name}"
            saved_path = default_storage.save(path, file)
            file_url = request.build_absolute_uri(
                default_storage.url(saved_path))
            self._set_nested_key(template_data, key, file_url)

        # Restore missing images from original data
        for dotted_key, original_value in flatten_keys(instance.template_data).items():
            if isinstance(original_value, str) and original_value.startswith("http"):
                self._restore_if_placeholder(
                    template_data, dotted_key, original_value)

        instance.template = validated_data.get("template", instance.template)
        instance.status = validated_data.get("status", instance.status)
        instance.template_data = template_data
        instance.save()
        return instance

    def _set_nested_key(self, data, dotted_key, value):
        parts = dotted_key.split(".")
        cur = data

        for i, part in enumerate(parts):
            last = i == len(parts) - 1
            part = int(part) if part.isdigit() else part

            if last:
                if isinstance(cur, list):
                    while len(cur) <= part:
                        cur.append({})
                    cur[part] = value
                else:
                    cur[part] = value
                return

            next_part = parts[i + 1]
            next_should_be_list = next_part.isdigit()

            if isinstance(cur, list):
                while len(cur) <= part:
                    cur.append([] if next_should_be_list else {})
                if not isinstance(cur[part], (list if next_should_be_list else dict)):
                    cur[part] = [] if next_should_be_list else {}
                cur = cur[part]
            else:
                if part not in cur:
                    cur[part] = [] if next_should_be_list else {}
                elif next_should_be_list and not isinstance(cur[part], list):
                    cur[part] = []
                elif not next_should_be_list and not isinstance(cur[part], dict):
                    cur[part] = {}
                cur = cur[part]

    def _restore_if_placeholder(self, data, dotted_key, original_value):
        try:
            parts = dotted_key.split(".")
            cur = data
            for i, part in enumerate(parts[:-1]):
                part = int(part) if part.isdigit() else part
                cur = cur[part]
            last_key = parts[-1]
            if cur.get(last_key) == dotted_key:
                cur[last_key] = original_value
        except Exception:
            pass

    def get_template_data_resolved(self, obj):
        return obj.template_data


def flatten_keys(data, prefix=""):
    """
    Flattens nested dict/list into dot-keyed structure.
    Example: {"hero": [{"image": "url"}]} → {"hero.0.image": "url"}
    """
    flat = {}
    if isinstance(data, dict):
        for k, v in data.items():
            path = f"{prefix}.{k}" if prefix else k
            flat.update(flatten_keys(v, path))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            path = f"{prefix}.{i}"
            flat.update(flatten_keys(v, path))
    else:
        flat[prefix] = data
    return flat
