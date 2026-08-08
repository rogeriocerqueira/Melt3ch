from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.core.database import get_db
from app.models.models import Produtor, Colmeia, LeituraSensor, Lote, LoteColmeia, EtapaCadeia, Laudo
from app.schemas.schemas import (
    LoginRequest, Token, LeituraSensorCreate, LeituraSensorOut,
    ColmeiaOut, LoteOut, LotePublicoOut, DashboardOut, EtapaOut, LaudoOut
)
from app.services.auth import verify_password, hash_password, create_token, get_current_produtor
from app.services import iot as iot_service
from app.services.qrcode_service import gerar_qr_base64

router = APIRouter()

# ══════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════

@router.post("/auth/login", response_model=Token, tags=["Auth"])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login do produtor — retorna JWT."""
    produtor = db.query(Produtor).filter(Produtor.email == payload.email).first()
    if not produtor or not verify_password(payload.senha, produtor.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = create_token({"sub": produtor.email})
    return {"access_token": token}

# ══════════════════════════════════════════════════════
# IOT
# ══════════════════════════════════════════════════════

@router.post("/iot/leitura", response_model=LeituraSensorOut, tags=["IoT"])
def receber_leitura(payload: LeituraSensorCreate, db: Session = Depends(get_db)):
    """Recebe leitura dos sensores IoT — chamado pelo simulador/hardware real."""
    colmeia = db.query(Colmeia).filter(Colmeia.codigo == payload.colmeia_codigo).first()
    if not colmeia:
        raise HTTPException(status_code=404, detail=f"Colmeia {payload.colmeia_codigo} não encontrada")
    leitura = iot_service.registrar_leitura(
        db, colmeia,
        payload.temperatura, payload.umidade,
        payload.peso, payload.som
    )
    return leitura

@router.get("/iot/colmeia/{codigo}/historico", response_model=List[LeituraSensorOut], tags=["IoT"])
def historico_colmeia(
    codigo: str, limite: int = 48,
    db: Session = Depends(get_db),
    produtor: Produtor = Depends(get_current_produtor)
):
    """Histórico de leituras (48 últimas = 24h)."""
    colmeia = db.query(Colmeia).filter(
        Colmeia.codigo == codigo,
        Colmeia.produtor_id == produtor.id
    ).first()
    if not colmeia:
        raise HTTPException(status_code=404, detail="Colmeia não encontrada")
    return (db.query(LeituraSensor)
            .filter(LeituraSensor.colmeia_id == colmeia.id)
            .order_by(desc(LeituraSensor.timestamp))
            .limit(limite).all())

# ══════════════════════════════════════════════════════
# DASHBOARD — produtor autenticado
# ══════════════════════════════════════════════════════

@router.get("/dashboard", response_model=DashboardOut, tags=["Dashboard"])
def dashboard(
    db: Session = Depends(get_db),
    produtor: Produtor = Depends(get_current_produtor)
):
    """Painel IoT do produtor com dados em tempo real."""
    colmeias = db.query(Colmeia).filter(
        Colmeia.produtor_id == produtor.id,
        Colmeia.ativa == True
    ).all()

    colmeias_out = []
    for c in colmeias:
        ultima = (db.query(LeituraSensor)
                  .filter(LeituraSensor.colmeia_id == c.id)
                  .order_by(desc(LeituraSensor.timestamp))
                  .first())
        colmeias_out.append({
            "id": c.id, "codigo": c.codigo, "florada": c.florada,
            "status": c.status,
            "ultima_temperatura": ultima.temperatura if ultima else None,
            "ultima_umidade":     ultima.umidade     if ultima else None,
            "ultimo_peso":        ultima.peso         if ultima else None,
            "ultimo_som":         ultima.som          if ultima else None,
            "ultimo_update":      ultima.timestamp.isoformat() if ultima else None,
            "producao_estimada":  round(max(0, (ultima.peso or 0) - 30), 1) if ultima else 0,
        })

    alertas = sum(1 for c in colmeias if c.status in ("alerta", "critico"))
    total_prod = sum(c["producao_estimada"] for c in colmeias_out)

    lotes = (db.query(Lote)
             .filter(Lote.produtor_id == produtor.id)
             .order_by(desc(Lote.criado_em))
             .limit(10).all())

    lotes_out = []
    for l in lotes:
        cols = [lc.colmeia.codigo for lc in l.colmeias_lote]
        qr = gerar_qr_base64(l.codigo) if l.status_lab == "aprovado" else None
        lotes_out.append({
            "id": l.id, "codigo": l.codigo, "florada": l.florada,
            "data_extracao": l.data_extracao.strftime("%d/%m/%Y") if l.data_extracao else None,
            "volume_kg": l.volume_kg, "status_lab": l.status_lab,
            "destino": l.destino, "colmeias": cols, "qr_code_base64": qr
        })

    return {
        "produtor_nome": produtor.nome,
        "total_colmeias": len(colmeias),
        "colmeias_alerta": alertas,
        "producao_total_estimada": total_prod,
        "colmeias": colmeias_out,
        "lotes": lotes_out,
    }

# ══════════════════════════════════════════════════════
# RASTREIO PÚBLICO — QR code do consumidor
# ══════════════════════════════════════════════════════

@router.get("/rastreio/{codigo}", response_model=LotePublicoOut, tags=["Rastreio"])
def rastreio_publico(codigo: str, db: Session = Depends(get_db)):
    """
    Rota PÚBLICA — chamada quando o consumidor escaneia o QR code.
    Retorna toda a cadeia de rastreabilidade do lote.
    """
    lote = db.query(Lote).filter(Lote.codigo == codigo).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado")

    # Colmeias do lote
    cols = [lc.colmeia.codigo for lc in lote.colmeias_lote]

    # Etapas da cadeia
    etapas = []
    for e in lote.etapas:
        etapas.append({
            "ordem": e.ordem, "tipo": e.tipo, "icone": e.icone,
            "titulo": e.titulo, "data": e.data,
            "local": e.local, "detalhe": e.detalhe,
            "concluida": e.concluida,
        })

    # Laudo
    laudo_out = None
    if lote.laudo:
        l = lote.laudo
        laudo_out = {
            "brix": l.brix, "ph": l.ph, "hmf": l.hmf,
            "diastase": l.diastase, "umidade_mel": l.umidade_mel,
            "cor": l.cor, "aprovado": l.aprovado,
            "laboratorio": l.laboratorio,
            "responsavel_tecnico": l.responsavel_tecnico,
            "data_analise": l.data_analise.strftime("%d/%m/%Y") if l.data_analise else None,
        }

    # Dados IoT resumidos das colmeias do lote
    iot_resumo = {}
    for lc in lote.colmeias_lote:
        leituras = (db.query(LeituraSensor)
                    .filter(LeituraSensor.colmeia_id == lc.colmeia_id)
                    .order_by(LeituraSensor.timestamp).all())
        if leituras:
            temps = [r.temperatura for r in leituras if r.temperatura]
            iot_resumo = {
                "temperatura_media": round(sum(temps)/len(temps), 1) if temps else None,
                "dias_monitorados": len(set(r.timestamp.date() for r in leituras)),
                "total_leituras": len(leituras),
                "anomalias": sum(1 for r in leituras if r.status_calculado != "normal"),
            }
            break

    return {
        "codigo": lote.codigo,
        "florada": lote.florada,
        "data_extracao": lote.data_extracao.strftime("%d/%m/%Y") if lote.data_extracao else None,
        "volume_kg": lote.volume_kg,
        "status_lab": lote.status_lab,
        "destino": lote.destino,
        "colmeias": cols,
        "etapas": etapas,
        "laudo": laudo_out,
        "iot_resumo": iot_resumo,
        "produtor_municipio": lote.produtor.municipio,
        "produtor_estado": lote.produtor.estado,
    }

# ══════════════════════════════════════════════════════
# QR CODE — gera imagem base64
# ══════════════════════════════════════════════════════

@router.get("/lotes/{codigo}/qr", tags=["Lotes"])
def qr_code_lote(
    codigo: str,
    db: Session = Depends(get_db),
    produtor: Produtor = Depends(get_current_produtor)
):
    """Gera QR code do lote (PNG base64)."""
    lote = db.query(Lote).filter(
        Lote.codigo == codigo,
        Lote.produtor_id == produtor.id
    ).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    return {"qr_code_base64": gerar_qr_base64(codigo), "codigo": codigo}
