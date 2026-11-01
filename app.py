from flask import Flask, render_template_string, request, session, redirect
import random, time

app = Flask(__name__)
app.secret_key = "abel_final_v3"

# TES NUMÉROS - C'EST LA CLÉ ADMIN
NUMEROS_PAIEMENT = {"WAVE": "0554762656", "MTN": "0554762656", "ORANGE": "0767911881"}
# Numéros qui débloquent l'espace créateur sur la même page
NUMEROS_CREATEUR = ["0554762656", "0767911881", "0554762656"] 

config_jeu = {"numero_gagnant": random.randint(1,100), "cote": random.randint(2,10), "mise_min": 200}
users = {}
depots_en_attente = []

HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Loto CI 1-100</title>
<style>
body{font-family:Arial; padding:12px; background:#f0f2f5}
.card{background:white; padding:14px; margin:10px 0; border-radius:12px; box-shadow:0 2px 5px #ddd}
.btn{padding:13px; border:none; border-radius:10px; width:100%; font-weight:bold; display:block; text-align:center; margin-top:8px; cursor:pointer; font-size:15px}
.btn-green{background:#25D366; color:white} .btn-blue{background:#007bff; color:white} .btn-ok{background:green; color:white; padding:8px 12px; width:auto; display:inline-block} .btn-no{background:red; color:white; padding:8px 12px; width:auto; display:inline-block}
input, select{width:100%; padding:11px; margin:6px 0; border-radius:8px; border:1px solid #ccc; box-sizing:border-box}
.admin-zone{background:#111; color:white; border:3px solid #FFD700; border-radius:12px; padding:14px; margin-bottom:15px}
.alert{padding:10px; border-radius:8px; margin:8px 0} .alert-green{background:#d4edda} .alert-red{background:#f8d7da}
</style></head><body>

{% if is_admin %}
<div class="admin-zone">
<h2 style="color:#FFD700; margin:0">👑 ESPACE CRÉATEUR (Toi seul vois ça)</h2>
<p>Gagnant actuel: <b style="color:#FFD700; font-size:20px">{{config.numero_gagnant}}</b> | Côte x{{config.cote}} | <a href="/random" style="color:yellow">🎲 Nouveau tirage</a></p>
<h3>💰 Dépôts à valider ({{depots|length}})</h3>
{% for d in depots if d.statut == 'attente' %}
<div style="background:#222; padding:10px; margin:8px 0; border-radius:8px; border-left:4px solid orange">
<b>{{d.tel}}</b> : {{d.montant}}F via {{d.operateur}} vers {{nums[d.operateur]}}<br>
ID: <code style="color:yellow">{{d.id_transaction}}</code> - {{d.date}}<br>
<form method="POST" action="/valider" style="display:inline"><input type="hidden" name="index" value="{{loop.index0}}"><button class="btn btn-ok" type="submit">✅ VALIDER + Créditer</button></form>
<form method="POST" action="/refuser" style="display:inline"><input type="hidden" name="index" value="{{loop.index0}}"><button class="btn btn-no" type="submit">❌ Refuser</button></form>
</div>
{% else %}
<p>Aucun dépôt en attente</p>
{% endfor %}
<hr style="border-color:#444">
<p style="font-size:11px; color:#aaa">Visible uniquement car tu es connecté avec {{user_tel}} (créateur)</p>
</div>
{% endif %}

<h2>🎰 LOTO CI 1-100</h2>

{% if user_tel %}
<div class="card" style="background:#e8f5e9; border:2px solid #25D366">
<b>{{user_tel}}</b> <a href="/logout" style="float:right; color:red">Quitter</a><br>
Solde: <span style="color:green; font-size:22px; font-weight:bold">{{solde}} F</span>
</div>

<div class="card">
<h3>💰 RECHARGER (Wave / MTN / Orange)</h3>
<form method="POST" action="/deposer">
<select name="operateur" required><option value="">-- Choisis --</option><option value="WAVE">WAVE -> {{nums.WAVE}}</option><option value="MTN">MTN -> {{nums.MTN}}</option><option value="ORANGE">ORANGE -> {{nums.ORANGE}}</option></select>
<input type="number" name="montant" placeholder="Montant min 200" min="200" required>
<input type="text" name="id_transaction" placeholder="ID transaction" required>
<button class="btn btn-green" type="submit">J'ai payé, confirmer</button>
</form>
</div>

<div class="card">
<h3>🎲 JOUER (1 à 100)</h3>
<p>Côte: x{{config.cote}} | Min: {{config.mise_min}}F</p>
<form method="POST" action="/jouer">
<input type="number" name="choix" placeholder="Numéro 1-100" min="1" max="100" required>
<input type="number" name="mise" placeholder="Mise max {{solde}}" min="200" max="{{solde}}" required>
<button class="btn btn-blue" type="submit">JOUER</button>
</form>
</div>

{% else %}
<div class="card">
<h3>Entrer pour jouer</h3>
<form method="POST" action="/login"><input type="text" name="tel" placeholder="Ton numéro" required><button class="btn btn-blue" type="submit">Entrer</button></form>
<p style="font-size:11px">Astuce: si tu entres {{nums.WAVE}} ou {{nums.ORANGE}}, tu verras l'espace créateur</p>
</div>
{% endif %}

{% if msg %}<div class="alert {% if 'GAGNÉ' in msg or 'envoyée' in msg or 'Validé' in msg %}alert-green{% else %}alert-red{% endif %}">{{msg}}</div>{% endif %}

</body></html>
"""

def get_solde(tel): return users.get(tel, {}).get('solde', 0)

@app.route("/")
def home():
    tel = session.get('tel')
    solde = get_solde(tel) if tel else 0
    # ICI C'EST LA SÉCURITÉ: seul toi vois l'admin
    is_admin = tel in NUMEROS_CREATEUR if tel else False
    return render_template_string(HTML, user_tel=tel, solde=solde, config=config_jeu, nums=NUMEROS_PAIEMENT, msg=session.pop('msg', None), is_admin=is_admin, depots=depots_en_attente)

@app.route("/login", methods=["POST"])
def login():
    tel = request.form['tel'].strip()
    session['tel'] = tel
    if tel not in users: users[tel] = {'solde': 0}
    if tel in NUMEROS_CREATEUR:
        session['msg'] = f"👑 Bienvenue Créateur {tel} ! Espace admin activé"
    else:
        session['msg'] = f"Bienvenue {tel} !"
    return redirect("/")

@app.route("/logout")
def logout(): session.pop('tel', None); return redirect("/")

@app.route("/deposer", methods=["POST"])
def deposer():
    tel = session.get('tel')
    if not tel: return redirect("/")
    op = request.form['operateur']; montant = int(request.form['montant']); id_trx = request.form['id_transaction'].strip()
    depots_en_attente.append({'tel': tel, 'operateur': op, 'montant': montant, 'id_transaction': id_trx, 'statut': 'attente', 'date': time.strftime("%H:%M %d/%m")})
    session['msg'] = f"✅ Demande {montant}F via {op} envoyée sur {NUMEROS_PAIEMENT[op]} ! En attente du créateur."
    return redirect("/")

@app.route("/jouer", methods=["POST"])
def jouer():
    tel = session.get('tel')
    if not tel: return redirect("/")
    solde = get_solde(tel)
    choix = int(request.form['choix']); mise = int(request.form['mise'])
    if mise > solde or mise < 200: session['msg'] = f"❌ Solde insuffisant {solde}F"; return redirect("/")
    gagnant = config_jeu['numero_gagnant']; cote = config_jeu['cote']
    users[tel]['solde'] -= mise
    if choix == gagnant:
        gain = mise * cote
        users[tel]['solde'] += gain
        session['msg'] = f"🎉 GAGNÉ ! {gagnant} == {choix} | +{gain}F ! Solde {users[tel]['solde']}F"
        config_jeu['numero_gagnant'] = random.randint(1,100); config_jeu['cote'] = random.randint(2,10)
    else:
        session['msg'] = f"Perdu {choix} != {gagnant} | Reste {users[tel]['solde']}F"
        config_jeu['numero_gagnant'] = random.randint(1,100); config_jeu['cote'] = random.randint(2,10)
    return redirect("/")

@app.route("/valider", methods=["POST"])
def valider():
    tel = session.get('tel')
    if tel not in NUMEROS_CREATEUR: return redirect("/") # Sécurité: seul créateur peut valider
    idx = int(request.form['index'])
    d = depots_en_attente[idx]
    if d['statut'] == 'attente':
        if d['tel'] not in users: users[d['tel']] = {'solde': 0}
        users[d['tel']]['solde'] += d['montant']
        d['statut'] = 'validé'
        session['msg'] = f"Validé {d['montant']}F pour {d['tel']}"
    return redirect("/")

@app.route("/refuser", methods=["POST"])
def refuser():
    tel = session.get('tel')
    if tel not in NUMEROS_CREATEUR: return redirect("/")
    idx = int(request.form['index'])
    depots_en_attente[idx]['statut'] = 'refusé'
    return redirect("/")

@app.route("/random")
def random_new():
    tel = session.get('tel')
    if tel not in NUMEROS_CREATEUR: return redirect("/")
    config_jeu['numero_gagnant'] = random.randint(1,100); config_jeu['cote'] = random.randint(2,10)
    return redirect("/")

if __name__ == "__main__":
    app.run()
