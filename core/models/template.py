from django.db import models


class Template(models.Model):
    business_type = models.ForeignKey(
        "core.BusinessType",
        on_delete=models.CASCADE,
        related_name="templates"
    )
    name = models.CharField(max_length=100)  # e.g. "Classic"
    code = models.SlugField(max_length=50)   # e.g. "classic"
    description = models.TextField(blank=True)
    preview_image = models.ImageField(
        upload_to="template_previews/", blank=True, null=True)
    # Optional: JSON form schema
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('business_type', 'code')
        ordering = ['business_type__name', 'name']

    def __str__(self):
        return f"{self.business_type.name} - {self.name}"
