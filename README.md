# Todo App

---

**Table of Contents**
1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Database Description](#database-description)
4. [Application Description](#application-description)
5. [How to Run the Project](#how-to-run-the-project)
6. [Technologies](#technologies)

---

## Project Overview

This project is a Django web application for managing daily tasks and tags. It provides a simple interface for creating, updating, completing, and deleting tasks, while also allowing separate CRUD management for task tags.

The workflow includes:
1. Creating tags for task grouping
2. Creating tasks with optional deadlines
3. Assigning one or more tags to a task
4. Marking tasks as done or undoing completion
5. Updating or deleting tasks and tags

---

## Project Structure

```text
todo-app/
|-- app/                              # Main Django application
|   |-- migrations/                   # Database migrations
|   |-- admin.py                      # Admin site configuration
|   |-- forms.py                      # Model forms for tasks and tags
|   |-- models.py                     # Task and Tag models
|   |-- tests.py                      # Automated test suite
|   |-- urls.py                       # Application URL routes
|   |-- views.py                      # Generic CRUD views and task toggle view
|   `-- __init__.py
|-- config/                           # Django project configuration
|   |-- settings.py                   # Project settings
|   |-- urls.py                       # Root URL configuration
|   |-- asgi.py                       # ASGI entrypoint
|   |-- wsgi.py                       # WSGI entrypoint
|   `-- __init__.py
|-- static/
|   `-- css/
|       `-- styles.css                # Custom styles
|-- templates/
|   |-- includes/                     # Shared template partials
|   |-- todo/                         # Task and tag templates
|   `-- base.html                     # Base layout
|-- db.sqlite3                        # SQLite database
|-- manage.py                         # Django management entrypoint
|-- README.md
|-- README_example.md
`-- requirements.txt                  # Project dependencies
```

---

## Database Description

The project uses SQLite as the default database and includes two main models:

- **Tag**
  - Stores task categories
  - Contains a unique `name` field
  - Ordered alphabetically by name

- **Task**
  - Stores the main todo item text in `content`
  - Automatically stores `created_at`
  - Supports an optional `deadline`
  - Tracks completion with `is_done`
  - Can be linked to multiple tags

Relationships:
- One `Tag` -> many `Task` objects through a many-to-many relation
- One `Task` -> many `Tag` objects

---

## Application Description

The application is built with Django generic class-based views and custom templates.

- Task features
  - View the task list on the home page
  - Create a new task
  - Update an existing task
  - Delete a task
  - Toggle a task between done and not done

- Tag features
  - View all tags
  - Create a new tag
  - Update an existing tag
  - Delete a tag

- Interface details
  - Tasks show their created date, optional deadline, and completion state
  - Tasks display their assigned tags on the page
  - A sidebar provides navigation between the task list and tag list

The Django admin is also configured for both models at `/admin/`.

---

## How to Run the Project

Follow these steps to set up the project locally.

### 1. Prerequisites

- Python 3.12+
- Git
- Virtual environment tool (`venv`)

### 2. Installation

2.1. Clone the repository:

```commandline
git clone https://github.com/mishagitcode/todo-app.git
```

```commandline
cd todo-app
```

2.2. Create a virtual environment:

```commandline
python -m venv venv
```

2.3. Activate the virtual environment

Windows:

```commandline
venv\Scripts\activate
```

macOS/Linux:

```commandline
source venv/bin/activate
```

2.4. Install dependencies:

```commandline
pip install -r requirements.txt
```

2.5. Create a `.env` file in the project root and add your Django secret key:

```env
DJANGO_SECRET_KEY=your_secret_key
```

2.6. Apply migrations:

```commandline
python manage.py migrate
```

2.7. Optionally create a superuser:

```commandline
python manage.py createsuperuser
```

### 3. Running the Application

Start the Django development server:

```bash
python manage.py runserver
```

Open in browser:

```text
http://127.0.0.1:8000/
```

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

### 4. Running Tests

Run the test suite with:

```bash
python manage.py test
```

If you use `coverage.py`, you can check coverage with:

```bash
coverage run manage.py test
coverage report
```

---

## Technologies

- **Python**: Core programming language
- **Django**: Main web framework
- **SQLite**: Default database
- **Bootstrap 5**: Layout and UI components
- **HTML/CSS**: Templates and styling
- **python-dotenv**: Environment variable loading

---

Developed by [mishagitcode](https://github.com/mishagitcode)