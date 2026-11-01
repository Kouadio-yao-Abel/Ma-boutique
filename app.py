from flask import Flask, render_template_string, request, session, redirect, jsonify
import random, time

app = Flask(__name__)
app.secret_key = "abel_secret_2026_final"

# TES NUMÉROS DE RÉCEPTION
NUMEROS_PAIEMENT = {
    "WAVE": "0554762656",
    "MTN": "0554762656",
    "ORANGE": "0767911881"
}

config_jeu = {"numero_gagnant": random.randint(1,100), "cote": random.randint(2,10), "mise_min": 200}

# FAUSSE BASE DE DONNÉES (après on mettra une vraie DB)
users = {} # {telephone: {solde: 0, nom: ""}}
depots_en_attente = [] # liste des dépôts
historique_jeux = []

HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Boutique Loto CI</title>
<style>
body{font-family:Arial; padding:15px; background:#f0f2f5} .card{background:white; padding:15px; margin:12px 0; border-radius:12px; box-shadow:0 2px 5px #ddd}
.btn{padding:14px; border:none; border-radius:10px; width:100%; font-weight:bold; display:block; text-align:center; text-decoration:none; margin-top:8px; cursor:pointer}
.btn-green{background:#25D366; color:white} .btn-blue{background:#007bff; color:white} .btn-orange{background:#FF7900; color:white} .btn-yellow{background:#FFCC00; color:black}
input, select{width:100%; padding:12px; margin:6px 0; border-radius:8px; border:1px solid #ccc; box-sizing:border-box}
.badge{padding:5px 10px; border-radius:20px; font-size:12px; color:white} .bg-wait{background:orange} .bg-ok{background:green}
</style></head><body>
<h2>🎰 LOTO CI 1-100 | Solde: {{solde}} F</h2>
{% if user_tel %}
<div class="card">
<b>{{user_tel}}</b> - Solde: <span style="color:green; font-size:20px">{{solde}} F</span>
<a href="/logout" style="float:right">Sortir</a>
<h3>💰 DÉPOSER (comme Melbet)</h3>
<form method="POST" action="/deposer">
<select name="operateur" required><option value="">Choisir</option><option value="WAVE">WAVE - {{nums.WAVE}}</option><option value="MTN">MTN - {{nums.MTN}}</option><option value="ORANGE">ORANGE - {{nums.ORANGE}}</option></select>
<input type="number" name="montant" placeholder="Montant min 200" min="200" required>
<input type="text" name="id_transaction" placeholder="ID transaction après transfert (ex: W123456)" required>
<button class="btn btn-green" type="submit">J'ai payé, confirmer</button>
</form>
<p style="font-size:12px; color:grey">1. Transfère l'argent sur le numéro affiché<br>2. Copie l'ID de transaction<br>3. Attends validation admin (5 min)</p>
</div>

<div class="card">
<p>Côte: x{{config.cote}} | Mise min: {{config.mise_min}}F</p>
<form method="POST" action="/jouer">
<input type="number" name="choix" placeholder="Numéro 1-100" min="1" max="100" required>
<input type="number" name="mise" placeholder="Mise (pris sur ton solde)" min="200" max="{{solde}}" required>
<button class="btn btn-blue" type="submit">JOUER {{config.mise_min}}F min</button>
</form>
{% if msg %}<h3>{{msg}}</h3>{% endif %}
</div>

{% else %}
<div class="card">
<h3>Connexion Joueur</h3>
<form method="POST" action="/login">
<input type="text" name="tel" placeholder="Ton numéro (ex: 0701234567)" required>
<button class="btn btn-blue" type="submit">Entrer & Jouer</button>
</form>
</div>
{% endif %}

<p><a href="/admin">Admin</a></p></body></html>
"""

HTML_ADMIN = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Admin Dépôts</title>
<style>body{font-family:Arial; padding:15px} .card{background:white; padding:15px; margin:10px 0; border-radius:10px; box-shadow:0 2px 5px #ddd} .btn{padding:10px; border:none; border-radius:8px; font-weight:bold; color:white; cursor:pointer} .btn-ok{background:green} .btn-no{background:red}</style>
</head><body>
<h1>ADMIN - Dépôts à valider</h1>
<h3>Gagnant actuel: {{config.numero_gagnant}} | Côte: x{{config.cote}} | <a href="/admin/random">🎲 Nouveau tirage</a></h3>
{% for d in depots %}
<div class="card">
<b>{{d.tel}}</b> veut {{d.montant}}F via {{d.operateur}} vers {{nums[d.operateur]}}<br>
ID: {{d.id_transaction}} | Date: {{d.date}} | <span class="badge bg-wait">{{d.statut}}</span>
{% if d.statut == 'attente' %}
<form method="POST" action="/admin/valider" style="display:inline">
<input type="hidden" name="index" value="{{loop.index0}}">
<button class="btn btn-ok" type="submit">✅ Valider (créditer solde)</button>
</form>
<form method="POST" action="/admin/refuser" style="display:inline">
<input type="hidden" name="index" value="{{loop.index0}}">
<button class="btn btn-no" type="submit">❌ Refuser</button>
</form>
{% endif %}
</div>
{% else %}
<p>Aucun dépôt</p>
{% endfor %}
<a href="/">Retour</a></body></html>
"""

def get_solde(tel):
    return users.get(tel, {}).get('solde', 0)

@app.route("/")
def home():
    tel = session.get('tel')
    solde = get_solde(tel) if tel else 0
    return render_template_string(HTML, user_tel=tel, solde=solde, config=config_jeu, nums=NUMEROS_PAIEMENT, msg=session.pop('msg', None))

@app.route("/login", methods=["POST"])
def login():
    tel = request.form['tel']
    session['tel'] = tel
    if tel not in users:
        users[tel] = {'solde': 0, 'nom': tel}
    return redirect("/")

@app.route("/logout")
def logout(): session.pop('tel', None); return redirect("/")

@app.route("/deposer", methods=["POST"])
def deposer():
    tel = session.get('tel')
    if not tel: return redirect("/")
    op = request.form['operateur']; montant = int(request.form['montant']); id_trx = request.form['id_transaction']
    if montant < 200: session['msg'] = "❌ Minimum 200F"; return redirect("/")
    depots_en_attente.append({'tel': tel, 'operateur': op, 'montant': montant, 'id_transaction': id_trx, 'statut': 'attente', 'date': time.strftime("%H:%M %d/%m")})
    session['msg'] = f"✅ Demande envoyée ! Transfère {montant}F sur {NUMEROS_PAIEMENT[op]} ({op}) puis attends validation."
    return redirect("/")

@app.route("/jouer", methods=["POST"])
def jouer():
    tel = session.get('tel')
    if not tel: return redirect("/")
    solde = get_solde(tel)
    choix = int(request.form['choix']); mise = int(request.form['mise'])
    if mise < 200 or mise > solde: session['msg'] = f"❌ Solde insuffisant ! Tu as {solde}F"; return redirect("/")
    gagnant = config_jeu['numero_gagnant']; cote = config_jeu['cote']
    users[tel]['solde'] -= mise
    if choix == gagnant:
        gain = mise * cote
        users[tel]['solde'] += gain
        msg = f"🎉 GAGNÉ ! {gagnant} = {choix} | Tu gagnes {gain}F ! Nouveau solde: {users[tel]['solde']}F"
        config_jeu['numero_gagnant'] = random.randint(1,100); config_jeu['cote'] = random.randint(2,10)
    else:
        msg = f"😭 Perdu {choix} != {gagnant}. Il te reste {users[tel]['solde']}F. Nouveau tirage !"
        config_jeu['numero_gagnant'] = random.randint(1,100); config_jeu['cote'] = random.randint(2,10)
    session['msg'] = msg
    return redirect("/")

@app.route("/admin")
def admin():
    return render_template_string(HTML_ADMIN, depots=depots_en_attente, config=config_jeu, nums=NUMEROS_PAIEMENT)

@app.route("/admin/random")
def admin_random():
    config_jeu['numero_gagnant'] = random.randint(1,100); config_jeu['cote'] = random.randint(2,10)
    return redirect("/admin")

@app.route("/admin/valider", methods=["POST"])
def valider():
    idx = int(request.form['index'])
    d = depots_en_attente[idx]
    tel = d['tel']
    if tel not in users: users[tel] = {'solde': 0}
    users[tel]['solde'] += d['montant']
    d['statut'] = 'validé'
    return redirect("/admin")

@app.route("/admin/refuser", methods=["POST"])
def refuser():
    idx = int(request.form['index'])
    depots_en_attente[idx]['statut'] = 'refusé'
    return redirect("/admin")

if __name__ == "__main__":
    app.run()
