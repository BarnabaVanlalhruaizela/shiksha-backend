from .settings_base import *

ALLOWED_HOSTS = [
    "134.209.154.122",
    "dev.api.shikshacom.com",
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://dev.api.shikshacom.com",
    "https://dev.shikshacom.com",
    "https://dev.app.shikshacom.com",
    "https://dev.teacher.shikshacom.com",
]

CORS_ALLOWED_ORIGINS = [
    "https://dev.shikshacom.com",
    "https://dev.app.shikshacom.com",
    "https://dev.teacher.shikshacom.com",
]
