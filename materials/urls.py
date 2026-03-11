from django.urls import path
from .views import ChapterMaterials, UploadStudyMaterial, DeleteStudyMaterial

urlpatterns = [

    path(
        "chapters/<uuid:chapter_id>/materials/",
        ChapterMaterials.as_view(),
    ),

    path(
        "chapters/<uuid:chapter_id>/materials/upload/",
        UploadStudyMaterial.as_view(),
    ),

    path(
        "materials/<uuid:material_id>/",
        DeleteStudyMaterial.as_view(),
    ),

]
