# 🍯 MelT3ch — Plataforma IoT de Rastreabilidade Apícola

**Mel Igapó · **

Stack: Vue.js 3 + FastAPI + PostgreSQL 16 + Docker Compose

---

## 🚀 Rodar localmente (5 minutos)

```bash
git clone https://github.com/seu-usuario/melt3ch.git
cd melt3ch

# Sobe tudo
docker compose up --build
```

Aguarde ~60s e acesse:

| URL | O quê |
|-----|-------|
| http://localhost:5173 | Frontend Vue.js |
| http://localhost:8000/docs | API Swagger |
| http://localhost:5173/#/rastreio/LT-2026-047 | QR consumidor |

**Login:** `daiane@melt3ch.com` / `melt3ch2026`

---

## 📡 Arquitetura

```
Frontend Vue.js 3 (Vite + Pinia + Vue Router)
         │
         │ REST API
         ▼
Backend FastAPI (Python 3.12 + SQLAlchemy)
         │
         │ SQLAlchemy ORM
         ▼
PostgreSQL 16
         ▲
         │ POST /api/iot/leitura a cada 30s
Simulator (Python — simula LoRaWAN)
```

## 🗄 Modelos do banco

| Tabela | Descrição |
|--------|-----------|
| `produtores` | Apicultores com login |
| `colmeias` | Colmeias monitoradas |
| `leituras_sensor` | Dados IoT em tempo real |
| `lotes` | Lotes de produção |
| `lotes_colmeias` | Relação N:N |
| `etapas_cadeia` | Rastreabilidade completa |
| `laudos` | Análise laboratorial |

## 🔑 Endpoints principais

```
POST /api/auth/login          → JWT do produtor
GET  /api/dashboard           → Painel IoT (autenticado)
POST /api/iot/leitura         → Recebe dados do sensor
GET  /api/rastreio/{codigo}   → Rastreio PÚBLICO (QR code)
GET  /api/lotes/{codigo}/qr   → Gera QR base64
GET  /health                  → Status do serviço
GET  /docs                    → Swagger UI
```

---

## 🌐 Deploy no VPS

### Requisitos mínimos
- Ubuntu 22.04+
- 2GB RAM / 2 vCPU / 20GB disco
- Docker + Docker Compose instalados
- Porta 80 aberta

### Passo a passo

```bash
# 1. Instalar Docker no VPS
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 2. Clonar o repositório
git clone https://github.com/seu-usuario/melt3ch.git
cd melt3ch

# 3. Configurar variáveis de ambiente
cp .env.example .env
nano .env  # editar POSTGRES_PASSWORD e VITE_API_URL

# 4. Deploy automático
chmod +x deploy.sh
./deploy.sh
```

### Variáveis de ambiente (.env)

```env
POSTGRES_USER=melt3ch
POSTGRES_PASSWORD=senha_forte_aqui
POSTGRES_DB=melt3ch_db
SECRET_KEY=gere_com_openssl_rand_hex_32
VITE_API_URL=http://IP_DO_VPS
SIMULATOR_INTERVAL=30
```

### Comandos úteis no VPS

```bash
# Ver logs em tempo real
docker compose -f docker-compose.prod.yml logs -f

# Reiniciar um serviço
docker compose -f docker-compose.prod.yml restart backend

# Ver status
docker compose -f docker-compose.prod.yml ps

# Parar tudo
docker compose -f docker-compose.prod.yml down
```

---

## 📱 Fluxo do consumidor (QR Code)

1. Produtor extrai o mel → cria lote no sistema
2. Sistema gera QR code único para o lote
3. QR code vai na etiqueta do pote (sticker ou impressão)
4. Consumidor escaneia com o celular
5. Abre `http://SEU_VPS/#/rastreio/LT-2026-047`
6. Vê toda a cadeia: colmeia → IoT → extração → laudo → prateleira

---

## 🛠 Desenvolvimento

```bash
# Apenas backend + db (sem frontend)
docker compose up db backend simulator

# Rebuild após mudança no código
docker compose up --build backend

# Acessar banco diretamente
docker exec -it melt3ch_db psql -U melt3ch -d melt3ch_db
```

---

*MelT3ch — Mel Igapó · Alagoas · 2026*
*Programa Centelha 3 — Fapeal / Finep / CNPq*
