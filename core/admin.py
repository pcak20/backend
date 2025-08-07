from django.contrib import admin
from .models.business import Business, BusinessType

admin.site.register(Business)
admin.site.register(BusinessType)
