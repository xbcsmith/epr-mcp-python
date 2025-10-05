FROM registry.access.redhat.com/ubi8/python-312:latest

# Environment variables for EPR configuration
ENV EPR_URL=http://localhost:8042
ENV EPR_DEBUG=false
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

# EPR_TOKEN should be provided at runtime for security

# Expose the HTTP port for MCP server
EXPOSE 8000

WORKDIR /src/epr_mcp
COPY . /src/epr_mcp

# Install the package and dependencies
RUN pip install --no-cache-dir /src/epr_mcp/dist/epr_mcp-0.1.0-py2.py3-none-any.whl

# Add health check for HTTP server
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the MCP server in HTTP mode
CMD ["python3", "-m", "epr_mcp.main", "start"]