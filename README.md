# Attanasio-DB-system

This project contains a MySQL schema and a small Flask application. The
application exposes a couple of endpoints and connects to the MySQL database.
Both services are orchestrated via Docker Compose.

## Requirements

- Docker with Compose support

## Usage

Build and start the environment:

```bash
docker compose up --build
```

The database will be initialized using `DockerConfig/DBScript.sql`. The
Flask server will be available on [http://localhost:5000](http://localhost:5000).

Useful endpoints:

- `/health` – simple health check
- `/specialists` – returns the list of specialists in the database

To stop the services:

```bash
docker compose down
```
