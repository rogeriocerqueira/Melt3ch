# ── Base: dependências ───────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# ── Desenvolvimento: servidor Vite com hot reload ────
FROM deps AS dev
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ── Build de produção ────────────────────────────────
FROM deps AS build
# Vazio = a API é chamada no mesmo endereço do site (/api), via nginx
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
COPY . .
RUN npm run build

# ── Produção: arquivos estáticos servidos pelo nginx ─
FROM nginx:1.27-alpine AS prod
COPY nginx.spa.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80