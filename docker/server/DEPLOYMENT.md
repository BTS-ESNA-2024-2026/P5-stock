# Production Deployment Guide

## Prerequisites
- Docker & Docker Compose installed
- PostgreSQL credentials configured
- SSL certificates (optional, for HTTPS)

## Quick Start

### 1. Prepare Environment
```bash
cp .env.example .env
# Edit .env with your production values
nano .env
```

### 2. Generate SSL Certificates (Optional)
For self-signed certificates in development:
```bash
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -nodes \
  -out ssl/cert.pem -keyout ssl/key.pem -days 365
```

For production with Let's Encrypt:
```bash
certbot certonly --standalone -d yourdomain.com
# Copy certificates to ssl/ directory
```

### 3. Start Services
```bash
docker compose up -d
```

### 4. Verify Services
```bash
# Check all services
docker compose ps

# View logs
docker compose logs -f

# Health checks
curl http://localhost:80/health  # HTTP
curl https://localhost:443/health  # HTTPS
```

## Architecture

```
┌─────────────────┐
│   Client        │
└────────┬────────┘
         │
    ┌────▼────────┐
    │  Nginx      │
    │  (443/80)   │
    └────┬────────┘
         │
    ┌────┴──────┬────────┐
    │            │        │
┌───▼──┐  ┌─────▼──┐  ┌──▼──────┐
│React │  │ Flask  │  │Postgres  │
│(SPA) │  │(API)   │  │(DB)      │
└──────┘  └────────┘  └──────────┘
```

## Configuration Details

### Frontend (React + Vite)
- **Build**: Multi-stage Docker build
- **Serve**: Alpine nginx
- **Port**: 80/443 (via Nginx reverse proxy)

### Backend (Flask)
- **Server**: Gunicorn with 4 workers
- **Image**: Python 3.14 Alpine
- **Port**: 8000 (internal only, proxied by Nginx)

### Database (PostgreSQL)
- **Image**: PostgreSQL 17 Alpine
- **Volume**: `postgres_data` (persistent)
- **Port**: 5432 (accessible within network only)

### Nginx
- **Gzip Compression**: Enabled
- **Rate Limiting**: 
  - API: 10 req/s
  - General: 30 req/s
- **Load Balancing**: Least connections
- **Security Headers**: HSTS, X-Frame-Options, CSP compatible

## Maintenance

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

### Database Backup
```bash
docker exec p5_postgres pg_dump -U postgres p5_stock > backup.sql
```

### Database Restore
```bash
docker exec -i p5_postgres psql -U postgres p5_stock < backup.sql
```

### Restart Services
```bash
# Single service
docker compose restart backend

# All services
docker compose restart
```

### Update Images
```bash
docker compose pull
docker compose up -d
```

## Security Best Practices (Implemented)

✅ Non-root user in containers  
✅ Read-only volumes where possible  
✅ Health checks for all services  
✅ Rate limiting on API endpoints  
✅ GZIP compression enabled  
✅ Security headers (HSTS, X-Frame-Options, etc.)  
✅ No new privileges security option  
✅ PostgreSQL in internal network only  

## Performance Tuning

### Worker Scaling
Edit `Dockerfile.backend` to adjust Gunicorn workers:
```dockerfile
CMD ["gunicorn", "--workers", "8", ...]  # Increase for more CPU cores
```

### Database Optimization
- Consider connection pooling (PgBouncer)
- Enable query logging for slow queries
- Regular VACUUM and ANALYZE

### Nginx Caching
Add to nginx.conf for static assets:
```nginx
expires 30d;
add_header Cache-Control "public, immutable";
```

## Troubleshooting

### Services not starting
```bash
docker compose logs -f
docker compose ps
```

### Database connection errors
```bash
docker compose exec backend curl postgres:5432
docker compose logs postgres
```

### Nginx 502 errors
- Check backend health: `docker compose logs backend`
- Verify network: `docker network inspect p5_network`

### Out of disk space
```bash
docker system prune -a --volumes  # Warning: removes unused images/volumes
```

## Scaling Considerations

For production:
- Use container orchestration (Kubernetes, Docker Swarm)
- Implement database replication/backup strategy
- Use managed database service (AWS RDS, etc.)
- Add Redis for caching
- Use CDN for static assets
- Implement centralized logging (ELK, Datadog)
