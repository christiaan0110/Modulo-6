from flask import Flask, request, jsonify, redirect, url_for, render_template
import redis
import json


client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Crear la aplicación Flask
app = Flask(__name__, template_folder='templates')


# Ruta principal que muestra el menú
@app.route('/')
def index():
    return render_template('base_html.html')  # Cambiar 'index.html' a 'base_html.html'

# Ruta para agregar una receta desde el formulario web
@app.route('/agregar', methods=['GET', 'POST'])
def agregar_receta():
    if request.method == 'POST':
        data = request.form
        nombre = data.get('nombre')

        if not nombre:
            return jsonify({"error": "El nombre de la receta es requerido"}), 400

        receta = {
            "nombre": nombre,
            "ingredientes": data.getlist('ingredientes'),
            "pasos": data.getlist('pasos')
        }

        # Guardar receta en KeyDB
        client.set(nombre, json.dumps(receta))
        return redirect(url_for('ver_recetas'))

    return render_template('recetas html.html')


@app.route('/recetas', methods=['GET'])
def ver_recetas():
    recetas_keys = client.keys()
    recetas = []

    for key in recetas_keys:
        if client.type(key) == 'string':  #
            receta_json = client.get(key)
            if receta_json:
                try:
                    receta = json.loads(receta_json)
                    recetas.append(receta)
                except json.JSONDecodeError:
                    print(f"Advertencia: La receta con clave {key} contiene datos no válidos.")
            else:
                print(f"Advertencia: La clave {key} tiene un valor vacío o nulo.")
        else:
            print(f"Advertencia: La clave {key} no es del tipo string.")

    return render_template('ver_recetas.html', recetas=recetas)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)