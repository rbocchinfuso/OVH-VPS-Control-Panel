#!/usr/bin/env bash
# setup.sh — First-time setup helper for the VPS Control Portal
# Run this on the host where you'll deploy the container.
set -euo pipefail

command -v docker >/dev/null 2>&1 || { echo "docker is required"; exit 1; }

echo ""
echo "=== VPS Control Portal — Setup ==="
echo ""

# ── Build the image first so we can use werkzeug from inside it ──
echo "Building Docker image (needed for password hashing)..."
docker compose build --quiet
echo "✓ Image built."
echo ""

# ── Hash helper — runs werkzeug inside the built image ──────────
hash_password() {
    docker run --rm vps-portal-vps-portal python3 -c \
        "from werkzeug.security import generate_password_hash; import sys; print(generate_password_hash(sys.argv[1]))" \
        "$1"
}

# ── Collect values ───────────────────────────────────────────────
echo "This script will create a .env file with hashed passwords."
echo ""

read -rp  "Admin username   [admin]:  " ADMIN_USER
ADMIN_USER="${ADMIN_USER:-admin}"

read -rsp "Admin password:            " ADMIN_PASS; echo
echo "Hashing admin password..."
# Werkzeug hashes contain '$' (e.g. pbkdf2:sha256:600000$salt$hash).
# Escape them as '$$' so Docker Compose writes a literal '$' into the
# container environment instead of treating them as variable references.
ADMIN_HASH=$(hash_password "$ADMIN_PASS" | sed 's/\$/\$\$/g')

read -rp  "Viewer username  [viewer]: " VIEWER_USER
VIEWER_USER="${VIEWER_USER:-viewer}"

read -rsp "Viewer password:           " VIEWER_PASS; echo
echo "Hashing viewer password..."
VIEWER_HASH=$(hash_password "$VIEWER_PASS" | sed 's/\$/\$\$/g')

# ── Generate Flask secret key using openssl (no python needed) ───
FLASK_SECRET=$(openssl rand -hex 32)

# ── Write .env ───────────────────────────────────────────────────
cat > .env <<EOF
# OVH API credentials
OVH_ENDPOINT=${OVH_ENDPOINT:-ovh-ca}
OVH_APPLICATION_KEY=${OVH_APPLICATION_KEY:-}
OVH_APPLICATION_SECRET=${OVH_APPLICATION_SECRET:-}
OVH_CONSUMER_KEY=${OVH_CONSUMER_KEY:-}

# Flask session secret
FLASK_SECRET_KEY=${FLASK_SECRET}

# Users
ADMIN_USERNAME=${ADMIN_USER}
ADMIN_PASSWORD_HASH=${ADMIN_HASH}
VIEWER_USERNAME=${VIEWER_USER}
VIEWER_PASSWORD_HASH=${VIEWER_HASH}
EOF

echo ""
echo "✓ .env written."
echo ""
echo "Next steps:"
echo "  1. Edit .env and fill in OVH_APPLICATION_KEY, OVH_APPLICATION_SECRET, OVH_CONSUMER_KEY"
echo "  2. Ensure your Caddy network exists:  docker network create caddy_net"
echo "  3. Start the portal:                  docker compose up -d"
echo ""
echo "Health check: curl http://localhost:5030/health"
