from courses.models import Subject
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import StudyMaterial, MaterialFile
from .serializers import StudyMaterialSerializer
from courses.models import Chapter


# ===============================
# LIST MATERIALS OF A CHAPTER
# ===============================

class ChapterMaterials(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, chapter_id):

        chapter = get_object_or_404(Chapter, id=chapter_id)

        materials = (
            StudyMaterial.objects
            .filter(chapter=chapter)
            .prefetch_related("files")
            .order_by("-created_at")
        )

        serializer = StudyMaterialSerializer(
            materials, many=True, context={"request": request}
        )

        return Response(serializer.data)


# ===============================
# UPLOAD STUDY MATERIAL
# ===============================

class UploadStudyMaterial(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, chapter_id=None):

        chapter_id = request.data.get("chapter_id")
        custom_chapter = request.data.get("custom_chapter")

        # ✅ Chapter logic
        if chapter_id:
            chapter = get_object_or_404(Chapter, id=chapter_id)

        elif custom_chapter:
            subject_id = request.data.get("subject_id")

            if not subject_id:
                return Response(
                    {"detail": "Subject is required for custom chapter"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subject = get_object_or_404(Subject, id=subject_id)

            chapter = Chapter.objects.create(
                subject=subject,
                title=custom_chapter
            )

        else:
            return Response(
                {"detail": "Chapter or custom chapter required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        title = request.data.get("title")
        file_ids = request.data.getlist("file_ids")

        if not title:
            return Response({"detail": "Title is required"}, status=400)

        if not file_ids:
            return Response({"detail": "At least one file required"}, status=400)

        # ✅ CREATE MATERIAL FIRST
        material = StudyMaterial.objects.create(
            chapter=chapter,
            title=title,
            description=request.data.get("description", ""),
            uploaded_by=request.user
        )

        # ✅ ATTACH FILES
        for fid in file_ids:
            file = get_object_or_404(MaterialFile, id=fid)
            file.material = material
            file.save()

        serializer = StudyMaterialSerializer(material, context={"request": request})

        return Response(serializer.data, status=201)


# ===============================
# DELETE MATERIAL
# ===============================

class DeleteStudyMaterial(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, material_id):

        material = get_object_or_404(StudyMaterial, id=material_id)

        material.delete()

        return Response(
            {"detail": "Material deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


# ===============================
# LIST MATERIALS OF A SUBJECT
# ===============================

class SubjectMaterials(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):

        subject = get_object_or_404(Subject, id=subject_id)

        materials = (
            StudyMaterial.objects
            .filter(chapter__subject=subject)
            .prefetch_related("files")
            .order_by("-created_at")
        )

        serializer = StudyMaterialSerializer(
            materials, many=True, context={"request": request}
        )

        return Response(serializer.data)


# ===============================
# STUDENT SUBJECT MATERIALS
# ===============================

class StudentSubjectMaterials(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):

        subject = get_object_or_404(Subject, id=subject_id)

        materials = (
            StudyMaterial.objects
            .filter(chapter__subject=subject)
            .select_related("chapter")
            .prefetch_related("files")
            .order_by("-created_at")
        )

        serializer = StudyMaterialSerializer(
            materials, many=True, context={"request": request}
        )

        return Response(serializer.data)


# ===============================
# MATERIAL DETAIL (NEW)
# ===============================

class StudyMaterialDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, material_id):

        material = get_object_or_404(
            StudyMaterial.objects.prefetch_related("files"),
            id=material_id
        )

        serializer = StudyMaterialSerializer(
            material,
            context={"request": request}
        )

        return Response(serializer.data)
    
class UploadTempFile(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        file = request.FILES.get("file")

        if not file:
            return Response({"detail": "File required"}, status=400)

        temp = MaterialFile.objects.create(
            file=file,
            material=None  # 🔥 allow null temporarily
        )

        return Response({
            "id": str(temp.id),
            "file_name": temp.filename(),
            "file_url": temp.file.url
        }, status=201)