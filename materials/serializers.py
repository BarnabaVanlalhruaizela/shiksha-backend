from rest_framework import serializers
from .models import StudyMaterial, MaterialFile


class MaterialFileSerializer(serializers.ModelSerializer):

    file_name = serializers.SerializerMethodField()

    class Meta:
        model = MaterialFile
        fields = ["id", "file", "file_name"]

    def get_file_name(self, obj):
        return obj.filename()


class StudyMaterialSerializer(serializers.ModelSerializer):

    files = MaterialFileSerializer(many=True, read_only=True)

    class Meta:
        model = StudyMaterial
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "files"
        ]
