"""Seed inicial — cria dados de exemplo para demonstração do MVP."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import Produtor, Colmeia, Lote, LoteColmeia, EtapaCadeia, Laudo, LeituraSensor
from app.services.auth import hash_password


def seed_database(db: Session):
    """Popula o banco com dados de demonstração se estiver vazio."""
    if db.query(Produtor).first():
        return  # Já tem dados

    # ── Produtor ──────────────────────────────────────
    produtor = Produtor(
        nome="Daiane Santos Cerqueira",
        email="daiane@melt3ch.com",
        senha_hash=hash_password("melt3ch2026"),
        municipio="Maceió",
        estado="AL"
    )
    db.add(produtor)
    db.flush()

    # ── Colmeias ──────────────────────────────────────
    colmeias_data = [
        {"codigo": "C-01", "florada": "Cipó-de-São-João", "status": "normal"},
        {"codigo": "C-02", "florada": "Cipó-de-São-João", "status": "alerta"},
        {"codigo": "C-03", "florada": "Aroeira",          "status": "normal"},
        {"codigo": "C-04", "florada": "Aroeira",          "status": "normal"},
        {"codigo": "C-05", "florada": "Angico",           "status": "normal"},
        {"codigo": "C-06", "florada": "Angico",           "status": "critico"},
    ]
    colmeias = []
    for d in colmeias_data:
        c = Colmeia(produtor_id=produtor.id, **d)
        db.add(c)
        colmeias.append(c)
    db.flush()

    # ── Leituras iniciais dos sensores ─────────────────
    import random
    sensor_base = [
        (34.2, 62, 48.7, 210),  # C-01 normal
        (36.8, 71, 44.1, 380),  # C-02 alerta
        (33.9, 60, 52.3, 195),  # C-03 normal
        (34.5, 63, 49.8, 220),  # C-04 normal
        (33.1, 58, 51.6, 185),  # C-05 normal
        (39.4, 78, 38.2, 520),  # C-06 critico
    ]
    base_time = datetime.utcnow() - timedelta(hours=24)
    for i, c in enumerate(colmeias):
        t_base, u_base, p_base, s_base = sensor_base[i]
        # 48 leituras = 24h de dados
        for h in range(48):
            ts = base_time + timedelta(minutes=30 * h)
            leitura = LeituraSensor(
                colmeia_id=c.id,
                timestamp=ts,
                temperatura=round(t_base + random.uniform(-0.5, 0.5), 1),
                umidade=round(u_base + random.uniform(-2, 2), 1),
                peso=round(p_base + (h * 0.02), 1),
                som=round(s_base + random.uniform(-15, 15), 0),
                status_calculado=c.status
            )
            db.add(leitura)

    # ── Lote aprovado ─────────────────────────────────
    lote1 = Lote(
        codigo="LT-2026-047",
        produtor_id=produtor.id,
        florada="Cipó-de-São-João + Aroeira",
        data_extracao=datetime(2026, 6, 12),
        volume_kg=38.5,
        status_lab="aprovado",
        destino="Mercado Livre / E-commerce"
    )
    db.add(lote1)
    db.flush()

    # Colmeias do lote
    for c in colmeias[:3]:  # C-01, C-02, C-03
        db.add(LoteColmeia(lote_id=lote1.id, colmeia_id=c.id))

    # Etapas da cadeia
    etapas1 = [
        (1, "colmeia",       "🌳", "Mata nativa preservada",
         "01/05/2026", "Alagoas — Sertão",
         "Colmeias C-01, C-03 e C-04 em área de caatinga preservada. Florada identificada: Cipó-de-São-João e Aroeira."),
        (2, "monitoramento", "📡", "Monitoramento IoT contínuo",
         "01/05 → 12/06/2026", "Sistema MelT3ch embarcado",
         "Temperatura média 34,2°C · Umidade 62% · Ganho de peso +38,5 kg · Nenhuma anomalia detectada em 42 dias."),
        (3, "extracao",      "🍯", "Extração a frio",
         "12/06/2026", "Unidade de beneficiamento",
         "Extração centrífuga a frio, sem aquecimento. Temperatura do mel durante extração: 28°C. Rendimento: 38,5 kg."),
        (4, "analise",       "🔬", "Análise laboratorial",
         "15/06/2026", "Laboratório parceiro homologado",
         "Brix 80,2% · pH 3,8 · HMF 8,2 mg/kg · Diastase 12,4 DN · Resultado: APROVADO."),
        (5, "envase",        "📦", "Envase e QR code",
         "17/06/2026", "Alagoas",
         "Envase em potes âmbar 300g. QR code de rastreabilidade gerado. 128 unidades produzidas."),
        (6, "distribuicao",  "🚚", "Distribuição",
         "20/06/2026", "AL → Brasil",
         "Transporte em caixas isotérmicas, temperatura controlada entre 15-25°C."),
        (7, "venda",         "🛒", "Na prateleira",
         "25/06/2026", "Mercado Livre · E-commerce · Varejo",
         "Disponível para compra. QR code ativo para consulta do consumidor."),
    ]
    for ordem, tipo, ico, titulo, data, local, detalhe in etapas1:
        db.add(EtapaCadeia(
            lote_id=lote1.id, ordem=ordem, tipo=tipo, icone=ico,
            titulo=titulo, data=data, local=local, detalhe=detalhe
        ))

    # Laudo do lote aprovado
    db.add(Laudo(
        lote_id=lote1.id,
        data_analise=datetime(2026, 6, 15),
        laboratorio="Laboratório parceiro homologado",
        responsavel_tecnico="Tamires Santos Cerqueira",
        brix=80.2, ph=3.8, hmf=8.2, diastase=12.4,
        umidade_mel=17.3, cor="Âmbar claro", aprovado=True
    ))

    # ── Lote em análise ───────────────────────────────
    lote2 = Lote(
        codigo="LT-2026-048",
        produtor_id=produtor.id,
        florada="Angico",
        data_extracao=datetime(2026, 6, 18),
        volume_kg=15.0,
        status_lab="em_analise",
        destino="Empório Orgânico Maceió"
    )
    db.add(lote2)
    db.flush()
    db.add(LoteColmeia(lote_id=lote2.id, colmeia_id=colmeias[4].id))

    # ── Lote reprovado ────────────────────────────────
    lote3 = Lote(
        codigo="LT-2026-046",
        produtor_id=produtor.id,
        florada="Cipó-de-São-João",
        data_extracao=datetime(2026, 6, 4),
        volume_kg=15.9,
        status_lab="reprovado",
        destino="—"
    )
    db.add(lote3)
    db.flush()
    for c in colmeias[1:3]:  # C-02, C-03
        db.add(LoteColmeia(lote_id=lote3.id, colmeia_id=c.id))

    db.commit()
    print("✅ Seed concluído — produtor: daiane@melt3ch.com / senha: melt3ch2026")
