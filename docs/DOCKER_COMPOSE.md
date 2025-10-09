# Docker Setup Guide

This guide explains how to run the EPR MCP Server using Docker, either with
Docker Compose (recommended) or directly with Docker commands.

## Direct Docker Usage

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/xbcsmith/epr-mcp-python.git
cd epr-mcp-python

# Build the Docker image
docker build -t epr-mcp-server .

# Run the container
docker run -d \
  --name epr-mcp-server \
  -p 8000:8000 \
  -e EPR_URL=http://host.docker.internal:8042 \
  -e EPR_TOKEN=your-epr-api-token \
  -e EPR_DEBUG=false \
  epr-mcp-server

# Check container status
docker ps

# View logs
docker logs -f epr-mcp-server

# Test the server
curl http://localhost:8000/health
```

### Docker Run Variations

#### Development Mode (Interactive)

```bash
# Run in foreground with interactive terminal
docker run -it --rm \
  --name epr-mcp-server \
  -p 8000:8000 \
  -e EPR_URL=http://host.docker.internal:8042 \
  -e EPR_TOKEN=your-epr-api-token \
  -e EPR_DEBUG=true \
  epr-mcp-server
```

#### Production Mode (Background)

```bash
# Run as daemon with restart policy
docker run -d \
  --name epr-mcp-server \
  --restart unless-stopped \
  -p 8000:8000 \
  -e EPR_URL=http://host.docker.internal:8042 \
  -e EPR_TOKEN=your-epr-api-token \
  -e EPR_DEBUG=false \
  epr-mcp-server
```

#### With Volume Mounts

```bash
# Mount logs directory for persistent logging
docker run -d \
  --name epr-mcp-server \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.env:/app/.env:ro \
  -e EPR_URL=http://host.docker.internal:8042 \
  -e EPR_TOKEN=your-epr-api-token \
  epr-mcp-server
```

#### Custom Network

```bash
# Create a custom network
docker network create epr-network

# Run container in custom network
docker run -d \
  --name epr-mcp-server \
  --network epr-network \
  -p 8000:8000 \
  -e EPR_URL=http://epr-api-server:8042 \
  -e EPR_TOKEN=your-epr-api-token \
  epr-mcp-server
```

### Container Management

#### View Container Status

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View container details
docker inspect epr-mcp-server
```

#### Container Logs

```bash
# View recent logs
docker logs epr-mcp-server

# Follow logs in real-time
docker logs -f epr-mcp-server

# View logs with timestamps
docker logs -t epr-mcp-server

# View last 100 lines
docker logs --tail 100 epr-mcp-server
```

#### Stop and Clean Up

```bash
# Stop the container
docker stop epr-mcp-server

# Remove the container
docker rm epr-mcp-server

# Remove the image
docker rmi epr-mcp-server

# Clean up everything (containers, networks, images)
docker system prune -a
```

### Environment Variables

| Variable    | Description                  | Default                            | Required |
| ----------- | ---------------------------- | ---------------------------------- | -------- |
| `EPR_URL`   | EPR API server URL           | `http://host.docker.internal:8042` | Yes      |
| `EPR_TOKEN` | EPR API authentication token | -                                  | Yes      |
| `EPR_DEBUG` | Enable debug logging         | `false`                            | No       |
| `MCP_HOST`  | MCP server bind address      | `0.0.0.0`                          | No       |
| `MCP_PORT`  | MCP server port              | `8000`                             | No       |

### Networking Considerations

When running with Docker, pay attention to networking:

- **EPR server on host machine**: Use `http://host.docker.internal:8042`
- **EPR server in another container**: Use `http://container-name:8042`
- **EPR server on remote machine**: Use `http://remote-host:8042`

### Troubleshooting Direct Docker

#### Container Won't Start

```bash
# Check if port is already in use
lsof -i :8000

# Run with different port
docker run -p 8001:8000 ...

# Check container logs for errors
docker logs epr-mcp-server
```

#### Connection Issues

```bash
# Test network connectivity from container
docker exec -it epr-mcp-server curl http://host.docker.internal:8042/health

# Check DNS resolution
docker exec -it epr-mcp-server nslookup host.docker.internal
```

#### Image Build Issues

```bash
# Build with no cache
docker build --no-cache -t epr-mcp-server .

# Build with verbose output
docker build --progress=plain -t epr-mcp-server .
```

## Docker Compose (Recommended)

### Quick Start

#### 1. Basic Setup

```bash
# Clone the repository
git clone https://github.com/xbcsmith/epr-mcp-python.git
cd epr-mcp-python

# Copy environment template
cp .env.example .env

# Edit the environment file with your EPR configuration
nano .env
```

### 2. Configure Environment

Edit `.env` file:

```bash
EPR_URL=http://your-epr-server:8042
EPR_TOKEN=your-actual-api-token
EPR_DEBUG=false
```

### 3. Run the Server

```bash
# Build and start the server
docker-compose up -d

# View logs
docker-compose logs -f epr-mcp-server

# Check health
curl http://localhost:8000/health
```

## Service Profiles

The Docker Compose configuration includes multiple service profiles for
different deployment scenarios:

