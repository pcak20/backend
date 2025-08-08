from django.contrib import admin
from .models.business import Business, BusinessType
from .models.site import Template, Site

admin.site.register(Business)
admin.site.register(BusinessType)

admin.site.register(Site)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'business_type']
    list_filter = ['business_type']
