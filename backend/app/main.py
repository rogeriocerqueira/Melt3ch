from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base, get_db
from app.api.routes import router

# Cria tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MelT3ch API",
    description="Plataforma IoT de rastreabilidade apícola — Mel Igapó / Alagoas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok", "service": "MelT3ch API", "version": "1.0.0"}

@app.on_event("startup")
def startup():
    db = next(get_db())
    try:
        from app.services.seed import seed_database
        seed_database(db)
    finally:
        db.close()

app.include_router(router, prefix="/api")
