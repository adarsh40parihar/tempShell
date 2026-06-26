# Docker Setup for TempShell

This project uses Docker Compose with a simplified single-machine setup. The React frontend is built and served as static files from the FastAPI backend.

## Architecture

- **Single Container for Backend**: Runs FastAPI with built-in React frontend
- **Single Container for Database**: MySQL 8.0
- **No Nginx**: Frontend served directly from FastAPI static file mounting

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

### 1. Setup Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` to change any configuration values if needed.

### 2. Build and Start Services

```bash
docker-compose up --build
```

This command will:
- Build the React frontend
- Build the backend Docker image with embedded frontend
- Start MySQL database
- Start the backend service (serving both API and frontend)

### 3. Access the Application

- **Frontend**: http://localhost:8000
- **API**: http://localhost:8000/api/v1/...
- **Health Check**: http://localhost:8000/health

All traffic goes through port 8000 only.

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

## Development Workflow

### Backend Development

Since the backend source code is not mounted as a volume (for production parity), you need to rebuild:

```bash
docker-compose build backend
docker-compose up backend
```

Or for faster iteration, consider mounting the code during development:

Edit `docker-compose.yml` and add under `backend` service:
```yaml
volumes:
  - ./backend:/app
```

Then restart: `docker-compose up --build`

### Frontend Development

To develop the frontend with hot reload:

```bash
# In terminal 1: Start only the database and backend API (without rebuilding frontend)
docker-compose up mysql backend

# In terminal 2: Run frontend development server locally
cd frontend
npm install
npm start
```

Update the frontend's `.env` file to point to the backend:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
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
- In production, use proper secret management tools (AWS Secrets Manager, HashiCorp Vault)

## Troubleshooting

### Port Already in Use

If port 8000 or 3306 are already in use:

1. Find the process using the port:
   ```bash
   lsof -i :8000
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

### Frontend Not Loading

Check that the React build succeeded:
```bash
docker-compose logs backend | grep -i "mount\|static"
```

Verify the static directory exists in the container:
```bash
docker-compose exec backend ls -la /app/static
```

### Build Issues

If the build fails due to npm dependencies:

```bash
# Clear Docker cache and rebuild
docker-compose build --no-cache
```

## Production Deployment on EC2

### 1. SSH into EC2 instance
```bash
ssh ec2-user@your-instance-ip
```

### 2. Install Docker and Docker Compose
```bash
sudo yum install -y docker docker-compose
sudo usermod -a -G docker ec2-user
```

### 3. Clone your repository and setup
```bash
git clone your-repo-url
cd tempShell
cp .env.example .env
```

### 4. Update .env with production values
```bash
nano .env
# Change SECRET_KEY, DB_PASSWORD, CORS_ORIGINS for your domain
```

### 5. Start services
```bash
docker-compose -f docker-compose.yml up -d
```

### 6. Verify it's running
```bash
curl http://localhost:8000
docker-compose ps
```

### 7. (Optional) Setup domain with nginx reverse proxy

Create `/etc/nginx/sites-available/tempshell`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then enable and restart nginx:
```bash
sudo ln -s /etc/nginx/sites-available/tempshell /etc/nginx/sites-enabled/
sudo nginx -s reload
```

### 8. Setup SSL (recommended)
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring

Check container resource usage:
```bash
docker stats
```

View realtime logs:
```bash
docker-compose logs -f --tail=100
```
