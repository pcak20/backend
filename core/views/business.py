from rest_framework import generics, permissions
from core.models.business import Business, BusinessType
from core.serializers.business import BusinessSerializer, BusinessTypeSerializer


class BusinessTypeListView(generics.ListAPIView):
    serializer_class = BusinessTypeSerializer
    queryset = BusinessType.objects.all()
    permission_classes = [permissions.AllowAny]


class BusinessListCreateView(generics.ListCreateAPIView):
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Business.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BusinessDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Business.objects.filter(owner=self.request.user)
