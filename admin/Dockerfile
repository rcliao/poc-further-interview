# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files from admin directory (build context is repo root)
COPY admin/package.json admin/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code from admin directory
COPY admin/ .

# Accept build argument for API URL
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration from admin directory
COPY admin/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
