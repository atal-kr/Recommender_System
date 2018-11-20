import os
from applications.recommendation.models import *
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recommender_service.settings")
application = get_wsgi_application()