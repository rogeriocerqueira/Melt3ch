from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ── Auth ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Sensor ───────────────────────────────────────────
class LeituraSensorCreate(BaseModel):
    colmeia_codigo: str
    temperatura: float
    umidade: float
    peso: float
    som: float

class LeituraSensorOut(BaseModel):
    id: int
    timestamp: datetime
    temperatura: float
    umidade: float
    peso: float
    som: float
    status_calculado: str

    class Config:
        from_attributes = True


# ── Colmeia ───────────────────────────────────────────
class ColmeiaOut(BaseModel):
    id: int
    codigo: str
    florada: Optional[str]
    status: str
    ultima_leitura: Optional[LeituraSensorOut] = None
    producao_estimada_kg: Optional[float] = None

    class Config:
        from_attributes = True


# ── Laudo ─────────────────────────────────────────────
class LaudoOut(BaseModel):
    brix: Optional[float]
    ph: Optional[float]
    hmf: Optional[float]
    diastase: Optional[float]
    umidade_mel: Optional[float]
    cor: Optional[str]
    aprovado: bool
    laboratorio: Optional[str]
    responsavel_tecnico: Optional[str]
    data_analise: Optional[datetime]

    class Config:
        from_attributes = True


# ── Etapa ─────────────────────────────────────────────
class EtapaOut(BaseModel):
    ordem: int
    tipo: str
    titulo: str
    data: Optional[str]
    local: Optional[str]
    detalhe: Optional[str]
    icone: Optional[str]
    concluida: bool

    class Config:
        from_attributes = True


# ── Lote público (QR code) ────────────────────────────
class LotePublicoOut(BaseModel):
    codigo: str
    florada: Optional[str]
    data_extracao: Optional[datetime]
    volume_kg: Optional[float]
    status_lab: str
    destino: Optional[str]
    colmeias: List[str] = []
    etapas: List[EtapaOut] = []
    laudo: Optional[LaudoOut] = None
    produtor_municipio: Optional[str] = None
    produtor_estado: Optional[str] = None

    class Config:
        from_attributes = True


# ── Dashboard produtor ────────────────────────────────
class DashboardOut(BaseModel):
    produtor_nome: str
    total_colmeias: int
    colmeias_alerta: int
    producao_total_estimada: float
    lotes_aprovados: Optional[int] = 0
    lotes_em_analise: Optional[int] = 0
    lotes_reprovados: Optional[int] = 0
    colmeias: List[ColmeiaOut]
    lotes: List[dict] = []


# ── Lote produtor ─────────────────────────────────────
class LoteOut(BaseModel):
    id: int
    codigo: str
    florada: Optional[str]
    data_extracao: Optional[datetime]
    volume_kg: Optional[float]
    status_lab: str
    destino: Optional[str]
    colmeias: List[str] = []
    laudo: Optional[LaudoOut] = None

    class Config:
        from_attributes = True
