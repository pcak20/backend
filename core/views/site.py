# core/views/site.py
from rest_framework import generics, permissions, filters
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from core.models.site import Site
from core.serializers.site import SiteSerializer
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from core.models.site import Site, SiteStatus  # import your enum/status


class SiteListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/core/sites/?business=<id>   -> list sites (optionally filter by business)
    POST /api/core/sites/                 -> create site (supports template_data + files)
    """
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = Site.objects.select_related(
            "business__business_type", "template").all()
        business_id = self.request.query_params.get("business")
        if business_id:
            qs = qs.filter(business_id=business_id)
        return qs

    def perform_create(self, serializer):
        request = self.request
        business = serializer.validated_data["business"]

        # Ownership check
        if business.owner != request.user:
            raise PermissionDenied("You do not own this business.")

        # Max 2 sites
        if business.sites.count() >= 2:
            raise ValidationError("Maximum 2 sites allowed per business.")

        # Create and ensure only one active
        with transaction.atomic():
            site = serializer.save()
            if site.status == SiteStatus.ACTIVE:
                Site.objects.filter(business=business).exclude(pk=site.pk).update(
                    status=SiteStatus.DRAFT
                )
        return site


class SiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/core/sites/<pk>/    -> fetch single site (for editor)
    PATCH  /api/core/sites/<pk>/    -> partial update (status, template_data via our create/update logic)
    PUT    /api/core/sites/<pk>/    -> full update
    DELETE /api/core/sites/<pk>/    -> delete site
    """
    queryset = Site.objects.select_related(
        "business__business_type", "template").all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_update(self, serializer):
        request = self.request
        current = self.get_object()

        # Ownership check
        if current.business.owner != request.user:
            raise PermissionDenied("You do not own this business.")

        # Do not allow moving a site to a different business via update
        new_business = serializer.validated_data.get("business")
        if new_business and new_business != current.business:
            raise ValidationError(
                "Cannot move a site to a different business.")

        prev_status = current.status

        with transaction.atomic():
            site = serializer.save()

            # If status changed to active, demote others to draft
            if site.status == SiteStatus.ACTIVE and prev_status != SiteStatus.ACTIVE:
                Site.objects.filter(business=site.business).exclude(pk=site.pk).update(
                    status=SiteStatus.DRAFT
                )
        return site
