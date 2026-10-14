from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit, parse_qs
import json
import mimetypes
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'public'))
PRODUCTOS = [
    {'id': i, 'nombre': nombre, 'precio': precio, 'stock': i * 3}
    for i, (nombre, precio) in enumerate([
        ('Lapiz HB', 1.5), ('Cuaderno A4', 8.0), ('Borrador', 1.0),
        ('Regla 30 cm', 3.0), ('Lapicero azul', 2.5), ('Resaltador', 4.5),
        ('Folder', 2.0), ('Tijeras', 6.0), ('Pegamento', 3.5),
        ('Cartulina', 1.2), ('Plumones', 12.0), ('Corrector', 4.0)
    ], 1)
]

class Servidor(BaseHTTPRequestHandler):
    def responder(self, codigo, datos):
        contenido = json.dumps(datos, ensure_ascii=False).encode('utf-8')
        self.send_response(codigo)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == '/api/inventario':
            parametros = parse_qs(url.query, keep_blank_values=True)
            try:
                limite = int(parametros.get('limite', ['10'])[0])
                pagina = int(parametros.get('pagina', ['1'])[0])
                if not 1 <= limite <= 100 or pagina < 1:
                    raise ValueError
            except ValueError:
                return self.responder(400, {'error': 'limite debe ser 1-100 y pagina mayor a 0'})

            filtro = parametros.get('filtro', [''])[0].strip().casefold()
            encontrados = [p for p in PRODUCTOS if filtro in p['nombre'].casefold()]
            inicio = (pagina - 1) * limite
            return self.responder(200, {
                'datos': encontrados[inicio:inicio + limite],
                'total': len(encontrados), 'pagina': pagina,
                'limite': limite, 'total_paginas': (len(encontrados) + limite - 1) // limite
            })

        ruta_relativa = url.path.lstrip('/') or 'index.html'
        ruta = os.path.abspath(os.path.join(BASE, ruta_relativa))
        if os.path.commonpath([BASE, ruta]) != BASE:
            return self.responder(403, {'error': 'Acceso prohibido'})
        if not os.path.isfile(ruta):
            return self.responder(404, {'error': 'Recurso no encontrado'})
        with open(ruta, 'rb') as archivo:
            contenido = archivo.read()
        tipo = mimetypes.guess_type(ruta)[0] or 'application/octet-stream'
        if tipo.startswith('text/'):
            tipo += '; charset=utf-8'
        self.send_response(200)
        self.send_header('Content-Type', tipo)
        self.send_header('Content-Length', str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)

if __name__ == '__main__':
    print('Servidor disponible en http://localhost:8000')
    HTTPServer(('localhost', 8000), Servidor).serve_forever()
