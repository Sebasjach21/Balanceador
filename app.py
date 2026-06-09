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
        if resp.status_code == 200 and 'application/json' in resp.headers.get('Content-Type', ''):
            return True
        return False
    except:
        return False

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    if is_api_alive(API_PRINCIPAL):
        target = API_PRINCIPAL
        print("Usando API principal")
    else:
        target = API_BACKUP
        print("⚠️ Usando backup")

    url = f"{target}/{path}"
    headers = {k: v for k, v in request.headers if k.lower() != 'host'}
    
    try:
        # Reenviar la petición sin descomprimir automáticamente para evitar problemas
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
        # Construir cabeceras de respuesta, excluyendo las que causan problemas
        excluded = ['content-encoding', 'transfer-encoding', 'content-length']
        response_headers = [(name, value) for name, value in resp.raw.headers.items() 
                            if name.lower() not in excluded]
        # Forzar Content-Type a application/json si la respuesta es JSON (para evitar símbolos raros)
        if 'application/json' in resp.headers.get('Content-Type', ''):
            response_headers.append(('Content-Type', 'application/json; charset=utf-8'))
        return Response(resp.content, status=resp.status_code, headers=response_headers)
    except Exception as e:
        return Response(f"Error en el balanceador: {str(e)}", status=500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)