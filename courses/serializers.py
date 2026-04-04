from .models_recordings import SessionRecording
from .models import Chapter
from rest_framework import serializers
from .models import Subject, Course, Board


class SubjectSerializer(serializers.ModelSerializer):
    teachers = serializers.SerializerMethodField()
    chapters = serializers.SerializerMethodField()

    stream_name = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    board_name = serializers.SerializerMethodField()   # ✅ NEW

    class Meta:
        model = Subject
        fields = (
            "id",
            "name",
            "order",
            "teachers",
            "chapters",
            "stream_name",
            "course_title",
            "board_name",   # ✅ USE THIS
        )

    def get_stream_name(self, obj):
        return obj.course.stream.name if obj.course and obj.course.stream else ""

    def get_course_title(self, obj):
        return obj.course.title if obj.course else ""

    def get_board_name(self, obj):   # ✅ NEW
        return obj.course.board.name if obj.course and obj.course.board else ""

    def get_teachers(self, obj):
        subject_teachers = (
            obj.subject_teachers
            .select_related("teacher__teacher_profile")
            .order_by("order")
        )

        return [
            {
                "id": st.teacher.id,
                "name": getattr(st.teacher, 'profile', None)
                and st.teacher.profile.full_name
                or st.teacher.username,
                "display_role": st.display_role,
                "qualification": getattr(st.teacher.teacher_profile, "qualification", ""),
                "bio": getattr(st.teacher.teacher_profile, "bio", ""),
                "rating": getattr(st.teacher.teacher_profile, "rating", None),
                "photo": (
                    st.teacher.teacher_profile.photo.url
                    if getattr(st.teacher, "teacher_profile", None)
                    and st.teacher.teacher_profile.photo
                    else None
                ),
            }
            for st in subject_teachers
        ]

    def get_chapters(self, obj):
        return [
            {
                "id": str(ch.id),
                "title": ch.title,
                "order": ch.order,
            }
            for ch in obj.chapters.all().order_by("order")
        ]


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ("id", "name", "board_type")


class CourseSerializer(serializers.ModelSerializer):
    board = BoardSerializer(read_only=True)
    stream_name = serializers.CharField(source="stream.name", read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "stream_name",
            "board",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ChapterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chapter
        fields = ["id", "title", "order"]


class RecordingSerializer(serializers.ModelSerializer):

    class Meta:
        model = SessionRecording
        fields = [
            "id",
            "title",
            "subject",
            "chapter",
            "session_date",
            "duration_seconds",
            "bunny_video_id",
            "thumbnail_url",
            "created_at",
        ]
