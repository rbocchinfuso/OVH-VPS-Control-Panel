# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.

## VPS Control Portal

A standalone Python/Flask container lives in `vps-portal/`. It is **not** part of the pnpm workspace — it is a self-contained Docker app meant to be deployed separately behind a Caddy reverse proxy at `vps-control.pscp-css.support`.

### Stack
- **Python 3.12 / Flask 3** + Gunicorn
- **OVH Python SDK** (`ovh==1.2.0`)
- **Auth**: username + password (Werkzeug PBKDF2 hashes stored in `.env`)
- **Roles**: `admin` (view + snapshot + reboot), `viewer` (view only)
- **Docker + docker-compose** with Caddy network integration

### Caddy auto-registration
The container uses `caddy-docker-proxy` labels. When it starts it self-registers with the running Caddy container — no manual Caddyfile editing or reload needed. See `caddy-docker-proxy.example.yml` for setting up Caddy itself.

### Deployment
1. Copy `vps-portal/` to the target server
2. Ensure `docker network create caddy_net` exists (same network Caddy is on)
3. Run `./setup.sh` to generate `.env` with hashed passwords
4. Add OVH credentials to `.env`
5. `docker compose up -d --build` — Caddy picks up the labels automatically
