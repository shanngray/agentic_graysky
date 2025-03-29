#!/bin/bash
set -e

# Enhanced logging function
log() {
  echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] $1"
}

# Debug information
log "Starting entrypoint script..."
log "Current user: $(id)"
log "FUSE device: $(ls -l /dev/fuse 2>/dev/null || echo 'Not found')"
log "LiteFS binary: $(which litefs 2>/dev/null || echo 'Not found')"

# Configure environment variables based on deployment environment
if [ -z "${FLY_APP_NAME:-}" ]; then
    log "Setting up for local development environment"
    # For MacOS compatibility in local development
    export LITEFS_DATA_TYPE="file"
    # Use hostname from Docker Compose
    export LITEFS_ADVERTISE_URL="http://${HOSTNAME:-localhost}:20202"
    export CONSUL_KEY="litefs/agentic-graysky-local-dev"
    export PRIMARY="true"
else
    log "Setting up for Fly.io environment"
    # Use standard FUSE mount on Linux
    export LITEFS_DATA_TYPE="fuse"
    # Use Fly.io internal networking
    export LITEFS_ADVERTISE_URL="http://${HOSTNAME}:20202"
    export CONSUL_KEY="${FLY_APP_NAME}/primary"
    
    # Set PRIMARY environment variable based on region comparison
    if [ "${FLY_REGION}" = "${PRIMARY_REGION}" ]; then
        export PRIMARY="true"
        log "This is a PRIMARY node (FLY_REGION=${FLY_REGION}, PRIMARY_REGION=${PRIMARY_REGION})"
    else
        export PRIMARY="false"
        log "This is a REPLICA node (FLY_REGION=${FLY_REGION}, PRIMARY_REGION=${PRIMARY_REGION})"
    fi
fi

# Ensure directories exist with appropriate permissions
log "Setting up LiteFS directories..."
mkdir -p /var/lib/litefs/data
chown -R root:root /var/lib/litefs
# More secure permissions - directories need execute permission
chmod -R 755 /var/lib/litefs
chmod -R 777 /var/lib/litefs/data  # Only the data directory needs write access for all

# Start LiteFS in the background
log "Starting LiteFS with unified config"
litefs mount --config /etc/litefs.yml &
LITEFS_PID=$!

# Function to check if LiteFS is mounted
check_litefs_mounted() {
  local max_attempts=30
  local attempt=1
  local mounted=false
  
  while [ $attempt -le $max_attempts ]; do
    log "Checking if LiteFS is mounted (attempt $attempt/$max_attempts)..."
    
    if mountpoint -q /var/lib/litefs/data; then
      log "LiteFS successfully mounted"
      mounted=true
      break
    fi
    
    if ! kill -0 $LITEFS_PID 2>/dev/null; then
      log "ERROR: LiteFS process died unexpectedly"
      return 1
    fi
    
    sleep 1
    attempt=$((attempt + 1))
  done
  
  if [ "$mounted" = false ]; then
    log "ERROR: LiteFS failed to mount after $max_attempts attempts"
    return 1
  fi
  
  return 0
}

# Wait for LiteFS to be mounted
if ! check_litefs_mounted; then
  log "FATAL: LiteFS mount failed, exiting"
  exit 1
fi

# Initialize the database if we're the primary
if [ "${PRIMARY:-false}" = "true" ]; then
    log "Primary node: initializing database if needed"
    if [ -f "/app/database/init_db.py" ]; then
        python -m database.init_db
        if [ $? -ne 0 ]; then
            log "WARNING: Database initialization failed"
        else
            log "Database initialization completed successfully"
        fi
    else
        log "WARNING: Database initialization script not found"
    fi
else
    log "Replica node: database will be synchronized from primary"
fi

# Start the application
log "Starting application: $*"
exec "$@" 