# Simhastha 2028 Web - local dev image
# Dev-mode image: runs `next dev` against a bind-mounted source tree (see
# infra/docker-compose.yml) for hot reload. Not a production build/image —
# Sprint 1 scope is a local-dev-ready scaffold, not a production deploy.
FROM node:20-slim

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
