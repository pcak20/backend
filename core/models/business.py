from django.db import models
from django.contrib.auth.models import User


class BusinessType(models.Model):
    code = models.SlugField(max_length=50, unique=True)  # e.g., "restaurant"
    name = models.CharField(max_length=100)              # e.g., "Restaurant"
    description = models.TextField(blank=True)
    icon = models.ImageField(
        upload_to="business_type_icons/", blank=True, null=True)

    def __str__(self):
        return self.name


class Business(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(max_length=255)
    business_type = models.ForeignKey(
        BusinessType, on_delete=models.CASCADE, related_name='businesses')

    logo = models.ImageField(
        upload_to='business_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
