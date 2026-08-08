"""
MelT3ch IoT Simulator
Simula leituras reais de sensores das colmeias via LoRaWAN
Envia para a API FastAPI a cada INTERVAL_SECONDS
"""
import os, time, random, logging
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SIM] %(message)s")
log = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://backend:8000")
INTERVAL = int(os.getenv("INTERVAL_SECONDS", "30"))

# Perfil base de cada colmeia (temperatura, umidade, peso_base, som)
COLMEIAS = [
    {"codigo": "C-01", "temp": 34.2, "umidade": 62, "peso": 48.7, "som": 210, "perfil": "normal"},
    {"codigo": "C-02", "temp": 36.8, "umidade": 71, "peso": 44.1, "som": 380, "perfil": "alerta"},
    {"codigo": "C-03", "temp": 33.9, "umidade": 60, "peso": 52.3, "som": 195, "perfil": "normal"},
    {"codigo": "C-04", "temp": 34.5, "umidade": 63, "peso": 49.8, "som": 220, "perfil": "normal"},
    {"codigo": "C-05", "temp": 33.1, "umidade": 58, "peso": 51.6, "som": 185, "perfil": "normal"},
    {"codigo": "C-06", "temp": 39.4, "umidade": 78, "peso": 38.2, "som": 520, "perfil": "critico"},
]

# Acumula peso ao longo do tempo (produção)
peso_acumulado = {c["codigo"]: c["peso"] for c in COLMEIAS}
ciclo = 0

def gerar_leitura(colmeia: dict) -> dict:
    """Gera leitura realista com ruído e deriva temporal."""
    global ciclo
    codigo = colmeia["codigo"]
    perfil = colmeia["perfil"]

    # Ruído realista por tipo de sensor
    noise_temp  = random.gauss(0, 0.3)
    noise_umid  = random.gauss(0, 1.5)
    noise_som   = random.gauss(0, 20)

    # Peso cresce levemente (produção de mel) — 0.01kg a cada leitura normal
    ganho = 0.01 if perfil == "normal" else 0.003
    peso_acumulado[codigo] = round(peso_acumulado[codigo] + ganho, 2)

    # Temperatura oscila com ciclo circadiano (mais quente de dia)
    ciclo_diurno = 0.8 * abs(((ciclo % 48) - 24) / 24 - 0.5)
    temp = round(colmeia["temp"] + noise_temp + ciclo_diurno, 1)
    umid = round(max(30, min(95, colmeia["umidade"] + noise_umid)), 1)
    som  = round(max(100, colmeia["som"] + noise_som), 0)
    peso = peso_acumulado[codigo]

    return {
        "colmeia_codigo": codigo,
        "temperatura": temp,
        "umidade": umid,
        "peso": peso,
        "som": som,
    }

def aguardar_backend(max_tentativas=30):
    """Aguarda o backend estar pronto antes de começar."""
    for i in range(max_tentativas):
        try:
            r = httpx.get(f"{API_URL}/health", timeout=5)
            if r.status_code == 200:
                log.info(f"Backend pronto em {API_URL}")
                return True
        except Exception:
            pass
        log.info(f"Aguardando backend... ({i+1}/{max_tentativas})")
        time.sleep(5)
    return False

def enviar_leitura(payload: dict) -> bool:
    try:
        r = httpx.post(f"{API_URL}/api/iot/leitura", json=payload, timeout=10)
        if r.status_code == 200:
            return True
        log.warning(f"Erro {r.status_code}: {r.text}")
        return False
    except Exception as e:
        log.error(f"Falha ao enviar para {payload['colmeia_codigo']}: {e}")
        return False

def main():
    global ciclo
    log.info(f"MelT3ch IoT Simulator iniciado — intervalo: {INTERVAL}s")
    log.info(f"API: {API_URL} — {len(COLMEIAS)} colmeias")

    if not aguardar_backend():
        log.error("Backend não respondeu — encerrando")
        return

    while True:
        sucesso = 0
        for colmeia in COLMEIAS:
            payload = gerar_leitura(colmeia)
            if enviar_leitura(payload):
                sucesso += 1
                log.info(
                    f"{payload['colmeia_codigo']} → "
                    f"T:{payload['temperatura']}°C "
                    f"U:{payload['umidade']}% "
                    f"P:{payload['peso']}kg "
                    f"S:{payload['som']}Hz"
                )

        ciclo += 1
        log.info(f"Ciclo {ciclo} concluído — {sucesso}/{len(COLMEIAS)} colmeias OK")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
