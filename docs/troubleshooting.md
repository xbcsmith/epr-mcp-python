# Troubleshooting Guide

This guide covers common issues and their solutions when running the EPR MCP
Server.

## Connection Issues

### "All connection attempts failed"

**Error Message:**

```text
Error fetching event: All connection attempts failed
```

**Cause:** The MCP server cannot connect to the EPR API server.

**Solutions:**

#### 1. Running in Docker (Most Common)

When running the MCP server in Docker, `localhost` refers to the container
itself, not the host machine.

**If EPR server runs on host machine:**

```bash
# In your .env file:
EPR_URL=http://host.docker.internal:8042
```

**If EPR server runs in another Docker container:**

```bash
# In your .env file (replace 'epr-server' with actual container name):
EPR_URL=http://epr-server:8042
```

**If EPR server is on a different machine:**

```bash
# In your .env file:
EPR_URL=http://your-epr-server-hostname:8042
```

#### 2. Check EPR Server Status

Verify the EPR server is running and accessible:

```bash
# Test direct connection to EPR server
curl http://localhost:8042/health
# or
curl http://your-epr-server:8042/health
```

#### 3. Verify Network Connectivity

```bash
# From within the Docker container:
docker exec -it epr-mcp-server curl http://host.docker.internal:8042/health

# Check if the container can resolve DNS:
docker exec -it epr-mcp-server nslookup host.docker.internal
```

## Configuration Issues

### Environment Variables Not Loading

**Symptoms:** Server uses default values instead of your configuration.

**Solutions:**

1. Ensure `.env` file is in the project root directory
2. Check `.env` file format (no spaces around `=`)
3. Verify Docker Compose loads the `.env` file:

   ```bash
   docker-compose config
   ```

### Invalid API Token

**Error Message:**

```text
HTTP error from EPR server: 401 - Unauthorized
```

**Solutions:**

1. Verify your `EPR_TOKEN` in the `.env` file
2. Check token hasn't expired
3. Ensure token has required permissions

## Docker Issues

### Docker Compose Issues

#### Container Won't Start

**Check logs:**

```bash
docker-compose logs epr-mcp-server
```

**Common solutions:**

1. Check port 8000 isn't already in use:

   ```bash
   lsof -i :8000
   ```

2. Rebuild the container:

   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

#### Health Check Failing

**Check health status:**

```bash
docker-compose ps
```

**Solutions:**

1. Verify the health endpoint is accessible:

   ```bash
   curl http://localhost:8000/health
   ```

2. Check server logs for startup errors

### Direct Docker Issues

#### Docker Container Won't Start

**Check logs:**

```bash
docker logs epr-mcp-server
```

**Common solutions:**

1. Check if port is already in use:

   ```bash
   lsof -i :8000
   # If in use, run with different port:
   docker run -p 8001:8000 ...
   ```

2. Verify Docker image exists:

   ```bash
   docker images | grep epr-mcp-server
   ```

3. Rebuild the image:

   ```bash
   docker build --no-cache -t epr-mcp-server .
   ```

#### Environment Variables Not Working

**Check if variables are set correctly:**

```bash
docker exec -it epr-mcp-server env | grep EPR
```

**Solutions:**

1. Ensure all required variables are provided:

   ```bash
   docker run -e EPR_URL=... -e EPR_TOKEN=... epr-mcp-server
   ```

2. Use environment file:

   ```bash
   docker run --env-file .env epr-mcp-server
   ```

#### Container Exits Immediately

**Check exit code and logs:**

```bash
docker ps -a  # Find container ID
docker logs <container-id>
```

**Common causes:**

- Missing required environment variables (EPR_TOKEN)
- Invalid EPR_URL format
- Application startup errors

#### Permission Issues

**Error:** "Permission denied" when mounting volumes

**Solutions:**

```bash
# Fix file permissions
chmod 644 .env
chmod -R 755 logs/

# Run with user ID
docker run --user $(id -u):$(id -g) ...
```

## Development Issues

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'epr_mcp'`

**Solutions:**

1. Install in development mode:

   ```bash
   pip install -e .
   ```

2. Verify virtual environment is activated:

   ```bash
   which python
   ```

### Test Failures

**Run tests with verbose output:**

```bash
python -m pytest tests/ -v
```

**Common solutions:**

1. Install test dependencies:

   ```bash
   pip install -e .[test]
   ```

2. Clear pytest cache:

   ```bash
   rm -rf .pytest_cache
   ```

## Debugging

### Enable Debug Mode

Add to your `.env` file:

```bash
EPR_DEBUG=true
```

### View Detailed Logs

```bash
# Docker Compose
docker-compose logs -f epr-mcp-server

# Local development
python -m epr_mcp start --debug
```

### Test Specific Operations

```bash
# Test a specific MCP tool (requires MCP client)
mcp.call_tool('fetchEvent', {'id': 'test-event-id'})
```

## Getting Help

If you continue experiencing issues:

1. **Check the logs** with debug mode enabled
2. **Verify network connectivity** between containers/services
3. **Test the EPR server directly** using curl or another HTTP client
4. **Create an issue** with:
   - Error messages
   - Docker Compose output
   - Environment configuration (without sensitive tokens)
   - Steps to reproduce

## Common Error Messages

| Error                            | Likely Cause               | Solution                                             |
| -------------------------------- | -------------------------- | ---------------------------------------------------- |
| `All connection attempts failed` | Network connectivity       | Check EPR_URL, use `host.docker.internal` for Docker |
| `401 Unauthorized`               | Invalid API token          | Verify EPR_TOKEN                                     |
| `404 Not Found`                  | Wrong endpoint URL         | Check EPR server API endpoints                       |
| `Connection timeout`             | EPR server overloaded/slow | Increase timeout, check EPR server status            |
| `Address already in use`         | Port 8000 occupied         | Stop conflicting service or change port              |
