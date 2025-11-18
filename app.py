from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'TIAMIOSSOTT12'

API_BASE = "https://api.nal.usda.gov/fdc/v1/"
API_KEY = "QweiYpuEmJTfQlcfZLdquUSeiCqxe7sGaLQo2OaJ"



@app.route("/")
def index():
    return render_template("inicio.html")


@app.route("/search", methods=["POST"])
def buscar_alimento():
    comNombre = request.form.get("food_name", "").strip().lower()

    if not comNombre:
        flash("Por favor, ingresa el nombre de un alimento.", "error")
        return redirect(url_for("index"))

    try:
        buscaUrl = f"{API_BASE}foods/search?query={comNombre}&api_key={API_KEY}"
        busResponse = requests.get(buscaUrl)

        if busResponse.status_code != 200:
            flash("No se pudo conectar con la API del USDA.", "error")
            return redirect(url_for("index"))

        busData = busResponse.json()

        if "foods" not in busData or len(busData["foods"]) == 0:
            flash(f'No se encontraron resultados para "{comNombre}".', "error")
            return redirect(url_for("index"))

        comida = busData["foods"][0]
        fdc_id = comida["fdcId"]

        detUrl = f"{API_BASE}food/{fdc_id}?api_key={API_KEY}"
        detResponse = requests.get(detUrl)
        detData = detResponse.json()

        food_info = {
            "description": detData.get("description", "Sin descripción"),
            "fdcId": detData.get("fdcId"),
            "nutrientes": [
        {
            "name": n.get("nutrientName", ""),
            "amount": n.get("value"),
            "unit": n.get("unitName", "")
        }
        for n in detData.get("foodNutrients", [])
    ]
}


        return render_template("resultado.html", food=food_info)

    except requests.exceptions.RequestException:
        flash("Error al conectar con la API del USDA. Intenta de nuevo más tarde.", "error")
        return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)

