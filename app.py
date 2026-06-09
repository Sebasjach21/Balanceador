import requests
from flask import Flask, request, Response
import os

app = Flask(__name__)

# URLs de tus APIs
API_PRINCIPAL = "https://techstore-api-1-5grr.onrender.com"
API_BACKUP = "https://proyectoad2.onrender.com"

# Tiempo de espera para health check (segundos)
HEALTH_TIMEOUT = 5

def is_api_alive(url):
    """Verifica si la API responde con JSON válido (contiene 'success' o 'data')"""
    try:
        resp = requests.get(f"{url}/productos", timeout=HEALTH_TIMEOUT)
        # Si la respuesta contiene 'success' o 'data' y no es HTML de suspensión
        if resp.status_code == 200 and "application/json" in resp.headers.get("Content-Type", ""):
            return True
        return False
    except:
        return False

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    # Verificar estado de la API principal
    if is_api_alive(API_PRINCIPAL):
        target = API_PRINCIPAL
    else:
        target = API_BACKUP
        print("⚠️ API principal caída, usando backup")

    # Reenviar la petición al target elegido
    url = f"{target}/{path}"
    method = request.method
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}
    try:
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            timeout=30
        )
        # Excluir cabeceras que causan problemas
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [(name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, response_headers)
    except Exception as e:
        return Response(f"Error en el balanceador: {e}", 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
