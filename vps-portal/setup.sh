#!/usr/bin/env bash
# setup.sh — First-time setup helper for the VPS Control Portal
# Run this on the host where you'll deploy the container.
set -euo pipefail

command -v python3 >/dev/null 2>&1 || { echo "python3 is required"; exit 1; }
command -v docker  >/dev/null 2>&1 || { echo "docker is required"; exit 1; }

echo ""
echo "=== VPS Control Portal — Setup ==="
echo ""

# ── Hash helper ─────────────────────────────────────────────────
hash_password() {
    python3 -c "from werkzeug.security import generate_password_hash; import sys; print(generate_password_hash(sys.argv[1]))" "$1"
}

# ── Collect values ───────────────────────────────────────────────
echo "This script will create a .env file with hashed passwords."
echo "Your OVH credentials should already be in .env or set as environment variables."
echo ""

read -rp "Admin username   [admin]:   " ADMIN_USER
ADMIN_USER="${ADMIN_USER:-admin}"

read -rsp "Admin password:            " ADMIN_PASS; echo
ADMIN_HASH=$(hash_password "$ADMIN_PASS")

read -rp "Viewer username  [viewer]:  " VIEWER_USER
VIEWER_USER="${VIEWER_USER:-viewer}"

read -rsp "Viewer password:           " VIEWER_PASS; echo
VIEWER_HASH=$(hash_password "$VIEWER_PASS")

# ── Write .env ───────────────────────────────────────────────────
cat > .env <<EOF
# OVH API credentials
OVH_ENDPOINT=${OVH_ENDPOINT:-ovh-ca}
OVH_APPLICATION_KEY=${OVH_APPLICATION_KEY:-}
OVH_APPLICATION_SECRET=${OVH_APPLICATION_SECRET:-}
OVH_CONSUMER_KEY=${OVH_CONSUMER_KEY:-}

# Flask session secret
FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Users
ADMIN_USERNAME=${ADMIN_USER}
ADMIN_PASSWORD_HASH=${ADMIN_HASH}
VIEWER_USERNAME=${VIEWER_USER}
VIEWER_PASSWORD_HASH=${VIEWER_HASH}
EOF

echo ""
echo "✓ .env file written."
echo ""
echo "Next steps:"
echo "  1. Edit .env and fill in your OVH_APPLICATION_KEY, OVH_APPLICATION_SECRET, OVH_CONSUMER_KEY"
echo "  2. Ensure your Caddy network exists:  docker network create caddy_net"
echo "  3. Start the container:               docker compose up -d --build"
echo "  4. Copy Caddyfile.snippet into your Caddy config and reload Caddy"
echo ""
echo "Health check: curl http://localhost:5000/health"
