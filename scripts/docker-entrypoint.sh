#!/bin/bash
python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn lookupproxy.wsgi:application \
    --name lookupproxy \
    --bind 0.0.0.0:8080 \
    --workers 3 \
    --log-level=info \
    --log-file=- \
    --access-logfile=- \
    "$@"
