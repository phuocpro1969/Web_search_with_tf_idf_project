from rest_framework import permissions, viewsets

from data.models import Data
from data.serializers import DataSerializer

# Lead Viewset


class DataViewSet(viewsets.ModelViewSet):
    queryset = Data.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = DataSerializer
