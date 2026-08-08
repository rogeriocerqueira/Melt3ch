from sqlalchemy.orm import Session
from app.models.models import Colmeia, LeituraSensor

# Limites ideais por parâmetro
LIMITES = {
    "temperatura": {"ok": (30, 36), "alerta": (36, 38), "critico": (38, 50)},
    "umidade":     {"ok": (40, 70), "alerta": (70, 80), "critico": (80, 100)},
    "peso":        {"ok": (35, 70), "alerta": (20, 35), "critico": (0, 20)},
    "som":         {"ok": (150, 300), "alerta": (300, 450), "critico": (450, 9999)},
}

def calcular_status(temp: float, umidade: float, peso: float, som: float) -> str:
    """Calcula status da colmeia baseado nos sensores."""
    criticos = 0
    alertas = 0

    def check(val, limites):
        nonlocal criticos, alertas
        ok_min, ok_max = limites["ok"]
        if ok_min <= val <= ok_max:
            return
        al_min, al_max = limites["alerta"]
        if al_min <= val <= al_max:
            alertas += 1
            return
        criticos += 1

    check(temp, LIMITES["temperatura"])
    check(umidade, LIMITES["umidade"])
    check(peso, LIMITES["peso"])
    check(som, LIMITES["som"])

    if criticos > 0:
        return "critico"
    if alertas > 0:
        return "alerta"
    return "normal"

def registrar_leitura(db: Session, colmeia: Colmeia,
                      temp: float, umidade: float,
                      peso: float, som: float) -> LeituraSensor:
    status = calcular_status(temp, umidade, peso, som)

    leitura = LeituraSensor(
        colmeia_id=colmeia.id,
        temperatura=temp,
        umidade=umidade,
        peso=peso,
        som=som,
        status_calculado=status
    )
    db.add(leitura)

    # Atualiza status da colmeia
    colmeia.status = status
    db.add(colmeia)
    db.commit()
    db.refresh(leitura)
    return leitura

def ultima_leitura(db: Session, colmeia_id: int) -> LeituraSensor | None:
    return (
        db.query(LeituraSensor)
        .filter(LeituraSensor.colmeia_id == colmeia_id)
        .order_by(LeituraSensor.timestamp.desc())
        .first()
    )

def producao_estimada(db: Session, colmeia_id: int) -> float:
    """Estima produção baseada no ganho de peso."""
    leituras = (
        db.query(LeituraSensor)
        .filter(LeituraSensor.colmeia_id == colmeia_id)
        .order_by(LeituraSensor.timestamp)
        .all()
    )
    if len(leituras) < 2:
        return 0.0
    ganho = leituras[-1].peso - leituras[0].peso
    return max(round(ganho, 2), 0.0)
