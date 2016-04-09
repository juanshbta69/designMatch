web: python manage.py runserver 0.0.0.0:$PORT
worker: celery --app=designMatch.celery:app worker --loglevel=INFO