from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'TIAMIOSSOTT12'

API_BASE = "https://api.nal.usda.gov/fdc/v1/"
API_KEY = "DEMO_KEY"  # <-- pon aquí tu propia API key si la tienes


@app.route("/")
def index():
    return render_template("inicio.html")


@app.route("/search", methods=["POST"])
def buscar_alimento():
    food_name = request.form.get("food_name", "").strip().lower()

    if not food_name:
        flash("Por favor, ingresa el nombre de un alimento.", "error")
        return redirect(url_for("index"))

    try:
        search_url = f"{API_BASE}foods/search?query={food_name}&api_key={API_KEY}"
        search_response = requests.get(search_url)

        if search_response.status_code != 200:
            flash("No se pudo conectar con la API del USDA.", "error")
            return redirect(url_for("index"))

        search_data = search_response.json()

        if "foods" not in search_data or len(search_data["foods"]) == 0:
            flash(f'No se encontraron resultados para "{food_name}".', "error")
            return redirect(url_for("index"))

        food = search_data["foods"][0]
        fdc_id = food["fdcId"]

        detail_url = f"{API_BASE}food/{fdc_id}?api_key={API_KEY}"
        detail_response = requests.get(detail_url)
        detail_data = detail_response.json()

        food_info = {
            "description": detail_data.get("description", "Sin descripción"),
            "fdcId": detail_data.get("fdcId"),
            "nutrients": [
                {
                    "name": n.get("nutrient", {}).get("name", ""),
                    "amount": n.get("amount"),
                    "unit": n.get("nutrient", {}).get("unitName", "")
                }
                for n in detail_data.get("foodNutrients", [])
            ]
        }

        return render_template("resultado.html", food=food_info)

    except requests.exceptions.RequestException:
        flash("Error al conectar con la API del USDA. Intenta de nuevo más tarde.", "error")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
