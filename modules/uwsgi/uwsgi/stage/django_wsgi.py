import os
import django.core.handlers.wsgi

os.environ['DJANGO_SETTINGS_MODULE'] = '$PROJECT_NAME.settings.stage'
application = django.core.handlers.wsgi.WSGIHandler()
