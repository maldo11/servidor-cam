from flask import Flask, request, jsonify, render_template,
send_from_directory import os import json from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'fotos'
DATA_FILE = 'registros.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def cargar_registros():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def guardar_registro(nombre, codigo_qr, tipo="MAYOR"):
    registros = cargar_registros()
    registros.insert(0, {
    "archivo": nombre,
    "codigo_qr": codigo_qr,
    "tipo": tipo,
    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
})
    with open(DATA_FILE, 'w') as f:
        json.dump(registros, f)

@app.route('/upload', methods=['POST'])
def upload():
    codigo_qr = request.headers.get('X-QR-Code', 'desconocido')
    tipo = request.headers.get('X-Tipo', 'MAYOR')
    imagen = request.data

    nombre = f"foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    if tipo == 'MENOR':
        guardar_registro("sin_foto", codigo_qr, tipo)
        return jsonify({"status": "ok", "tipo": "menor_registrado"}), 200

    if not imagen:
        return jsonify({"error": "sin imagen"}), 400

    ruta = os.path.join(UPLOAD_FOLDER, nombre)
    with open(ruta, 'wb') as f:
        f.write(imagen)

    guardar_registro(nombre, codigo_qr, tipo)
    print(f"Foto recibida: {nombre} | QR: {codigo_qr} | Tipo: {tipo}")
    return jsonify({"status": "ok", "archivo": nombre}), 200

@app.route('/fotos/<nombre>')
def servir_foto(nombre):
    return send_from_directory(UPLOAD_FOLDER, nombre)

@app.route('/')
def galeria():
    registros = cargar_registros()
    return render_template('index.html', registros=registros)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
