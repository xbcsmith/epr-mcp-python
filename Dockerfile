FROM registry.access.redhat.com/ubi8/python-312:latest

ENV EPR_URL=http://localhost:8024
ENV EPR_DEBUG=false

WORKDIR /src/epr_mcp
COPY . /src/epr_mcp
RUN pip install --no-cache-dir /src/epr_mcp/dist/epr_mcp-0.1.0-py2.py3-none-any.whl

CMD ["python3", "/opt/app-root/bin/eprmcp",  "start",  "--url", "${EPR_URL}", "--debug"]