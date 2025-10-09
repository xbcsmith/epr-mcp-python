# Docker Quick Reference

Quick reference for running EPR MCP Server with Docker.

## Basic Commands

### Build and Run

```bash
# Build image
docker build -t epr-mcp-server .

# Basic run
docker run -p 8000:8000 \
  -e EPR_URL=http://host.docker.internal:8042 \
  -e EPR_TOKEN=your-token \
  epr-mcp-server

# Run in background
docker run -d --name epr-mcp-server \
  -p 8000:8000 \
  -e EPR_URL=http://host.docker.internal:8042 \
  -e EPR_TOKEN=your-token \
  epr-mcp-server
```

### Management

```bash
# View running containers
docker ps

# View logs
docker logs -f epr-mcp-server

# Stop container
docker stop epr-mcp-server

# Remove container
docker rm epr-mcp-server

# Execute command in container
docker exec -it epr-mcp-server bash
```

## Common Scenarios

### Development

```bash
# Interactive mode with debug
docker run -it --rm \
  -p 8000:8000 \
  -e EPR_URL=http://host.docker.internal:8042 \
  -e EPR_TOKEN=your-token \
  -e EPR_DEBUG=true \
  epr-mcp-server
```

### Production

```bash
# Daemon with restart policy
docker run -d \
  --name epr-mcp-server \
  --restart unless-stopped \
  -p 8000:8000 \
  -e EPR_URL=http://your-epr-server:8042 \
  -e EPR_TOKEN=your-token \
  epr-mcp-server
```

### With Persistent Logs

```bash
# Mount logs directory
docker run -d \
  --name epr-mcp-server \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -e EPR_URL=http://host.docker.internal:8042 \
  -e EPR_TOKEN=your-token \
  epr-mcp-server
```

### With Configuration File

```bash
# Mount .env file
docker run -d \
  --name epr-mcp-server \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env:ro \
  epr-mcp-server
```

### Custom Network

```bash
# Create network
docker network create epr-network

# Run with custom network
docker run -d \
  --name epr-mcp-server \
  --network epr-network \
  -p 8000:8000 \
  -e EPR_URL=http://epr-api-server:8042 \
  -e EPR_TOKEN=your-token \
  epr-mcp-server
```

## Environment Variables

| Variable    | Description    | Example                            |
| ----------- | -------------- | ---------------------------------- |
| `EPR_URL`   | EPR server URL | `http://host.docker.internal:8042` |
| `EPR_TOKEN` | API token      | `your-secret-token`                |
| `EPR_DEBUG` | Debug mode     | `true` or `false`                  |
| `MCP_HOST`  | Bind address   | `0.0.0.0`                          |
| `MCP_PORT`  | Server port    | `8000`                             |

## Networking

### EPR Server Locations

| EPR Server Location | Docker EPR_URL                     |
| ------------------- | ---------------------------------- |
| Host machine        | `http://host.docker.internal:8042` |
| Docker container    | `http://container-name:8042`       |
| Remote server       | `http://remote-host:8042`          |
| Local (non-Docker)  | `http://localhost:8042`            |

## Troubleshooting

### Check Container Status

```bash
# Container running?
docker ps

# Container logs
docker logs epr-mcp-server

# Container details
docker inspect epr-mcp-server
```

### Test Connectivity

```bash
# Test EPR connection from container
docker exec -it epr-mcp-server \
  curl http://host.docker.internal:8042/health

# Test MCP server
curl http://localhost:8000/health
```

### Port Issues

```bash
# Check port usage
lsof -i :8000

# Use different port
docker run -p 8001:8000 ...
```

### Debug Container

```bash
# Interactive shell
docker exec -it epr-mcp-server bash

# Check environment
docker exec -it epr-mcp-server env | grep EPR

# Check processes
docker exec -it epr-mcp-server ps aux
```

## Cleanup

### Remove Container

```bash
# Stop and remove
docker stop epr-mcp-server
docker rm epr-mcp-server

# Force remove
docker rm -f epr-mcp-server
```

### Remove Image

```bash
# Remove image
docker rmi epr-mcp-server

# Remove all unused images
docker image prune -a
```

### Complete Cleanup

```bash
# Remove everything (containers, networks, images, volumes)
docker system prune -a

# Remove only stopped containers and unused images
docker system prune
```
