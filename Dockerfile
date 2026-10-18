FROM node:24-bookworm-slim@sha256:0e0ff40c39bc087845bfb27465a0df4ea419520094bc35842ff83dd8cbe6f9b6
WORKDIR /app
COPY package.json package-lock.json ./
COPY vendor ./vendor
RUN npm cache add ./vendor/*.tgz --offline --ignore-scripts && npm ci --offline --omit=dev --ignore-scripts --no-audit --no-fund && npm cache clean --force
COPY src ./src
USER node
ENV NODE_ENV=production HOST=0.0.0.0 PORT=8080 RELAY_DB=/data/relay/relay.sqlite
EXPOSE 8080
CMD ["node","src/start.mjs"]
