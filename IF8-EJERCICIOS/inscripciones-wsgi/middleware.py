import json
import os
from hmac import compare_digest


def autenticacion(aplicacion):
    def middleware(environ, start_response):
        token = environ.get('HTTP_AUTHORIZATION', '')
        esperado = 'Bearer ' + os.environ.get('API_TOKEN', 'token123')
        if not compare_digest(token, esperado):
            cuerpo = json.dumps({'error': 'Token incorrecto'}).encode('utf-8')
            start_response('401 Unauthorized', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(cuerpo)))])
            return [cuerpo]
        return aplicacion(environ, start_response)
    return middleware
