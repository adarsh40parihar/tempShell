# Docker Setup for TempShell

This project is now containerized using Docker Compose. Kubernetes support has been removed in favor of simpler Docker-based deployment.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

### 1. Setup Environment Variables

Copy the example environment file and customize as needed:

```bash
cp .env.example .env
```

Edit `.env` to change any configuration values if needed.

### 2. Build and Start Services

```bash
docker-compose up --build
```

This command will:
- Build the backend and frontend images
- Start MySQL database
- Start the backend service
- Start the frontend service

Services will be available at:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **MySQL**: localhost:3306

### 3. Verify Services are Running

```bash
docker-compose ps
```

You should see three running containers:
- `tempshell-mysql`
- `tempshell-backend`
- `tempshell-frontend`

## Common Commands

### View Logs

View logs from all services:
```bash
docker-compose logs -f
```

View logs from a specific service:
```bash
docker-compose logs -f backend
```

### Stop Services

```bash
docker-compose down
```

To also remove volumes (database data):
```bash
docker-compose down -v
```

### Rebuild Images

```bash
docker-compose build --no-cache
```

### Access Service Shell

MySQL:
```bash
docker-compose exec mysql mysql -uroot -p -e "use tempshell;"
```

Backend:
```bash
docker-compose exec backend bash
```

Frontend:
```bash
docker-compose exec frontend sh
```

## Development Workflow

### Backend Development

The backend directory is mounted as a volume. Changes to Python code will be reflected immediately (if using auto-reload configuration).

To restart the backend service:
```bash
docker-compose restart backend
```

### Frontend Development

For development, you might want to run the frontend locally instead of in Docker:

```bash
# In terminal 1: Start Docker services (without frontend)
docker-compose down
docker-compose up --build -d mysql backend

# In terminal 2: Run frontend locally
cd frontend
npm install
npm start
```

## Environment Variables

All configuration is managed through the `.env` file. Key variables:

- `DB_PASSWORD`: MySQL user password
- `SECRET_KEY`: JWT secret key (generate with: `openssl rand -hex 32`)
- `CORS_ORIGINS`: Allowed origins for CORS (JSON array)
- `RATE_LIMIT_PER_MINUTE`: API rate limit

## Security Notes

- Change `SECRET_KEY` in production using: `openssl rand -hex 32`
- Change `DB_PASSWORD` to a strong password
- Do not commit `.env` file with real credentials
- The `.env` file should only exist on your local machine and servers

## Troubleshooting

### Port Already in Use

If ports 80, 8000, or 3306 are already in use:

1. Find the process using the port:
   ```bash
   lsof -i :80
   ```

2. Either kill the process or modify the port mappings in `docker-compose.yml`

### Database Connection Issues

Check if MySQL is healthy:
```bash
docker-compose ps mysql
```

View MySQL logs:
```bash
docker-compose logs mysql
```

Wait a bit longer for MySQL to initialize on first run.

### Backend Cannot Connect to Database

Ensure MySQL is fully started and healthy before backend starts. The `depends_on` condition ensures this, but you can manually restart:

```bash
docker-compose restart mysql backend
```

## Deploying to Production

For production deployment:

1. Use a proper `.env` file with secure credentials
2. Use proper secret management (AWS Secrets Manager, HashiCorp Vault, etc.)
3. Consider using Docker Swarm or Kubernetes for orchestration
4. Set resource limits appropriately
5. Use health checks to ensure service availability
6. Implement proper backup strategy for MySQL volumes
7. Use a reverse proxy (nginx, Traefik) in front of the containers
