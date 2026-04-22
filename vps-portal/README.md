# VPS Control Portal

A self-hosted Flask web portal for managing OVH VPS instances. Supports viewing instance status, taking snapshots, and rebooting — with role-based access control (admin / viewer).

The portal **auto-registers** with your running Caddy container via [caddy-docker-proxy](https://github.com/lucaslorentz/caddy-docker-proxy) labels. No manual Caddyfile editing or `caddy reload` needed — starting the container is enough.

## Features

- **Dashboard** — lists all VPS instances with live status, IPs, CPU/RAM at a glance
- **Detail view** — full instance specs, IP addresses, snapshot status
- **Snapshot** — trigger a snapshot from the UI (admin only)
- **Reboot** — soft-reboot with confirmation dialog (admin only)
- **Role-based access** — `admin` can take actions; `viewer` can only view
- **Secure sessions** — httponly cookies, CSRF-safe forms, password hashing (Werkzeug)
- **Health endpoint** — `GET /health` for container health checks
- **Auto Caddy registration** — labels wire up TLS + routing automatically via caddy-docker-proxy

## Prerequisites

Your Caddy container must be running [lucaslorentz/caddy-docker-proxy](https://github.com/lucaslorentz/caddy-docker-proxy) and must be attached to the shared Docker network (`caddy_net` by default).

If you need to set up caddy-docker-proxy for the first time, see [`caddy-docker-proxy.example.yml`](./caddy-docker-proxy.example.yml).

## Quick Start

### 1. Copy files to your server

```bash
scp -r vps-portal/ user@your-server:~/vps-portal
ssh user@your-server
cd vps-portal
```

### 2. Ensure the shared Docker network exists

This network must be the same one your Caddy container is on:

```bash
docker network create caddy_net   # skip if it already exists
```

### 3. Run the setup script

```bash
chmod +x setup.sh
./setup.sh
```

This prompts for admin and viewer passwords, hashes them, generates a Flask secret key, and writes `.env`.

### 4. Add your OVH credentials to `.env`

```dotenv
OVH_ENDPOINT=ovh-ca
OVH_APPLICATION_KEY=your_key
OVH_APPLICATION_SECRET=your_secret
OVH_CONSUMER_KEY=your_consumer_key
```

### 5. Build and start

```bash
docker compose up -d --build
```

That's it. caddy-docker-proxy detects the container labels, provisions a TLS certificate via ACME, and begins routing `https://vps-control.pscp-css.support` to the Flask app. No Caddy reload required.

Verify:

```bash
docker compose logs -f vps-portal
curl -sf https://vps-control.pscp-css.support/health && echo OK
```

## How auto-registration works

`docker-compose.yml` attaches the container to `caddy_net` and sets these labels:

```yaml
labels:
  caddy: vps-control.pscp-css.support          # virtual host
  caddy.reverse_proxy: "{{upstreams 5000}}"    # proxy to Flask
  caddy.header.Strict-Transport-Security: '"max-age=31536000; includeSubDomains; preload"'
  caddy.header.X-Content-Type-Options: '"nosniff"'
  caddy.header.X-Frame-Options: '"DENY"'
  caddy.header.Referrer-Policy: '"strict-origin-when-cross-origin"'
```

caddy-docker-proxy watches the Docker socket and translates these labels into a live Caddyfile block. When the container stops, the route is removed automatically.

## Changing the domain

Edit the `caddy:` label in `docker-compose.yml`:

```yaml
caddy: my-other-domain.example.com
```

Then recreate the container:

```bash
docker compose up -d --force-recreate
```

## Adding / changing users

Generate a new password hash:

```bash
docker run --rm python:3.12-slim python3 -c \
  "from werkzeug.security import generate_password_hash; print(generate_password_hash('newpassword'))"
```

Paste the output into `ADMIN_PASSWORD_HASH` or `VIEWER_PASSWORD_HASH` in `.env`, then restart:

```bash
docker compose restart vps-portal
```

## Roles

| Action               | admin | viewer |
|----------------------|-------|--------|
| View instance list   | ✓     | ✓      |
| View instance detail | ✓     | ✓      |
| Take snapshot        | ✓     | ✗      |
| Reboot instance      | ✓     | ✗      |

## Directory layout

```
vps-portal/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── auth.py                  # Login, logout, role decorators
│   ├── vps.py                   # VPS routes (list, detail, reboot, snapshot)
│   ├── main.py                  # Root redirect + health endpoint
│   ├── ovh_client.py            # OVH API wrapper
│   ├── static/
│   │   ├── css/main.css
│   │   └── js/main.js
│   └── templates/
│       ├── base.html
│       ├── login.html
│       └── vps/
│           ├── index.html
│           └── detail.html
├── config.py                    # Config from environment variables
├── wsgi.py                      # Gunicorn entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml           # Includes caddy-docker-proxy labels
├── caddy-docker-proxy.example.yml  # Reference: set up Caddy itself
├── setup.sh                     # First-time setup helper
└── .env.example
```

## Environment variables

| Variable                 | Required | Default   | Description                          |
|--------------------------|----------|-----------|--------------------------------------|
| `OVH_ENDPOINT`           | No       | `ovh-ca`  | OVH API endpoint region              |
| `OVH_APPLICATION_KEY`    | Yes      |           | OVH application key                  |
| `OVH_APPLICATION_SECRET` | Yes      |           | OVH application secret               |
| `OVH_CONSUMER_KEY`       | Yes      |           | OVH consumer key                     |
| `FLASK_SECRET_KEY`       | Yes      |           | Flask session encryption key         |
| `ADMIN_USERNAME`         | No       | `admin`   | Admin account username               |
| `ADMIN_PASSWORD_HASH`    | Yes      |           | Werkzeug-hashed admin password       |
| `VIEWER_USERNAME`        | No       | `viewer`  | Viewer account username              |
| `VIEWER_PASSWORD_HASH`   | Yes      |           | Werkzeug-hashed viewer password      |

## Troubleshooting

**Portal not reachable after `docker compose up`**

- Confirm the container is on `caddy_net`: `docker inspect vps-portal | grep -A5 Networks`
- Confirm caddy-docker-proxy is running and on the same network: `docker ps | grep caddy`
- Check caddy-docker-proxy picked up the labels: `docker logs caddy 2>&1 | tail -30`
- Confirm DNS for `vps-control.pscp-css.support` points to your server's public IP

**TLS certificate not issued**

- Port 80 and 443 must be reachable from the internet for ACME HTTP-01 challenge
- Check `docker logs caddy` for ACME errors
