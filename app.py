import requests
from flask import Flask, request, Response
import os

app = Flask(__name__)

API_PRINCIPAL = "https://techstore-api-1-5grr.onrender.com"
API_BACKUP = "https://proyectoad2.onrender.com"
HEALTH_TIMEOUT = 5

def is_api_alive(url):
    try:
        resp = requests.get(f"{url}/productos", timeout=HEALTH_TIMEOUT)
        # Considera viva si es JSON y no tiene la palabra "suspended"
        if resp.status_code == 200 and 'application/json' in resp.headers.get('Content-Type', ''):
            return True
        return False
    except:
        return False

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    # Decidir target
    if is_api_alive(API_PRINCIPAL):
        target = API_PRINCIPAL
    else:
        target = API_BACKUP
        print(f"⚠️ Usando backup: {target}")

    # Construir URL completa
    url = f"{target}/{path}"
    
    # Copiar cabeceras omitiendo 'host' y otras problemáticas
    headers = {}
    for key, value in request.headers:
        if key.lower() in ('host', 'content-length', 'connection'):
            continue
        headers[key] = value
    
    try:
        # Reenviar la petición con los mismos parámetros, datos, etc.
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            timeout=30
        )
        # Construir respuesta de Flask copiando TODAS las cabeceras de la respuesta original
        response_headers = [(name, value) for name, value in resp.headers.items()
                            if name.lower() not in ('content-encoding', 'transfer-encoding', 'content-length')]
        # Devolver el contenido tal cual, con el código de estado y cabeceras
        return Response(resp.content, status=resp.status_code, headers=response_headers)
    except Exception as e:
        return Response(f"Error en el balanceador: {str(e)}", status=500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)