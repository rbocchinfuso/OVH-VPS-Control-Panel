# VPS Control Portal

A self-hosted Flask web portal for managing OVH VPS instances. Supports viewing instance status, taking snapshots, and rebooting — with role-based access control (admin / viewer).

## Features

- **Dashboard** — lists all VPS instances with live status, IPs, CPU/RAM at a glance
- **Detail view** — full instance specs, IP addresses, snapshot status
- **Snapshot** — trigger a snapshot from the UI (admin only)
- **Reboot** — soft-reboot with confirmation dialog (admin only)
- **Role-based access** — `admin` can take actions; `viewer` can only view
- **Secure sessions** — httponly cookies, CSRF-safe forms, password hashing (Werkzeug)
- **Health endpoint** — `GET /health` for container health checks and reverse proxy probes

## Quick Start

### 1. Clone / copy files

```bash
# copy the vps-portal/ directory to your server
scp -r vps-portal/ user@your-server:~/vps-portal
cd vps-portal
```

### 2. Run the setup script

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Prompt for admin and viewer usernames/passwords
- Hash passwords with Werkzeug (bcrypt-style PBKDF2)
- Generate a random Flask secret key
- Write a `.env` file

### 3. Fill in OVH credentials in `.env`

```dotenv
OVH_ENDPOINT=ovh-ca
OVH_APPLICATION_KEY=a629dcc732f6056b
OVH_APPLICATION_SECRET=<your_secret>
OVH_CONSUMER_KEY=<your_consumer_key>
```

### 4. Create the Docker network (if not already present)

```bash
docker network create caddy_net
```

### 5. Build and start

```bash
docker compose up -d --build
docker compose logs -f
```

### 6. Add Caddy config

Copy the contents of `Caddyfile.snippet` into your Caddy configuration and reload:

```bash
caddy reload --config /etc/caddy/Caddyfile
```

The portal will be available at `https://vps-control.pscp-css.support`.

## Adding / changing users

Passwords are stored as hashes in `.env`. To generate a new hash:

```bash
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('newpassword'))"
```

Copy the output into `ADMIN_PASSWORD_HASH` or `VIEWER_PASSWORD_HASH` in `.env`, then restart:

```bash
docker compose restart vps-portal
```

## Roles

| Action              | admin | viewer |
|---------------------|-------|--------|
| View instance list  | ✓     | ✓      |
| View instance detail| ✓     | ✓      |
| Take snapshot       | ✓     | ✗      |
| Reboot instance     | ✓     | ✗      |

## Directory layout

```
vps-portal/
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── auth.py            # Login, logout, decorators
│   ├── vps.py             # VPS routes (list, detail, reboot, snapshot)
│   ├── main.py            # Root redirect + health endpoint
│   ├── ovh_client.py      # OVH API wrapper
│   ├── static/
│   │   ├── css/main.css
│   │   └── js/main.js
│   └── templates/
│       ├── base.html
│       ├── login.html
│       └── vps/
│           ├── index.html
│           └── detail.html
├── config.py              # Config from environment variables
├── wsgi.py                # Gunicorn entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Caddyfile.snippet      # Paste into your Caddy config
├── setup.sh               # First-time setup helper
└── .env.example
```

## Environment variables

| Variable               | Required | Default   | Description                            |
|------------------------|----------|-----------|----------------------------------------|
| `OVH_ENDPOINT`         | No       | `ovh-ca`  | OVH API endpoint region                |
| `OVH_APPLICATION_KEY`  | Yes      |           | OVH application key                    |
| `OVH_APPLICATION_SECRET` | Yes    |           | OVH application secret                 |
| `OVH_CONSUMER_KEY`     | Yes      |           | OVH consumer key                       |
| `FLASK_SECRET_KEY`     | Yes      |           | Flask session encryption key           |
| `ADMIN_USERNAME`       | No       | `admin`   | Admin account username                 |
| `ADMIN_PASSWORD_HASH`  | Yes      |           | Werkzeug-hashed admin password         |
| `VIEWER_USERNAME`      | No       | `viewer`  | Viewer account username                |
| `VIEWER_PASSWORD_HASH` | Yes      |           | Werkzeug-hashed viewer password        |
