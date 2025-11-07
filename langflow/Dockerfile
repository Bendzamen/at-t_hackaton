# You used 1.6.5 in your build logs, so let's keep that
FROM langflowai/langflow:1.6.5

# We're root here; install extra tools
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      git ripgrep \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir -p /app/components /app/workspace /app/data && \
    chown -R 1000:1000 /app

# Ensure langflow is installed globally and accessible
RUN pip install --no-cache-dir langflow==1.6.5 || true

# Langflow will auto-discover components from this path
ENV LANGFLOW_COMPONENTS_PATH=/app/components
ENV PATH="/usr/local/bin:${PATH}"

# Drop privileges to the existing non-root user (UID 1000 already exists)
USER 1000

EXPOSE 7860

# Default command to start langflow
CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
