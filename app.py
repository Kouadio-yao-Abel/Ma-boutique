from flask import Flask, request, render_template_string
import urllib.parse
import os

app = Flask(__name__)

# CONFIG BOSS - change ici
NUMERO_GAGNANT = 7
COTE_DU_JOUR = 5.75

produits = {"chaussure": [5000, 8000, 10], "sac": [3000, 5500, 5]}
benefice_total = 0

HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:sans-serif;background:#f0f0f0;padding:15px}.box{background:white;padding:20px;border-radius:15px;margin-bottom:20px}input,button{width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #ccc}button{background:#25D366;color:white;font-weight:bold;border:none}.gagne{background:#d4edda;padding:15px;border-radius:10px}.perdu{background:#f8d7da;padding:15px;border-radius:10px}</style>
</head><body>
<div class="box"><h2>🎰 LOTO - Cote {{cote}}</h2><form method="post" action="/loto"><input type="number" name="mise" placeholder="Mise FCFA" required><input type="number" name="numero" placeholder="Numéro 1-100" required><button>JOUER</button></form>{% if loto %}<div class="{{cl}}">{{loto}}</div>{% endif %}</div>
<div class="box"><h2>🛍️ BOUTIQUE</h2><p>Stock: {% for k,v in produits.items() %}{{k}}({{v[2]}}) {% endfor %} | Bénéf: {{benef}} FCFA</p><form method="post" action="/vendre"><input type="text" name="client" placeholder="Nom client" required><input type="text" name="tel" placeholder="2250..." required><input type="text" name="prod" placeholder="Produit" required><input type="number" name="qte" placeholder="Qté" required><button>VENDRE + WHATSAPP</button></form>{% if recu %}<div class="gagne">{{recu}}<br><br><a href="{{lien}}" target="_blank"><button>OUVRIR WHATSAPP</button></a></div>{% endif %}</div>
</body></html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, cote=COTE_DU_JOUR, produits=produits, benef=benefice_total, loto=None, recu=None)

@app.route("/loto", methods=["POST"])
def loto():
    mise=int(request.form["mise"]); num=int(request.form["numero"])
    if num==NUMERO_GAGNANT:
        gain=int(mise*COTE_DU_JOUR)
        msg=f"🎉 GAGNÉ ! C'était {NUMERO_GAGNANT}. Tu gagnes {gain} FCFA"
        cl="gagne"
    else:
        msg=f"😭 Perdu ! C'était {NUMERO_GAGNANT}"; cl="perdu"
    return render_template_string(HTML, cote=COTE_DU_JOUR, produits=produits, benef=benefice_total, loto=msg, cl=cl, recu=None)

@app.route("/vendre", methods=["POST"])
def vendre():
    global benefice_total
    client=request.form["client"]; tel=request.form["tel"]; prod=request.form["prod"].lower(); qte=int(request.form["qte"])
    if prod not in produits or produits[prod][2]<qte:
        return render_template_string(HTML, cote=COTE_DU_JOUR, produits=produits, benef=benefice_total, loto=None, recu="Stock insuffisant", lien="#")
    pa,pv,st=produits[prod]; total=pv*qte; benef=(pv-pa)*qte; produits[prod][2]-=qte; benefice_total+=benef
    recu_txt=f"🧾 REÇU\nClient:{client}\nProduit:{prod} x{qte}\nTOTAL:{total} FCFA\nMerci!"
    lien=f"https://wa.me/{tel}?text={urllib.parse.quote(recu_txt)}"
    return render_template_string(HTML, cote=COTE_DU_JOUR, produits=produits, benef=benefice_total, loto=None, recu=recu_txt, lien=lien)

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