### Default Profile (Core Server)

```bash
docker-compose up -d
```

- **epr-mcp-server**: Core MCP server on port 8000

### Production Profile (with Nginx)

```bash
docker-compose --profile production up -d
```

- **epr-mcp-server**: Core MCP server
- **nginx**: Reverse proxy with rate limiting and security headers on port
  80/443

### Monitoring Profile (with Prometheus & Grafana)

```bash
docker-compose --profile monitoring up -d
```

- **epr-mcp-server**: Core MCP server
- **prometheus**: Metrics collection on port 9090
- **grafana**: Visualization dashboard on port 3000

### Full Stack (All Services)

```bash
docker-compose --profile production --profile monitoring up -d
```

## Available Endpoints

### Core Server (Port 8000)

- **MCP Endpoint**: `http://localhost:8000/mcp`
- **API Documentation**: `http://localhost:8000/docs`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`
- **Health Check**: `http://localhost:8000/health`

### Production (Port 80/443)

- **Web Interface**: `http://localhost/` (proxied to core server)
- **SSL Support**: Configure certificates in `ssl/` directory

### Monitoring (Port 3000/9090)

- **Grafana Dashboard**: `http://localhost:3000` (admin/admin)
- **Prometheus**: `http://localhost:9090`

## Configuration Files

### Environment Variables (.env)

```bash
# Required
EPR_URL=http://your-epr-server:8042
EPR_TOKEN=your-api-token

# Optional
EPR_DEBUG=false
GRAFANA_USER=admin
GRAFANA_PASSWORD=secure-password
```

### Nginx Configuration (nginx.conf)

- Rate limiting (10 requests/second)
- Security headers
- SSL/TLS support (commented out)
- Proxy configuration

### Prometheus Configuration (prometheus.yaml)

- Scrapes metrics from MCP server
- 15-second scrape intervals
- Self-monitoring

## Management Commands

### Start Services

```bash
# Default profile
docker-compose up -d

# Specific profiles
docker-compose --profile production up -d
docker-compose --profile monitoring up -d
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f epr-mcp-server
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart epr-mcp-server
```

### Update and Rebuild

```bash
# Pull latest images and rebuild
docker-compose pull
docker-compose build --no-cache
docker-compose up -d
```

## Health Monitoring

### Built-in Health Checks

- **Container Health**: Docker health checks every 30 seconds
- **HTTP Health**: `curl http://localhost:8000/health`
- **Service Dependencies**: Containers wait for healthy dependencies

### Monitoring Stack

When using the monitoring profile:

1. **Prometheus** collects metrics from the MCP server
2. **Grafana** provides visualization dashboards
3. **Health checks** ensure service availability

## Development Workflow

### Local Development

```bash
# Start with debug mode
EPR_DEBUG=true docker-compose up -d

# Follow logs for debugging
docker-compose logs -f epr-mcp-server

# Reload configuration
docker-compose restart epr-mcp-server
```

### Testing Changes

```bash
# Rebuild after code changes
docker-compose build epr-mcp-server
docker-compose up -d epr-mcp-server

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

## Production Deployment

### 1. SSL Configuration

```bash
# Create SSL directory
mkdir ssl

# Add your certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem

# Update nginx.conf to enable HTTPS
# (uncomment the HTTPS server block)
```

### 2. Security Considerations

- Use strong passwords for Grafana
- Configure proper EPR_TOKEN
- Enable SSL/TLS for production
- Consider firewall rules
- Regular security updates

### 3. Resource Limits

Add resource limits to docker-compose.yaml:

```yaml
services:
  epr-mcp-server:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**

   ```bash
   # Check port usage
   lsof -i :8000

   # Change ports in docker-compose.yaml
   ports:
     - "8001:8000"  # Use different host port
   ```

2. **Environment Variables Not Loading**

   ```bash
   # Verify .env file exists and has correct format
   cat .env

   # Restart with fresh environment
   docker-compose down
   docker-compose up -d
   ```

3. **Health Check Failures**

   ```bash
   # Check server logs
   docker-compose logs epr-mcp-server

   # Test health endpoint directly
   docker-compose exec epr-mcp-server curl localhost:8000/health
   ```

4. **Network Issues**

   ```bash
   # Check network connectivity
   docker network ls
   docker network inspect epr-mcp-network

   # Recreate network
   docker-compose down
   docker-compose up -d
   ```

### Getting Help

- Check logs: `docker-compose logs -f`
- Inspect containers: `docker-compose ps`
- Debug networks: `docker network inspect epr-mcp-network`
- Report issues: GitHub Issues

## Advanced Configuration

### Custom Networks

```yaml
networks:
  epr-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Volume Mounts for Development

```yaml
services:
  epr-mcp-server:
    volumes:
      - ./src:/src/epr_mcp/src:ro # Mount source for development
```

### Multiple Environments

Create separate compose files:

- `docker-compose.yaml` (base)
- `docker-compose.dev.yaml` (development overrides)
- `docker-compose.prod.yaml` (production overrides)

Usage:

```bash
# Development
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

# Production
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d
```
