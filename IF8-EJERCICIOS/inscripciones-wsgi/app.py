import json
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server
from middleware import autenticacion


def responder(start_response, estado, datos):
    cuerpo = json.dumps(datos, ensure_ascii=False).encode('utf-8')
    start_response(estado, [('Content-Type', 'application/json; charset=utf-8'),
                            ('Content-Length', str(len(cuerpo)))])
    return [cuerpo]


def aplicacion(environ, start_response):
    if environ['PATH_INFO'] != '/api/inscripciones':
        return responder(start_response, '404 Not Found', {'error': 'Ruta no encontrada'})
    if environ['REQUEST_METHOD'] != 'POST':
        return responder(start_response, '405 Method Not Allowed', {'error': 'Usa POST'})

    try:
        longitud = int(environ.get('CONTENT_LENGTH') or 0)
        if longitud <= 0 or longitud > 10000:
            raise ValueError('Tamaño de solicitud inválido')
        cuerpo = environ['wsgi.input'].read(longitud).decode('utf-8')
        tipo = environ.get('CONTENT_TYPE', '').split(';')[0].strip().lower()
        if tipo == 'application/json':
            datos = json.loads(cuerpo)
        elif tipo == 'application/x-www-form-urlencoded':
            datos = {k: v[0] for k, v in parse_qs(cuerpo, keep_blank_values=True).items()}
        else:
            return responder(start_response, '415 Unsupported Media Type', {'error': 'Formato no permitido'})
        if not isinstance(datos, dict):
            raise ValueError('Datos inválidos')
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return responder(start_response, '400 Bad Request', {'error': 'Solicitud inválida'})

    campos = ('dni', 'correo_electronico', 'programa_academico')
    if any(not isinstance(datos.get(c), str) or not datos[c].strip() for c in campos):
        return responder(start_response, '400 Bad Request', {'error': 'Faltan campos obligatorios'})

    return responder(start_response, '201 Created', {'mensaje': 'Inscripción registrada',
                                                     'inscripcion': {c: datos[c].strip() for c in campos}})


app = autenticacion(aplicacion)

if __name__ == '__main__':
    with make_server('localhost', 8000, app) as servidor:
        print('Servidor en http://localhost:8000')
        servidor.serve_forever()
