from django.db import models
from core.models.business import Business
from django.core.exceptions import ValidationError
from core.models.template import Template


class SiteStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    DRAFT = 'draft', 'Draft'


class Site(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="sites"
    )
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="sites"
    )
    status = models.CharField(
        max_length=20, choices=SiteStatus.choices, default=SiteStatus.DRAFT)

    # 🧠 All user content (hero, menu, footer, etc.) stored here
    template_data = models.JSONField(blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business"],
                condition=models.Q(status="active"),
                name="unique_active_site_per_business"
            )
        ]
        ordering = ["-created_at"]

    def clean(self):
        # Business can only have up to 2 sites
        if self.business.sites.count() >= 2 and not self.pk:
            raise ValidationError("A business can only have up to 2 sites.")

    def __str__(self):
        return f"{self.business.name} - {self.template.name} ({self.status})"
