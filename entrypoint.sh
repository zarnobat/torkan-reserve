#!/bin/sh
set -e

# Ensure directories exist
mkdir -p /code/staticfiles
mkdir -p /code/media

sudo chown -R appuser:appuser /code/staticfiles /code/media
sudo chmod -R 755 /code/staticfiles /code/media
echo "--> Collecting static files..."
python manage.py collectstatic --noinput

echo "--> Applying database migrations..."
python manage.py migrate --noinput

echo "--> Starting website"
# exec python manage.py runserver 0.0.0.0:8000

exec gunicorn config.wsgi:application \
    --workers=4 \
    --worker-class=sync \
    --bind=0.0.0.0:8000 \
    --log-level=info

# echo "--> Starting Uvicorn server..."
# exec uvicorn config.asgi:application \
#     --host 0.0.0.0 \
#     --port 8000 \
#     --workers 2 \
#     --timeout-keep-alive 10

