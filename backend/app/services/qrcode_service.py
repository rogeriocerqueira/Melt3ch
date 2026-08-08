import qrcode
import io
import base64

def gerar_qr_base64(lote_codigo: str, base_url: str = "http://localhost:5173") -> str:
    """Gera QR code do lote em base64 para embutir no HTML."""
    url = f"{base_url}/rastreio/{lote_codigo}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#3B2208", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_b64}"

def gerar_qr_url(lote_codigo: str, base_url: str = "http://localhost:5173") -> str:
    """Retorna a URL de rastreio do lote."""
    return f"{base_url}/rastreio/{lote_codigo}"
