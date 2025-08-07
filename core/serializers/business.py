from rest_framework import serializers
from core.models.business import Business, BusinessType


class BusinessTypeSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = BusinessType
        fields = ['id', 'code', 'name', 'description', 'icon']

    def get_icon(self, obj):
        request = self.context.get('request')
        if obj.icon:
            return request.build_absolute_uri(obj.icon.url) if request else obj.icon.url
        return None


class BusinessSerializer(serializers.ModelSerializer):
    business_type = BusinessTypeSerializer(read_only=True)
    business_type_id = serializers.PrimaryKeyRelatedField(
        queryset=BusinessType.objects.all(),
        source='business_type',
        write_only=True
    )
    logo = serializers.ImageField(required=False)  # ✅ Now allows upload

    class Meta:
        model = Business
        fields = [
            'id', 'name', 'business_type', 'business_type_id',
            'logo', 'website', 'phone', 'address', 'created_at'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")

        # ✅ Convert logo to full URL if present
        if instance.logo and request:
            rep['logo'] = request.build_absolute_uri(instance.logo.url)
        elif instance.logo:
            rep['logo'] = instance.logo.url
        else:
            rep['logo'] = None

        return rep
