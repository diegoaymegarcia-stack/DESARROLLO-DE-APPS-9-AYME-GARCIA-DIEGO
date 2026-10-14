import json
from io import BytesIO
from wsgiref.util import setup_testing_defaults
from app import app


def probar(nombre, token, datos, tipo='application/json'):
    cuerpo = json.dumps(datos).encode() if tipo == 'application/json' else datos.encode()
    entorno = {}
    setup_testing_defaults(entorno)
    entorno.update(PATH_INFO='/api/inscripciones', REQUEST_METHOD='POST',
                   CONTENT_TYPE=tipo, CONTENT_LENGTH=str(len(cuerpo)),
                   HTTP_AUTHORIZATION=token, **{'wsgi.input': BytesIO(cuerpo)})
    resultado = {}

    def iniciar(estado, cabeceras):
        resultado['estado'] = estado

    respuesta = b''.join(app(entorno, iniciar)).decode()
    print(f'{nombre}: {resultado["estado"]} - {respuesta}')


probar('JSON válido', 'Bearer token123', {'dni': '12345678', 'correo_electronico': 'alumno@correo.com', 'programa_academico': 'Ingeniería de Sistemas'})
probar('Formulario válido', 'Bearer token123', 'dni=12345678&correo_electronico=alumno%40correo.com&programa_academico=Sistemas', 'application/x-www-form-urlencoded')
probar('Campo faltante', 'Bearer token123', {'dni': '12345678'})
probar('Token incorrecto', 'Bearer incorrecto', {'dni': '12345678'})
