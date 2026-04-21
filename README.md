# TaskManager

Collaborative task management web app built with Django 5, Django REST Framework, Bootstrap 5, SQLite, and optional Docker support.

## Features

- Custom user model with profile fields
- Session-based authentication with registration and password reset
- Team collaboration with invite codes
- Task CRUD, comments, filtering, assignment, and notifications
- DRF API endpoints for future frontend expansion
- Bootstrap dashboard with Chart.js summary
- Basic automated tests, Docker files, CI workflow, and sample fixture

## Project Structure

- `core/`: Django project configuration
- `tasks/`: Main application for auth, teams, tasks, comments, notifications, and API
- `templates/`: Shared Django templates
- `static/`: Minimal styling assets
- `fixtures/`: Sample data fixture

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment variables:

```bash
cp .env.example .env
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Optionally load demo data:

```bash
python manage.py loaddata fixtures/sample_data.json
```

6. Create a superuser:

```bash
python manage.py createsuperuser
```

7. Start the development server:

```bash
python manage.py runserver
```

## Password Reset

Password reset uses Django's console email backend in development. Reset emails print to the terminal running `runserver`.

## API Endpoints

- `POST /api/register/`
- `POST /api/login/`
- `POST /api/logout/`
- `GET|POST /api/teams/`
- `POST /api/teams/<id>/join/`
- `GET|POST|PUT|PATCH|DELETE /api/tasks/`
- `GET|POST /api/tasks/<id>/comments/`
- `GET /api/notifications/`
- `GET /api/dashboard/stats/`

## Docker

Build and run with Docker Compose:

```bash
docker-compose up --build
```

## Testing

Run the test suite with:

```bash
python manage.py test
```
