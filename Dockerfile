FROM python:3.13-slim

WORKDIR /app

# Install necessary dependencies for LiteFS
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    fuse3 \
    sqlite3 \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Set up LiteFS with architecture detection
ENV LITEFS_VERSION=0.5.11
RUN ARCH=$(uname -m); \
    case "$ARCH" in \
    x86_64) LITEFS_ARCH="amd64" ;; \
    aarch64|arm64) LITEFS_ARCH="arm64" ;; \
    *) echo "Unsupported architecture: $ARCH"; exit 1 ;; \
    esac && \
    curl -fsSL "https://github.com/superfly/litefs/releases/download/v${LITEFS_VERSION}/litefs-v${LITEFS_VERSION}-linux-${LITEFS_ARCH}.tar.gz" -o litefs.tar.gz && \
    tar -C /usr/local/bin -xzf litefs.tar.gz && \
    rm litefs.tar.gz && \
    chmod +x /usr/local/bin/litefs

# Copy configuration file
COPY litefs.yml /etc/litefs.yml

# Create directories for LiteFS
RUN mkdir -p /var/lib/litefs/data

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content directory first
COPY data/content /app/data/content

# Copy the rest of the application
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Create a non-root user to run the application
# Note: LiteFS requires root to mount FUSE
# RUN useradd -m appuser
# USER appuser

# Expose the ports (App and LiteFS proxy)
EXPOSE 8080 20202

# Use the entrypoint script only
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"] 