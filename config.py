import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'your_secret_key_here'  # 실제 서비스 시 안전하게 변경하세요

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False  # HTTPS 환경에서는 True로 설정 권장

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB 제한

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'uploads.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

PERMANENT_SESSION_LIFETIME = timedelta(days=7)
