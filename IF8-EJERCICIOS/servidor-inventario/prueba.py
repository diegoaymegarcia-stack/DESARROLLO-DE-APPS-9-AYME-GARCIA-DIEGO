from urllib.request import urlopen
from urllib.error import HTTPError

for ruta in ['/', '/style.css', '/api/inventario?limite=5&pagina=1',
             '/api/inventario?filtro=lapiz', '/api/inventario?limite=101',
             '/api/inventario?pagina=0', '/no-existe.html']:
    try:
        with urlopen('http://localhost:8000' + ruta) as respuesta:
            print(respuesta.status, respuesta.headers.get('Content-Type'), ruta)
    except HTTPError as error:
        print(error.code, ruta)
