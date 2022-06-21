from rest_framework.serializers import ModelSerializer

from .models import ImageUpload


class ImageUploadSerializer(ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = [
            "id",
            "file",
            "thumbnail_url",
            "is_video",
            "created_at",
        ]
