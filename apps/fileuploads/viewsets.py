from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from .models import ImageUpload
from .serializers import ImageUploadSerializer


class ImageUploadViewSet(ModelViewSet):
    queryset = ImageUpload.objects.all()
    serializer_class = ImageUploadSerializer

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied
