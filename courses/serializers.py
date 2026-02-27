from rest_framework import serializers
from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    teacher_names = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = (
            "id",
            "name",
            "order",
            "teacher_names",
        )

    def get_teacher_names(self, obj):
        return [
            teacher.username
            for teacher in obj.teachers.all()
        ]
