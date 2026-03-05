from rest_framework import serializers
from django.utils import timezone
from .models import Assignment, AssignmentSubmission
from courses.models import Chapter
import os


# ==========================================
# FILE TYPE VALIDATOR
# ==========================================

# Blocked for security - dangerous executable/script extensions
BLOCKED_EXTENSIONS = [
    ".exe", ".bat", ".cmd", ".sh", ".bash",
    ".php", ".py", ".rb", ".pl", ".cgi",
    ".js", ".vbs", ".ps1", ".msi", ".dll",
    ".com", ".scr", ".jar", ".app",
]


def validate_assignment_file(file):
    """
    Allows all file types except dangerous executables/scripts.
    Suitable for any LMS platform (PC, Android, iPhone).
    Max file size: 100MB
    """
    if file is None:
        return file

    # Check extension against blocked list
    ext = os.path.splitext(file.name)[1].lower()
    if ext in BLOCKED_EXTENSIONS:
        raise serializers.ValidationError(
            f"File type '{ext}' is not allowed for security reasons."
        )

    # Max file size: 100MB
    max_size = 100 * 1024 * 1024
    if file.size > max_size:
        raise serializers.ValidationError(
            "File too large. Maximum allowed size is 100MB."
        )

    return file


# ==========================================
# STUDENT SERIALIZERS
# ==========================================

class AssignmentListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    subject_name = serializers.CharField(
        source="chapter.subject.name",
        read_only=True
    )
    course_id = serializers.UUIDField(
        source="chapter.subject.course.id",
        read_only=True
    )
    # ✅ FIX 1: Added attachment so students can see uploaded files
    attachment = serializers.FileField(read_only=True)

    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "due_date",
            "status",
            "subject_name",
            "course_id",
            "attachment",
        )

    def get_status(self, obj):
        submission = getattr(obj, "user_submission", None)

        if submission:
            return "SUBMITTED"

        if obj.due_date < timezone.now():
            return "EXPIRED"

        return "PENDING"


class AssignmentDetailSerializer(serializers.ModelSerializer):
    submission_status = serializers.SerializerMethodField()
    submitted_file = serializers.SerializerMethodField()
    submitted_at = serializers.SerializerMethodField()
    subject_name = serializers.CharField(
        source="chapter.subject.name",
        read_only=True
    )
    course_name = serializers.CharField(
        source="chapter.subject.course.title",
        read_only=True
    )

    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "description",
            "attachment",
            "due_date",
            "subject_name",
            "course_name",
            "submission_status",
            "submitted_file",
            "submitted_at",
        )

    def get_submission(self, obj):
        return getattr(obj, "user_submission", None)

    def get_submission_status(self, obj):
        submission = self.get_submission(obj)

        if submission:
            return "SUBMITTED"

        if obj.due_date < timezone.now():
            return "EXPIRED"

        return "PENDING"

    def get_submitted_file(self, obj):
        submission = self.get_submission(obj)
        if submission and submission.submitted_file:
            return submission.submitted_file.url
        return None

    def get_submitted_at(self, obj):
        submission = self.get_submission(obj)
        return submission.submitted_at if submission else None


# ==========================================
# TEACHER SERIALIZERS
# ==========================================

class TeacherAssignmentCreateSerializer(serializers.ModelSerializer):
    chapter_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Assignment
        fields = (
            "chapter_id",
            "title",
            "description",
            "due_date",
            "attachment",
        )

    def validate(self, attrs):
        if attrs["due_date"] < timezone.now():
            raise serializers.ValidationError(
                "Due date must be in the future."
            )
        return attrs

    def validate_chapter_id(self, value):
        try:
            Chapter.objects.select_related(
                "subject__course"
            ).get(id=value)
        except Chapter.DoesNotExist:
            raise serializers.ValidationError("Invalid chapter.")
        return value

    # ✅ File type validation on create
    def validate_attachment(self, value):
        return validate_assignment_file(value)

    def create(self, validated_data):
        chapter_id = validated_data.pop("chapter_id")
        chapter = Chapter.objects.get(id=chapter_id)

        return Assignment.objects.create(
            chapter=chapter,
            **validated_data
        )


class TeacherAssignmentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment
        fields = (
            "title",
            "description",
            "due_date",
            "attachment",
        )

    def validate_due_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Due date must be in the future."
            )
        return value

    # ✅ File type validation on update
    def validate_attachment(self, value):
        return validate_assignment_file(value)


class TeacherAssignmentListSerializer(serializers.ModelSerializer):
    chapter_name = serializers.CharField(
        source="chapter.title",
        read_only=True
    )
    total_submissions = serializers.IntegerField(
        read_only=True
    )
    is_expired = serializers.BooleanField(
        source="is_expired",
        read_only=True
    )
    # ✅ FIX 2: Added attachment so teacher sees file in response after create/update
    attachment = serializers.FileField(read_only=True)

    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "chapter_name",
            "due_date",
            "is_expired",
            "total_submissions",
            "attachment",
        )


class TeacherSubmissionListSerializer(serializers.ModelSerializer):
    student_id = serializers.UUIDField(
        source="student.id",
        read_only=True
    )
    student_email = serializers.EmailField(
        source="student.email",
        read_only=True
    )
    student_name = serializers.CharField(
        source="student.profile.full_name",
        read_only=True
    )

    class Meta:
        model = AssignmentSubmission
        fields = (
            "id",
            "student_id",
            "student_email",
            "student_name",
            "submitted_file",
            "submitted_at",
        )
