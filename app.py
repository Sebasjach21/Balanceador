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
        # Verifica que la respuesta sea JSON y contenga los datos esperados
        if resp.status_code == 200 and 'application/json' in resp.headers.get('Content-Type', ''):
            return True
        return False
    except:
        return False

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    # Seleccionar API objetivo
    if is_api_alive(API_PRINCIPAL):
        target = API_PRINCIPAL
    else:
        target = API_BACKUP
        print(f"⚠️ Usando backup: {target}")

    # Construir URL completa
    url = f"{target}/{path}"
    
    # Reenviar la petición tal cual, excepto la cabecera Host
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}
    
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            timeout=30,
            allow_redirects=False
        )
        # Preparar las cabeceras de respuesta (copiando todas excepto algunas problemáticas)
        response_headers = [(name, value) for name, value in resp.raw.headers.items()
                            if name.lower() not in ('content-encoding', 'transfer-encoding')]
        # Crear respuesta con el contenido original y su código de estado
        return Response(resp.content, status=resp.status_code, headers=response_headers)
    except requests.exceptions.RequestException as e:
        return Response(f"Error en el balanceador: {str(e)}", status=500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)