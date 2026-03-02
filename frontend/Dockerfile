FROM cgr.dev/chainguard/node:latest-dev AS build

USER root
RUN mkdir -p /app && chown -R node:node /app
USER node

WORKDIR /app

# Copy package files
COPY --chown=node:node package*.json ./

# Install dependencies
RUN npm install

# Copy source code and build static assets
COPY --chown=node:node . .
RUN npm run build

# Serve static assets with an unprivileged Nginx runtime
FROM cgr.dev/chainguard/nginx:latest

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
CMD ["-g", "daemon off;"]
