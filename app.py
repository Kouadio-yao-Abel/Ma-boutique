from flask import Flask, render_template_string, request, session, redirect
import random

app = Flask(__name__)
app.secret_key = "abel_secret_2026"

NUMERO_WHATSAPP = "2250507961624"
MOT_DE_PASSE_ADMIN = "Abel123"

config_jeu = {
    "numero_gagnant": random.randint(1, 100),
    "cote": random.randint(2, 10),
    "mise_min": 200,
    "max_num": 100
}

produits = [
    {"nom": "Chaussure", "prix": 15000, "stock": 100, "image": "👟"},
    {"nom": "Sac", "prix": 12000, "stock": 100, "image": "👜"},
]

HTML_HOME = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ma Boutique + Loto</title>
<style>
body{font-family:Arial; padding:15px; background:#f5f5f5}
.card{background:white; padding:15px; margin:12px 0; border-radius:12px; box-shadow:0 2px 5px #ddd}
.btn{padding:14px; border:none; border-radius:10px; width:100%; font-size:17px; font-weight:bold; display:block; text-align:center; text-decoration:none; margin-top:10px}
.btn-green{background:#25D366; color:white} .btn-blue{background:#007bff; color:white}
input{width:100%; padding:12px; margin:6px 0; border-radius:8px; border:1px solid #ccc; box-sizing:border-box}
.alert-red{background:#ffdddd; color:red; padding:10px; border-radius:8px; border:1px solid red; margin:10px 0}
</style></head>
<body>
<h1>🛍️ Ma Boutique</h1>
{% for p in produits %}
<div class="card">
<h3>{{p.image}} {{p.nom}}</h3><p style="color:#25D366; font-weight:bold">{{p.prix}} FCFA - Stock: {{p.stock}} ✅</p>
<a class="btn btn-green" href="https://wa.me/{{numero}}?text=Je veux commander {{p.nom}}" target="_blank">Commander WhatsApp</a>
</div>
{% endfor %}
<hr><h1>🎰 JEU LOTO - 1 à 100</h1>
<div class="card">
<p>Côte: <b>x{{config.cote}}</b> | Mise min: <b>{{config.mise_min}} FCFA</b></p>
<form method="POST" action="/jouer">
<input type="number" name="choix" placeholder="Ton numéro (1-100)" required min="1" max="100">
<input type="number" name="mise" placeholder="Ta mise min 200F" required min="200">
<button class="btn btn-blue" type="submit">JOUER</button>
</form>
{% if erreur %}<div class="alert-red">{{erreur}}</div>{% endif %}
{% if resultat %}<h2>{{resultat}}</h2>
{% if gagne %}<a class="btn btn-green" href="https://wa.me/{{numero}}?text={{msg_win}}" target="_blank">💰 Réclamer gain WhatsApp</a>{% endif %}{% endif %}
</div>
</body></html>
"""

HTML_LOGIN = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Admin</title>
<style>body{font-family:Arial; padding:15px} input{width:100%; padding:12px; margin:6px 0; border-radius:8px; border:1px solid #ccc} .btn{background:black; color:white; padding:14px; width:100%; border-radius:10px}</style>
</head><body><h1>🔒 Admin</h1><div style="background:white; padding:15px; border-radius:12px">
<form method="POST"><input type="password" name="password" placeholder="Mot de passe" required><button class="btn" type="submit">Entrer</button></form>
{% if error %}<p style="color:red">{{error}}</p>{% endif %}</div></body></html>"""

HTML_ADMIN = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Admin</title>
<style>body{font-family:Arial; padding:15px} .btn{background:black; color:white; padding:14px; width:100%; border-radius:10px; margin:5px 0; border:none; font-weight:bold} .btn-rand{background:#ff9800; color:white}</style>
</head><body>
<h1>🔒 ADMIN</h1>
<div style="background:white; padding:15px; border-radius:12px">
<p>Gagnant: <b>{{config.numero_gagnant}}</b> (1-100) | Côte: <b>x{{config.cote}}</b></p>
<form method="POST" action="/admin/update">
<button name="action" value="random" class="btn btn-rand" type="submit">🎲 GÉNÉRER ALÉATOIREMENT (1-100)</button>
</form>
<hr>
<form method="POST" action="/admin/update">
<input type="number" name="numero_gagnant" placeholder="Numéro 1-100" min="1" max="100">
<input type="number" name="cote" placeholder="Côte ex: 5" min="1">
<button name="action" value="manual" class="btn" type="submit">Mettre à jour manuel</button>
</form>
<br><a href="/admin/logout">Déconnexion</a> | <a href="/">Boutique</a>
</div></body></html>"""

@app.route("/")
def home():
    return render_template_string(HTML_HOME, produits=produits, config=config_jeu, numero=NUMERO_WHATSAPP, resultat=None, erreur=None)

@app.route("/jouer", methods=["POST"])
def jouer():
    try:
        choix = int(request.form["choix"])
        mise = int(request.form["mise"])
    except:
        return render_template_string(HTML_HOME, produits=produits, config=config_jeu, numero=NUMERO_WHATSAPP, resultat=None, erreur="Entre des nombres valides !", gagne=False)

    if mise < config_jeu["mise_min"]:
        return render_template_string(HTML_HOME, produits=produits, config=config_jeu, numero=NUMERO_WHATSAPP, resultat=None, erreur=f"❌ Minimum {config_jeu['mise_min']} FCFA ! Tu as mis {mise}F", gagne=False)
    
    if choix < 1 or choix > 100:
        return render_template_string(HTML_HOME, produits=produits, config=config_jeu, numero=NUMERO_WHATSAPP, resultat=None, erreur="❌ Numéro doit être entre 1 et 100", gagne=False)

    gagnant = config_jeu["numero_gagnant"]
    cote = config_jeu["cote"]
    
    if choix == gagnant:
        gain = mise * cote
        resultat = f"🎉 GAGNÉ ! C'était {gagnant}. Tu gagnes {gain} FCFA (x{cote}) !"
        msg = f"J'ai gagné au Loto 1-100 ! Mise {mise}F sur {choix}, gagnant {gagnant}, gain {gain}F (côte x{cote})"
        config_jeu["numero_gagnant"] = random.randint(1, 100)
        config_jeu["cote"] = random.randint(2, 10)
        return render_template_string(HTML_HOME, produits=produits, config=config_jeu, numero=NUMERO_WHATSAPP, resultat=resultat, gagne=True, msg_win=msg, erreur=None)
    else:
        resultat = f"😭 Perdu... {choix} ≠ {gagnant}. Nouveau tirage lancé !"
        config_jeu["numero_gagnant"] = random.randint(1, 100)
        config_jeu["cote"] = random.randint(2, 10)
        return render_template_string(HTML_HOME, produits=produits, config=config_jeu, numero=NUMERO_WHATSAPP, resultat=resultat, gagne=False, erreur=None)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["password"] == MOT_DE_PASSE_ADMIN:
            session["admin"] = True
            return redirect("/admin/panel")
        else:
            return render_template_string(HTML_LOGIN, error="Mot de passe incorrect !")
    if session.get("admin"):
        return redirect("/admin/panel")
    return render_template_string(HTML_LOGIN, error=None)

@app.route("/admin/panel")
def admin_panel():
    if not session.get("admin"):
        return redirect("/admin")
    return render_template_string(HTML_ADMIN, config=config_jeu)

@app.route("/admin/update", methods=["POST"])
def admin_update():
    if not session.get("admin"):
        return redirect("/admin")
    action = request.form.get("action")
    if action == "random":
        config_jeu["numero_gagnant"] = random.randint(1, 100)
        config_jeu["cote"] = random.randint(2, 10)
    else:
        if request.form.get("numero_gagnant"):
            config_jeu["numero_gagnant"] = int(request.form["numero_gagnant"])
        if request.form.get("cote"):
            config_jeu["cote"] = int(request.form["cote"])
    return render_template_string(HTML_ADMIN, config=config_jeu)

@app.route("/admin/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

if __name__ == "__main__":
    app.run()
