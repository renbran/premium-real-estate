# Use Node.js 18 Alpine for smaller image size
FROM node:18-alpine

# Install n8n globally
RUN npm install -g n8n@latest

# Create app directory
WORKDIR /app

# Create data directory for n8n
RUN mkdir -p /app/.n8n

# Set environment variables
ENV N8N_USER_FOLDER=/app/.n8n
ENV N8N_HOST=0.0.0.0
ENV N8N_PORT=5678
ENV DB_TYPE=sqlite
ENV DB_SQLITE_DATABASE=/app/.n8n/database.sqlite
ENV N8N_BASIC_AUTH_ACTIVE=true

# Copy workflow file if exists
COPY n8n_bill_automation_workflow.json /app/.n8n/

# Expose the port n8n runs on
EXPOSE 5678

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:5678/healthz || exit 1

# Start n8n
CMD ["n8n", "start"]