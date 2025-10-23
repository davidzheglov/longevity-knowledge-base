# Use Debian-based images to avoid OpenSSL 1.1 issues on Alpine (musl)
FROM node:20-bookworm-slim AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
# Basic packages and certs
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends ca-certificates openssl && \
    rm -rf /var/lib/apt/lists/* && \
    npm ci

FROM deps AS build
WORKDIR /app
COPY . .
# Generate Prisma client before building Next.js so API routes can import @prisma/client
RUN npx prisma generate
RUN npm run build

FROM node:20-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000
# Ensure certs available
RUN apt-get update -y && apt-get install -y --no-install-recommends ca-certificates openssl && rm -rf /var/lib/apt/lists/*

# Copy only what's needed to run `next start`
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
# Optional: copy prisma folder for reference/tools (not required at runtime but useful for migrations)
COPY --from=build /app/prisma ./prisma
COPY --from=build /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "run", "start"]
