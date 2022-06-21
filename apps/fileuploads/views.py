from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ImageUpload


class ImageUploadView(APIView):
    parser_classes = [FileUploadParser]

    def post(self, request, format=None):
        file_obj = request.data["file"]
        image_upload = ImageUpload()
        image_upload.file.save(file_obj.name, file_obj, save=True)
        image_upload.save()

        file_size = file_obj.size
        max_file_size = 50 * 1024 * 1024
        if file_size >= max_file_size:
            extra_headers = {"X-Api-Error": "too_large"}
        else:
            extra_headers = {}

        return Response(
            status=204, headers={"X-Upload-Id": image_upload.id, **extra_headers}
        )
