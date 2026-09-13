# Cinema

## Description

Cinema Project is a web application built with Django that lets users
browse a curated catalog of movies, TV series, and animated films, leave
reviews and ratings, and manage their personal favorites lists.

The project focuses on usability and a responsive design, making it
comfortable to use on both desktop and mobile devices. Further features
and UX improvements are planned for future releases.

## Features

- Browse a catalog of movies and TV series with detailed information
- Reviews and ratings: authenticated users can leave comments and rate titles
- Personal lists: create and edit a favorites list (beta)
- Responsive design: interface optimized for virtually any device

## Tech Stack

- Django
- PostgreSQL
- Redis (caching)
- Docker / Docker Compose
- Bootstrap

## Getting Started

The project is fully containerized, so the only requirement on your machine
is [Docker](https://www.docker.com/products/docker-desktop/) with Docker
Compose.

### 1. Clone the repository

```bash
git clone https://github.com/Phantom-AL/Cinema_Project.git
```

### 2. Set up environment variables

Create a `.env` file, using
`.env.example` as a reference. Fill in your own values:

```
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
TMDB_API_KEY=your_tmdb_api_key
OMDB_API_KEY=your_omdb_api_key
```

To generate a new `SECRET_KEY`, you can run:

```bash
docker compose run --rm web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

You'll need your own free API keys from [TMDB](https://www.themoviedb.org/settings/api)
and [OMDB](https://www.omdbapi.com/apikey.aspx) to populate the catalog.

### 3. Build and start the containers

```bash
docker compose up --build -d
```

This starts three services: `web` (Django), `db` (PostgreSQL), and `redis`
(caching).

### 4. Apply database migrations


```bash
docker compose exec web python manage.py migrate
```

### 6. Open the app

Visit **http://localhost:8000** in your browser.

## Screenshots

![image](https://github.com/user-attachments/assets/7e6dfa5f-7ff5-4a92-b1b9-5e89e286019f)

![image](https://github.com/user-attachments/assets/116d5596-965c-4602-b5af-7621b4aeabfb)

![image](https://github.com/user-attachments/assets/99370364-6d51-46aa-8620-01b8740a39cc)
