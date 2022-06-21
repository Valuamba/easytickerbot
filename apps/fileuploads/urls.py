from django.urls import path

from .views import ImageUploadView

app_name = "fileuploads"

urlpatterns = [
    path("upload/image", ImageUploadView.as_view(), name="upload_image"),
]
