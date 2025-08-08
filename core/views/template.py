# core/views/template.py
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny  # or IsAuthenticated if needed
from core.models.template import Template
from core.serializers.template import TemplateSerializer


class TemplateListView(ListAPIView):
    """
    GET /api/core/templates/?business_type=<code>
    """
    serializer_class = TemplateSerializer
    permission_classes = [AllowAny]  # or IsAuthenticated

    def get_queryset(self):
        qs = Template.objects.select_related("business_type").all()
        bt_code = self.request.query_params.get("business_type")
        if bt_code:
            qs = qs.filter(business_type__code=bt_code)
        return qs


class TemplateDetailView(RetrieveAPIView):
    """
    GET /api/core/templates/<pk>/
    """
    queryset = Template.objects.select_related("business_type").all()
    serializer_class = TemplateSerializer
    permission_classes = [AllowAny]  # or IsAuthenticated
