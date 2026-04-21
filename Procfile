release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT