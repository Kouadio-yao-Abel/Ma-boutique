from flask import Flask, render_template_string

app = Flask(__name__)

NUMERO_WHATSAPP = "225554762656"

produits = [
    {"id": 1, "nom": "Chaussure Élégante", "prix": 15000, "stock": 100, "image": "👟"},
    {"id": 2, "nom": "Sac à Main", "prix": 12000, "stock": 100, "image": "👜"},
    {"id": 3, "nom": "Montre Classique", "prix": 20000, "stock": 100, "image": "⌚"},
]

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ma Boutique - Abel</title>
<style>
body{font-family:Arial; padding:15px; background:#f5f5f5; margin:0}
h1{text-align:center; color:#333}
.card{background:white; padding:15px; margin:12px 0; border-radius:12px; box-shadow:0 2px 8px #ddd}
.btn{background:#25D366; color:white; padding:14px; border:none; border-radius:10px; width:100%; font-size:17px; font-weight:bold; text-decoration:none; display:block; text-align:center; margin-top:12px}
.prix{color:#25D366; font-weight:bold; font-size:20px}
.stock{color:green}
</style>
</head>
<body>
<h1>🛍️ Ma Boutique</h1>
<p style="text-align:center">Livraison partout en Côte d'Ivoire</p>
{% for p in produits %}
<div class="card">
<h3>{{p.image}} {{p.nom}}</h3>
<p class="prix">{{p.prix}} FCFA</p>
<p class="stock">Stock: {{p.stock}} disponible ✅</p>
<a class="btn" href="https://wa.me/{{numero}}?text=Bonjour Abel, je veux commander {{p.nom}} à {{p.prix}} FCFA" target="_blank">💬 Commander sur WhatsApp</a>
</div>
{% endfor %}
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, produits=produits, numero=NUMERO_WHATSAPP)

if __name__ == "__main__":
    app.run()
