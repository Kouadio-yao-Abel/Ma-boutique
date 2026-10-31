from flask import Flask, render_template_string, request

app = Flask(__name__)

NUMERO_WHATSAPP = "2250507961624"

# === PARTIE ADMIN : c'est toi qui changes ici ===
config_jeu = {
    "numero_gagnant": 7,
    "cote": 3,
    "mise_min": 500
}

produits = [
    {"nom": "Chaussure", "prix": 15000, "stock": 100, "image": "👟"},
    {"nom": "Sac", "prix": 12000, "stock": 100, "image": "👜"},
]

HTML_HOME = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ma Boutique + Loto</title>
<style>
body{font-family:Arial; padding:15px; background:#f5f5f5}
.card{background:white; padding:15px; margin:12px 0; border-radius:12px; box-shadow:0 2px 5px #ddd}
.btn{padding:14px; border:none; border-radius:10px; width:100%; font-size:17px; font-weight:bold; display:block; text-align:center; text-decoration:none; margin-top:10px}
.btn-green{background:#25D366; color:white}
.btn-blue{background:#007bff; color:white}
input{width:100%; padding:12px; margin:6px 0; border-radius:8px; border:1px solid #ccc; box-sizing:border-box}
.prix{color:#25D366; font-weight:bold}
</style>
</head>
<body>
<h1>🛍️ Ma Boutique</h1>

{% for p in produits %}
<div class="card">
<h3>{{p.image}} {{p.nom}}</h3>
<p class="prix">{{p.prix}} FCFA - Stock: {{p.stock}} ✅</p>
<a class="btn btn-green" href="https://wa.me/{{numero}}?text=Je veux commander {{p.nom}}" target="_blank">Commander WhatsApp</a>
</div>
{% endfor %}

<hr>
<h1>🎰 JEU LOTO</h1>
<div class="card">
<p>Côte actuelle: <b>x{{config.cote}}</b> | Mise min: {{config.mise_min}} FCFA</p>
<p>Devine le numéro entre 1 et 20 !</p>
<form method="POST" action="/jouer">
<input type="number" name="choix" placeholder="Ton numéro (1-20)" required min="1" max="20">
<input type="number" name="mise" placeholder="Ta mise FCFA (ex: 500)" required>
<button class="btn btn-blue" type="submit">JOUER</button>
</form>
{% if resultat %}
<h2>{{resultat}}</h2>
{% if gagne %}
<a class="btn btn-green" href="https://wa.me/{{numero}}?text={{msg_win}}" target="_blank">💰 Réclamer mon gain sur WhatsApp</a>
{% endif %}
{% endif %}
</div>

<p style="text-align:center; margin-top:20px"><a href="/admin">🔒 Espace Admin (toi)</a></p>
</body>
</html>
"""

HTML_ADMIN = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Admin</title>
<style>body{font-family:Arial; padding:15px} input{width:100%; padding:12px; margin:6px 0} .btn{background:black; color:white; padding:14px; width:100%; border-radius:10px}</style>
</head>
<body>
<h1>🔒 ADMIN - C'est toi Abel</h1>
<div style="background:white; padding:15px; border-radius:12px">
<p>Numéro gagnant actuel: <b>{{config.numero_gagnant}}</b> | Côte: <b>x{{config.cote}}</b></p>
<form method="POST">
<input type="number" name="numero_gagnant" placeholder="Nouveau numéro gagnant (1-20)" required min="1" max="20">
<input type="number" name="cote" placeholder="Nouvelle côte (ex: 3)" required min="1">
<button class="btn" type="submit">METTRE À JOUR LE JEU</button>
</form>
<p><a href="/">Retour boutique</a></p>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_HOME, produits=produits, config=config_jeu, numero=NUMERO_WHATSAPP, resultat=None)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        config_jeu["numero_gagnant"] = int(request.form["numero_gagnant"])
        config_jeu["cote"] = int(request.form["cote"])
    return render_template_string(HTML_ADMIN, config=config_jeu)

@app.route("/jouer", methods=["POST"])
def jouer():
    choix = int(request.form["choix"])
    mise = int(request.form["mise"])
    gagnant = config_jeu["numero_gagnant"]
    cote = config_jeu["cote"]
    
    if choix == gagnant:
        gain = mise * cote
        resultat = f"🎉 GAGNÉ ! C'était bien {gagnant}. Tu remportes {gain} FCFA !"
        msg = f"Bonjour, j'ai gagné au Loto ! J'ai misé {mise} FCFA sur {choix} et le numéro gagnant est {gagnant}. Mon gain est {gain} FCFA (côte x{cote})"
        return render_template_string(HTML_HOME, produits=produits, config=config_jeu, numero=NUMERO_WHATSAPP, resultat=resultat, gagne=True, msg_win=msg)
    else:
        resultat = f"😭 Perdu... Tu as mis {choix}, le gagnant était {gagnant}. Retente !"
        return render_template_string(HTML_HOME, produits=produits, config=config_jeu, numero=NUMERO_WHATSAPP, resultat=resultat, gagne=False)

if __name__ == "__main__":
    app.run()
