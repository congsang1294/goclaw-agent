# OPERATIONS GUIDE — Gà Trống Tre AI Team Framework

> **File:** `OPERATIONS.md`
> **Version:** 1.0.0
> **Applies to:** v1.0.0-framework

---

## 1. Service Management

### 1.1 Status Check

```bash
# Quick health check
docker ps --format 'table {{.Names}}\t{{.Status}}'
curl -s -o /dev/null -w "Gateway: HTTP %{http_code}\n" http://localhost:18790/health

# Detailed
docker logs goclaw-bai-13-goclaw-1 --tail 20
```

### 1.2 Start / Stop / Restart

```bash
# Start all services
cd /opt/goclaw
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d

# Restart GoClaw (after config/skill changes)
docker restart goclaw-bai-13-goclaw-1

# Full restart
docker compose -f docker-compose.yml -f docker-compose.postgres.yml restart

# Stop
docker compose -f docker-compose.yml -f docker-compose.postgres.yml down
```

---

## 2. Backup

### 2.1 Database Backup

```bash
# Create backup
docker exec goclaw-bai-13-postgres-1 pg_dump -U goclaw -d goclaw \
  --no-owner --no-acl \
  > /root/backups/goclaw_$(date +%Y%m%d_%H%M%S).sql

# Keep last 7 days
find /root/backups -name "goclaw_*.sql" -mtime +7 -delete
```

### 2.2 Workspace Backup

```bash
# Backup workspace volumes
docker run --rm -v goclaw-bai-13_goclaw-workspace:/workspace:ro \
  -v /root/backups:/backup \
  alpine tar czf /backup/workspace_$(date +%Y%m%d).tar.gz -C /workspace .
```

### 2.3 Config Backup

```bash
cp /opt/goclaw/.env /root/backups/env_$(date +%Y%m%d).bak
```

### 2.4 Automation (Crontab)

```bash
# Daily at 2 AM
0 2 * * * /opt/goclaw/scripts/backup.sh

# backup.sh content:
#   #!/bin/bash
#   BACKUP_DIR=/root/backups
#   mkdir -p $BACKUP_DIR
#   docker exec goclaw-bai-13-postgres-1 pg_dump -U goclaw -d goclaw > $BACKUP_DIR/db_$(date +%Y%m%d).sql
#   find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
```

---

## 3. Restore

### 3.1 Database Restore

```bash
# Restore from backup
cat /root/backups/goclaw_20260709.sql | \
  docker exec -i goclaw-bai-13-postgres-1 psql -U goclaw -d goclaw

# Then restart GoClaw
docker restart goclaw-bai-13-goclaw-1
```

### 3.2 Full Restore (from scratch)

```bash
# 1. Stop services
cd /opt/goclaw
docker compose down

# 2. Restore database
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d postgres
sleep 5
cat /root/backups/goclaw_latest.sql | docker exec -i goclaw-bai-13-postgres-1 psql -U goclaw -d goclaw

# 3. Restore workspace
docker run --rm -v goclaw-bai-13_goclaw-workspace:/workspace \
  -v /root/backups:/backup \
  alpine tar xzf /backup/workspace_latest.tar.gz -C /workspace

# 4. Start GoClaw
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d
```

---

## 4. Update

### 4.1 Framework Update

```bash
# On VPS
cd /opt/goclaw-agent
git pull origin main

# Sync new context files (see DEPLOYMENT.md section 3.5)

# Restart to pick up changes
docker restart goclaw-bai-13-goclaw-1
```

### 4.2 GoClaw Update

```bash
cd /opt/goclaw
git pull origin main
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d --build
```

---

## 5. Monitoring

### 5.1 Health Endpoints

```http
GET /health → HTTP 200 {"status": "ok"}
GET /v1/agents → List agents
GET /v1/agents/{id} → Agent details
```

### 5.2 Key Metrics

| Metric | How to Check | Alert If |
|--------|-------------|----------|
| GoClaw status | `docker ps` | Not healthy |
| Postgres status | `docker ps` | Not running |
| Telegram bot | `docker logs \| grep "telegram bot connected"` | Not connected |
| Agent count | `SELECT count(*) FROM agents` | Dropped below 4 |
| Session count | `SELECT count(*) FROM sessions` | > 100 (leak) |
| Failed tasks | `SELECT count(*) FROM team_tasks WHERE status='failed'` | > 5/day |
| Disk usage | `df -h` | > 80% |
| Memory | `free -m` | > 80% of total |

### 5.3 Logs

```bash
# GoClaw application logs
docker logs goclaw-bai-13-goclaw-1 --tail 100
docker logs goclaw-bai-13-goclaw-1 -f  # Follow

# Filter by agent
docker logs goclaw-bai-13-goclaw-1 2>&1 | grep "agent=ga-trong-tre"
docker logs goclaw-bai-13-goclaw-1 2>&1 | grep "agent=viet-bai-fb"

# Filter by event
docker logs goclaw-bai-13-goclaw-1 2>&1 | grep "tool call"
docker logs goclaw-bai-13-goclaw-1 2>&1 | grep "telegram"
docker logs goclaw-bai-13-goclaw-1 2>&1 | grep "error\|Error\|panic"

# Postgres logs
docker logs goclaw-bai-13-postgres-1 --tail 50
```

