# Attanasio-DB-system

This project contains a MySQL schema and a Flask application. The application exposes REST endpoints for each table and requires authentication.

## Requirements

- Docker with Compose support

## Usage

Build and start the environment:

```bash
docker compose up --build
```

Open [http://localhost:5000](http://localhost:5000) and log in with **admin/admin123**.

Useful endpoints (all require login):

- `/specialists` – gestione tabella Specialista
- `/users` – gestione tabella Utente
- `/afferenze` – gestione Afferenza
- `/sedi` – gestione Sede
- `/provvedimenti` – gestione Provvedimento
- `/loginusers` – gestione utenti di login

To stop the services:

```bash
docker compose down
```
