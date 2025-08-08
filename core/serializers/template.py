from rest_framework import serializers
from core.models.site import Template


class TemplateSerializer(serializers.ModelSerializer):
    business_type_name = serializers.CharField(
        source='business_type.name', read_only=True)
    business_type_id = serializers.PrimaryKeyRelatedField(
        queryset=Template._meta.get_field(
            'business_type').related_model.objects.all(),
        source='business_type',
        write_only=True
    )
    preview_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = [
            'id', 'name', 'code', 'description',
            'business_type_id', 'business_type_name',
            'preview_image', 'preview_image_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_preview_image_url(self, obj):
        request = self.context.get("request")
        if obj.preview_image:
            return request.build_absolute_uri(obj.preview_image.url) if request else obj.preview_image.url
        return None
