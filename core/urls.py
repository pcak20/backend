from django.urls import path
from .views import BusinessListCreateView, BusinessDetailView, BusinessTypeListView

urlpatterns = [
    path('businesses/', BusinessListCreateView.as_view(),
         name='business-list-create'),
    path('businesses/<int:pk>/', BusinessDetailView.as_view(),
         name='business-detail'),
    path('business-types/', BusinessTypeListView.as_view(),
         name='business-type-list'),
]
