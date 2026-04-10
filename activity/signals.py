from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from assignments.models import Assignment
from quizzes.models import Quiz
from livestream.models import LiveSession
from enrollments.models import Enrollment

from .services import create_activity
from .models import Activity
from livestream.services.notifications import push_ws_notification


# =========================
# ASSIGNMENT CREATED
# =========================
@receiver(post_save, sender=Assignment)
def assignment_created(sender, instance, created, **kwargs):
    if not created:
        return

    course = instance.chapter.subject.course
    students = Enrollment.objects.filter(
        course=course,
        status=Enrollment.STATUS_ACTIVE
    ).select_related("user")

    content_type = ContentType.objects.get_for_model(instance)

    # 🔥 bulk create activities for students
    Activity.objects.bulk_create([
        Activity(
            user=enrollment.user,
            type=Activity.TYPE_ASSIGNMENT,
            title=f"New assignment: {instance.title}",
            due_date=instance.due_date,
            content_type=content_type,
            object_id=instance.id,
        )
        for enrollment in students
    ])

    # 🔥 push WebSocket notification to each student
    for enrollment in students:
        push_ws_notification(enrollment.user.id, {
            'type': 'assignment',
            'title': f"New assignment: {instance.title}",
            'due_date': str(instance.due_date) if instance.due_date else None,
            'id': str(instance.id),
        })

    # 🔥 notify teacher
    teachers = instance.chapter.subject.subject_teachers.select_related(
        "teacher").all()
    for st in teachers:
        create_activity(
            user=st.teacher,
            obj=instance,
            type=Activity.TYPE_ASSIGNMENT,
            title=f"You created: {instance.title}",
            due_date=instance.due_date
        )
        push_ws_notification(st.teacher.id, {
            'type': 'assignment',
            'title': f"You created: {instance.title}",
            'due_date': str(instance.due_date) if instance.due_date else None,
            'id': str(instance.id),
        })


# =========================
# QUIZ PUBLISHED
# =========================
@receiver(post_save, sender=Quiz)
def quiz_published(sender, instance, created, **kwargs):
    if not instance.is_published:
        return

    course = instance.subject.course
    students = Enrollment.objects.filter(
        course=course,
        status=Enrollment.STATUS_ACTIVE
    ).select_related("user")

    content_type = ContentType.objects.get_for_model(instance)

    # 🔥 bulk create activities for students
    Activity.objects.bulk_create([
        Activity(
            user=enrollment.user,
            type=Activity.TYPE_QUIZ,
            title=f"Quiz available: {instance.title}",
            due_date=instance.due_date,
            content_type=content_type,
            object_id=instance.id,
        )
        for enrollment in students
    ])

    # 🔥 push WebSocket notification to each student
    for enrollment in students:
        push_ws_notification(enrollment.user.id, {
            'type': 'quiz',
            'title': f"Quiz available: {instance.title}",
            'due_date': str(instance.due_date) if instance.due_date else None,
            'id': str(instance.id),
        })

    # 🔥 notify teacher
    user = getattr(instance, "created_by", None)
    if user:
        create_activity(
            user=user,
            obj=instance,
            type=Activity.TYPE_QUIZ,
            title=f"You published quiz: {instance.title}",
            due_date=instance.due_date
        )
        push_ws_notification(user.id, {
            'type': 'quiz',
            'title': f"You published quiz: {instance.title}",
            'due_date': str(instance.due_date) if instance.due_date else None,
            'id': str(instance.id),
        })


# =========================
# LIVE SESSION CREATED
# =========================
@receiver(post_save, sender=LiveSession)
def session_created(sender, instance, created, **kwargs):
    if not created:
        return

    course = instance.course
    students = Enrollment.objects.filter(
        course=course,
        status=Enrollment.STATUS_ACTIVE
    ).select_related("user")

    content_type = ContentType.objects.get_for_model(instance)

    # 🔥 bulk create activities for students
    Activity.objects.bulk_create([
        Activity(
            user=enrollment.user,
            type=Activity.TYPE_SESSION,
            title=f"Live session scheduled: {instance.title}",
            due_date=instance.start_time,
            content_type=content_type,
            object_id=instance.id,
        )
        for enrollment in students
    ])

    # 🔥 push WebSocket notification to each student
    for enrollment in students:
        push_ws_notification(enrollment.user.id, {
            'type': 'live_session',
            'title': f"Live session scheduled: {instance.title}",
            'start_time': instance.start_time.isoformat(),
            'id': str(instance.id),
        })

    # 🔥 notify teacher
    user = getattr(instance, "created_by", None)
    if user:
        create_activity(
            user=user,
            obj=instance,
            type=Activity.TYPE_SESSION,
            title=f"You scheduled session: {instance.title}",
            due_date=instance.start_time
        )
        push_ws_notification(user.id, {
            'type': 'live_session',
            'title': f"You scheduled session: {instance.title}",
            'start_time': instance.start_time.isoformat(),
            'id': str(instance.id),
        })
