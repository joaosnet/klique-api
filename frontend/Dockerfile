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

# Receive build arguments (must be declared after FROM to be in scope)
ARG VITE_GOOGLE_CLIENT_ID
ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID
ARG VITE_APPLE_CLIENT_ID
ENV VITE_APPLE_CLIENT_ID=$VITE_APPLE_CLIENT_ID
ARG VITE_APPLE_REDIRECT_URI
ENV VITE_APPLE_REDIRECT_URI=$VITE_APPLE_REDIRECT_URI

RUN npm run build

# Serve static assets with an unprivileged Nginx runtime
FROM cgr.dev/chainguard/nginx:latest

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
CMD ["-g", "daemon off;"]