---

## 6. Debugging

### 6.1 Common Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Agent not found | Agent missing in DB | `POST /v1/agents` to create |
| Team tasks fail | Team not created | Create via `teams.create` RPC |
| Worker not responding | No context files | Copy AGENTS.md + SKILL.md to workspace |
| Telegram not responding | Token invalid | Re-generate token, update channel instance |
| "No provider" | Provider not enabled | Check `llm_providers` table |
| Sandbox error | Sandbox misconfig | Set `sandbox.mode=off` in config |
| `no workstation bound to agent` | Thiếu row trong `agent_workstation_links` (agent chưa được link ws) | `./scripts/bind-workstation.sh` — xem [Workstation Setup](docs/WORKSTATION_SETUP.md) |
| `binary 'python3' not allowed` | Allowlist workstation thiếu binary skill cần | `./scripts/bind-workstation.sh` (mở allowlist) hoặc `POST /v1/workstations/{id}/permissions` |

### 6.2 Agent Debug Commands

```bash
# Check agent config
docker exec goclaw-bai-13-postgres-1 psql -U goclaw -d goclaw \
  -c "SELECT agent_key, model, provider, tools_config FROM agents WHERE agent_key='ga-trong-tre';"

# Check team
docker exec goclaw-bai-13-postgres-1 psql -U goclaw -d goclaw \
  -c "SELECT tm.agent_id, a.agent_key, tm.role FROM agent_team_members tm JOIN agents a ON tm.agent_id = a.id;"

# Check recent runs
docker logs goclaw-bai-13-goclaw-1 2>&1 | grep "v3.run.completed" | tail -10

# Check team tasks
docker exec goclaw-bai-13-postgres-1 psql -U goclaw -d goclaw \
  -c "SELECT subject, status, owner_agent_key FROM team_tasks ORDER BY created_at DESC LIMIT 10;"
```

### 6.3 Workspace Inspection

```bash
# Check context files
docker exec goclaw-bai-13-goclaw-1 ls -la /app/workspace/ga-trong-tre/context-files/

# Check skill files
docker exec goclaw-bai-13-goclaw-1 ls -la /app/workspace/viet-bai-fb/

# View a file
docker exec goclaw-bai-13-goclaw-1 cat /app/workspace/ga-trong-tre/context-files/AGENTS.md
```

---

## 7. Recovery Procedures

### 7.1 GoClaw Crash

```bash
# Auto-recovery: Docker restart policy (unless-stopped)
# Manual:
docker restart goclaw-bai-13-goclaw-1

# If container won't start:
docker logs goclaw-bai-13-goclaw-1 --tail 50
# Fix the issue, then restart
```

### 7.2 PostgreSQL Crash

```bash
docker restart goclaw-bai-13-postgres-1
# GoClaw will auto-reconnect when Postgres is back
```

### 7.3 Telegram Disconnect

Telegram bot auto-reconnects. Monitor:
```bash
docker logs goclaw-bai-13-goclaw-1 2>&1 | grep "telegram"
# Expected: "telegram bot connected" for each bot
```

### 7.4 Full Recovery

See [Restore](#3-restore) section.

---

## 8. Scheduler / Cron

### 8.1 GoClaw Cron Jobs

```bash
# List cron jobs
docker exec goclaw-bai-13-goclaw-1 \
  curl -s http://localhost:18790/v1/cron \
  -H "Authorization: Bearer $GATEWAY_TOKEN"

# Heartbeat runs via GoClaw's internal heartbeat mechanism
# Config in HEARTBEAT.md
```

### 8.2 VPS Cron (Framework)

```bash
# Add to /etc/crontab:
# Backup database daily at 2 AM
0 2 * * * root /opt/goclaw-agent/scripts/backup.sh

# Health check every 5 minutes
*/5 * * * * root curl -s -o /dev/null http://localhost:18790/health || docker restart goclaw-bai-13-goclaw-1
```

---

## 9. Log Locations

| Log | Location | Retention |
|-----|----------|-----------|
| GoClaw application | `docker logs goclaw-bai-13-goclaw-1` | Docker default |
| PostgreSQL | `docker logs goclaw-bai-13-postgres-1` | Docker default |
| Task history (framework) | `goclaw-agent/memory/long-term/task_history.log` | Per-session |
| Session state (framework) | `goclaw-agent/memory/sessions/session_*.json` | Per-session |
| GoClaw traces | `/app/data/traces/` | Configurable |
| GoClaw config | `/app/data/config.json` | Permanent |

---

## 10. Security Notes

- **Never expose `GOCLAW_GATEWAY_TOKEN` publicly**
- **Never commit `.env` files to git**
- **Telegram tokens are stored in channel_instances DB table**
- **LLM API keys are stored in `llm_providers` DB table**
- **Restrict VPS SSH to key-based auth only**
- **Firewall: only ports 22 (SSH), 18790 (GoClaw API) open**
