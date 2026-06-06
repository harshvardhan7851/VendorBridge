# =============================================================================
# VendorBridge Frontend - Dockerfile
# Base Image: Node 20 LTS
# =============================================================================

FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files first for layer caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy the rest of the source code
# (In development, source is mounted as a volume — this runs Vite dev server)
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start Vite dev server with host flag for Docker network access
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
