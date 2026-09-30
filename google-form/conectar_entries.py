"""Lee el Google Form publicado y escribe los entry.NNN en GOOGLE_FORM de la encuesta HTML."""
import json
import re
import sys
import urllib.request
from pathlib import Path

FORM_ID = "1FAIpQLScFWX3PGl65jvlJfJWATB-rYvHJzBHx3OvCLZdTb2CrSjAmRQ"
HTML = Path(__file__).resolve().parent.parent / "index.html"

TITULOS = {
    "Taller": "taller", "Fecha": "fecha", "Sede del taller": "sede", "Encuestador": "encuestador",
    "Sector": "sector", "Ocupación o rol": "rol", "Dónde vive": "zona",
    "Corregimiento, vereda o municipio": "residencia", "Edad": "edad", "Se identifica como": "genero",
    "Nombre": "nombre", "Teléfono": "telefono", "Autoriza datos": "autorizaDatos",
    "Metodología y actividades": "metodologia", "Trabajo del equipo facilitador": "facilitacion",
    "Claridad de la información": "informacion", "Oportunidad de participar y ser escuchado": "participacion",
    "Lugar, refrigerio y logística": "logistica", "Horario y duración": "horario",
    "Utilidad para el plan de turismo": "utilidad", "Satisfacción general con el taller": "general",
    "Recomendaría participar": "recomienda", "Qué fue lo que más le gustó": "gusto",
    "Qué deberíamos mejorar": "mejorar", "Necesidades del turismo": "necesidad", "Idea o proyecto": "idea",
}
OPCIONALES = {"Consentimiento informado": "consentimiento"}
ATR = {
    "Nombre": "nombre", "Tipo": "tipo", "Ubicación": "zona", "Corregimiento o vereda": "lugar",
    "Cómo se llega": "acceso", "Estado actual": "estado", "Recibe visitantes": "visitantes",
    "Por qué lo recomendaría": "porque", "Es el más representativo": "representativo",
}


def leer_form():
    url = f"https://docs.google.com/forms/d/e/{FORM_ID}/viewform"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    data = json.loads(re.search(r"FB_PUBLIC_LOAD_DATA_ = (.*?);</script>", html, re.S).group(1))
    return [(it[1], it[4][0][0]) for it in (data[1][1] or []) if it[4]]


def main():
    base, atr = {}, [{} for _ in range(5)]
    for titulo, eid in leer_form():
        titulo = titulo.strip()
        m = re.match(r"Atractivo ([1-5]) · (.+)$", titulo)
        if m and m.group(2) in ATR:
            atr[int(m.group(1)) - 1][ATR[m.group(2)]] = f"entry.{eid}"
        elif titulo in TITULOS:
            base[TITULOS[titulo]] = f"entry.{eid}"
        elif titulo in OPCIONALES:
            base[OPCIONALES[titulo]] = f"entry.{eid}"

    faltan = [k for k in TITULOS.values() if k not in base]
    faltan += [f"atractivo{i + 1}.{k}" for i, a in enumerate(atr) for k in ATR.values() if k not in a]
    if faltan:
        print("Faltan preguntas en el formulario:", ", ".join(faltan))
        sys.exit(1)

    s = HTML.read_text(encoding="utf-8")
    for k, v in base.items():
        s, n = re.subn(rf'(\b{k}:)"[^"]*"', rf'\1"{v}"', s, count=1)
        assert n == 1, k
    atr_js = json.dumps(atr, ensure_ascii=False)
    s, n = re.subn(r"atractivos: (?:Array\.from\(\{length:5\}, \(\)=>Object\.fromEntries\(ATR_FIELDS\.map\(k=>\[k,\"\"\]\)\)\)|\[\{.*?\}\])",
                   lambda _: "atractivos: " + atr_js, s, count=1, flags=re.S)
    assert n == 1, "atractivos"
    HTML.write_text(s, encoding="utf-8")
    print(f"Conectadas {len(base)} preguntas y 5 bloques de atractivos.")


if __name__ == "__main__":
    main()
