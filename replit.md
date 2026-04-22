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

### Deployment
1. Copy `vps-portal/` to the target server
2. Run `./setup.sh` to generate `.env` with hashed passwords
3. Add OVH credentials to `.env`
4. `docker compose up -d --build`
5. Add `Caddyfile.snippet` to Caddy config and reload
