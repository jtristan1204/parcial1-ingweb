# servidor web basico con python y flask
from flask import Flask, request, redirect, send_from_directory, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')

archivo_datos = 'mensajes.json'

# ruta de inicio que entrega el index desde la carpeta html
@app.route('/')
def inicio():
    return send_from_directory('html', 'index.html')

# ruta para cualquier pagina dentro de la carpeta html
@app.route('/html/<path:archivo>')
def servir_html(archivo):
    return send_from_directory('html', archivo)

# rutas directas amigables
@app.route('/acerca.html')
def acerca():
    return send_from_directory('html', 'acerca.html')

@app.route('/contacto.html')
def contacto():
    return send_from_directory('html', 'contacto.html')

@app.route('/index.html')
def index_directo():
    return send_from_directory('html', 'index.html')

# ruta para recibir y guardar datos del formulario
@app.route('/enviar-contacto', methods=['POST'])
def recibir_contacto():
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    asunto = request.form.get('asunto', '').strip()
    mensaje = request.form.get('mensaje', '').strip()

    # validacion basica en el servidor
    if not nombre or not correo or not asunto or not mensaje:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'exito': False, 'error': 'campos_incompletos'}, 400
        return redirect('/html/contacto.html?error=campos_incompletos')

    nuevo_registro = {
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'nombre': nombre,
        'correo': correo,
        'asunto': asunto,
        'mensaje': mensaje
    }

    # lectura y actualizacion del archivo json
    datos = []
    if os.path.exists(archivo_datos):
        try:
            with open(archivo_datos, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                if not isinstance(datos, list):
                    datos = []
        except Exception:
            datos = []

    datos.append(nuevo_registro)

    with open(archivo_datos, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    # respuesta en json para solicitudes asincronas o redireccion a contacto
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'exito': True, 'mensaje': 'guardado con exito'}, 200

    return redirect('/html/contacto.html?enviado=1')

# ruta para consultar los mensajes guardados en formato json
@app.route('/ver-mensajes')
def ver_mensajes():
    if os.path.exists(archivo_datos):
        try:
            with open(archivo_datos, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            return json.dumps(datos, ensure_ascii=False, indent=2), 200, {'Content-Type': 'application/json; charset=utf-8'}
        except Exception:
            return json.dumps([], ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'}
    return json.dumps([], ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'}

# iniciar servidor
if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=puerto, debug=True)
