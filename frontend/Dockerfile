# ---------- Build stage ----------
FROM node:20-slim AS build

WORKDIR /app

# Install dependencies against the lockfile for reproducible builds.
COPY package.json package-lock.json* ./
RUN npm ci

# Build the production bundle. VITE_* vars must be present at build time
# because Vite inlines them into the static output.
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY . .
RUN npm run build

# ---------- Serve stage ----------
FROM node:20-slim AS serve

WORKDIR /app

# Only the build output and the bits vite preview needs to run.
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/vite.config.ts ./vite.config.ts

EXPOSE 5173

# Serve the built bundle. --host exposes it outside the container.
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5173"]
