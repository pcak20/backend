from django.urls import path
from .views.business import BusinessListCreateView, BusinessDetailView, BusinessTypeListView
from .views.template import TemplateListView, TemplateDetailView
from .views.site import SiteListCreateView, SiteDetailView

urlpatterns = [
    #     BUSINESS
    path('businesses/', BusinessListCreateView.as_view(),
         name='business-list-create'),
    path('businesses/<int:pk>/', BusinessDetailView.as_view(),
         name='business-detail'),
    path('business-types/', BusinessTypeListView.as_view(),
         name='business-type-list'),

    #     TEMPLATES
    path("templates/", TemplateListView.as_view(), name="template-list"),
    path("templates/<int:pk>/", TemplateDetailView.as_view(), name="template-detail"),

    #     SITES
    path("sites/", SiteListCreateView.as_view(), name="site-list-create"),
    path("sites/<int:pk>/", SiteDetailView.as_view(), name="site-detail"),

]
