import math

import pandas as pd
import streamlit as st

MGDL_POR_MMOL = 38.67  # colesterol: 1 mmol/L = 38.67 mg/dL

# Ecuaciones PREVENT (modelo base, 10 años, sin raza). Orden de los coeficientes:
KEYS = "c a nh h pmin pmax emin emax d s t e tp enh anh ah ap ae da sa".split()
COEF = {  # (riesgo, sexo) -> coeficientes en el orden de KEYS
    ("ascvd", "Mujer"): (-3.819975, 0.719883, 0.1176967, -0.151185, -0.0835358, 0.3592852, 0.4864619, 0.0397779,
                         0.8348585, 0.4831078, 0.2265309, -0.0592374, -0.0395762, 0.0844423, -0.0567839, 0.0325692,
                         -0.1035985, -0.1671492, -0.2417542, -0.0791142),
    ("ascvd", "Hombre"): (-3.500655, 0.7099847, 0.1658663, -0.1144285, -0.2837212, 0.3239977, 0.3690075, 0.0203619,
                          0.7189597, 0.3956973, 0.2036522, -0.0865581, -0.0322916, 0.114563, -0.0300005, 0.0232747,
                          -0.0927024, -0.1217081, -0.2018525, -0.0970527),
    ("cvd", "Mujer"): (-3.307728, 0.7939329, 0.0305239, -0.1606857, -0.2394003, 0.3600781, 0.6045917, 0.0433769,
                       0.8667604, 0.5360739, 0.3151672, -0.1477655, -0.0663612, 0.1197879, -0.0819715, 0.0306769,
                       -0.0946348, -0.1637806, -0.27057, -0.078715),
    ("cvd", "Hombre"): (-3.031168, 0.7688528, 0.0736174, -0.0954431, -0.4347345, 0.3362658, 0.5378979, 0.0164827,
                        0.7692857, 0.4386871, 0.288879, -0.1337349, -0.0475924, 0.150273, -0.0517874, 0.0191169,
                        -0.1049477, -0.1543702, -0.2251948, -0.0895067),
}
RANGOS = {"edad": (30, 79), "ct": (130, 320), "hdl": (20, 100), "pas": (90, 200), "egfr": (15, 140)}  # mg/dL, mmHg


def riesgo(tipo, sexo, edad, ct, hdl, pas, egfr, diabetes, fuma, htn, estatina):
    """Riesgo a 10 años en % (colesterol en mg/dL)."""
    k = dict(zip(KEYS, COEF[(tipo, sexo)]))
    a = (edad - 55) / 10
    nh = 0.02586 * (ct - hdl) - 3.5
    h = (0.02586 * hdl - 1.3) / 0.3
    pmin, pmax = (min(pas, 110) - 110) / 20, (max(pas, 110) - 130) / 20
    emin, emax = (min(egfr, 60) - 60) / -15, (max(egfr, 60) - 90) / -15
    x = (k["c"] + k["a"] * a + k["nh"] * nh + k["h"] * h + k["pmin"] * pmin + k["pmax"] * pmax
         + k["emin"] * emin + k["emax"] * emax
         + diabetes * (k["d"] + k["da"] * a) + fuma * (k["s"] + k["sa"] * a)
         + htn * (k["t"] + k["tp"] * pmax) + estatina * (k["e"] + k["enh"] * nh)
         + a * (k["anh"] * nh + k["ah"] * h + k["ap"] * pmax + k["ae"] * emin))
    return 100 / (1 + math.exp(-x))


def errores(edad, ct, hdl, pas, egfr):
    """Valida entradas (colesterol en mg/dL); devuelve lista de mensajes."""
    e = [f"{n} fuera de rango ({lo}–{hi})." for n, v, (lo, hi) in
         [("Edad", edad, RANGOS["edad"]), ("Colesterol total", ct, RANGOS["ct"]), ("HDL", hdl, RANGOS["hdl"]),
          ("Presión sistólica", pas, RANGOS["pas"]), ("eGFR", egfr, RANGOS["egfr"])] if not lo <= v <= hi]
    if hdl >= ct:
        e.append("El HDL debe ser menor que el colesterol total.")
    return e


# Autocomprobación con el caso de ejemplo del paquete de referencia preventr:
# mujer 50 años, CT 200, HDL 45, PAS 160, diabetes, tratada para HTA, IMC 35, eGFR 90 -> ASCVD 9.2 %, ECV total 14.7 %.
_caso = ("Mujer", 50, 200, 45, 160, 90, 1, 0, 1, 0)
assert abs(riesgo("ascvd", *_caso) - 9.2) < 0.15 and abs(riesgo("cvd", *_caso) - 14.7) < 0.15

st.set_page_config(page_title="Riesgo cardiovascular", page_icon="❤️")
st.markdown("### ❤️ Riesgo cardiovascular a 10 años")
st.caption("Ecuaciones PREVENT de la AHA (2024). Solo educativo; no reemplaza la evaluación médica.")

c = st.columns(4)
mmol = c[0].radio("Colesterol en", ["mg/dL", "mmol/L"]) == "mmol/L"
sexo = c[1].radio("Sexo", ["Hombre", "Mujer"])
edad = c[2].number_input("Edad", 0, 120, 55)
egfr = c[3].number_input("eGFR", 0, 200, 90, help="Función renal (mL/min/1.73 m²), sale de la creatinina. Normal: ≥90.")
f, u = (MGDL_POR_MMOL, "mmol/L") if mmol else (1, "mg/dL")
c = st.columns(3)
ct = c[0].number_input(f"Col. total ({u})", 0.0, 500.0, 5.2 if mmol else 200.0, 0.1 if mmol else 1.0) * f
hdl = c[1].number_input(f"HDL ({u})", 0.0, 200.0, 1.3 if mmol else 50.0, 0.1 if mmol else 1.0) * f
pas = c[2].number_input("Presión sistólica (mmHg)", 0, 300, 120)
c = st.columns(4)
htn = c[0].checkbox("Trata HTA")
estatina = c[1].checkbox("Estatinas")
fuma = c[2].checkbox("Fuma")
diabetes = c[3].checkbox("Diabetes")

if err := errores(edad, ct, hdl, pas, egfr):
    for m in err:
        st.error(m + (" (Rangos de colesterol en mg/dL; 1 mmol/L = 38.67 mg/dL.)" if mmol and ("HDL" in m or "olesterol" in m) else ""))
    st.stop()


def r(tipo="ascvd", **cambios):
    p = dict(edad=edad, ct=ct, hdl=hdl, pas=pas, egfr=egfr, diabetes=diabetes, fuma=fuma, htn=htn,
             estatina=estatina) | cambios
    return riesgo(tipo, sexo, **p)


ascvd, cvd = r(), r("cvd")
nivel = "Bajo" if ascvd < 5 else "Limítrofe" if ascvd < 7.5 else "Intermedio" if ascvd < 20 else "Alto"
c1, c2 = st.columns(2)
c1.metric("Infarto o ACV", f"{ascvd:.1f} %", nivel, delta_color="off",
          help="<5 % bajo, 5–7.4 % limítrofe, 7.5–19.9 % intermedio, ≥20 % alto: cortes ACC/AHA 2018, no validados formalmente para PREVENT.")
c2.metric("Enfermedad cardiovascular total", f"{cvd:.1f} %", help="Incluye además insuficiencia cardiaca.")

# ¿Qué podría cambiar el riesgo? Se recalcula el modelo con un factor modificado.
esc = {"Actual": ascvd}
cambios = {}
if fuma:
    cambios["Dejar de fumar"] = {"fuma": False}
if pas > 120:
    cambios["Presión a 120"] = {"pas": 120}
if ct - 40 > max(hdl, RANGOS["ct"][0]):
    cambios["Col. total −40 mg/dL"] = {"ct": ct - 40}
for n, cb in cambios.items():
    esc[n] = r(**cb)
if len(cambios) > 1:
    esc["Todos"] = r(**{k: v for cb in cambios.values() for k, v in cb.items()})
if cambios:
    st.bar_chart(pd.DataFrame({"Riesgo de infarto o ACV a 10 años (%)": esc}), horizontal=True, height=40 + 35 * len(esc))
    st.caption("Simulación con el mismo modelo; no garantiza esa reducción.")

with st.expander("Fuentes"):
    st.markdown(
        "- Khan SS et al. *Development and Validation of the American Heart Association's PREVENT Equations.* "
        "Circulation 2024;149:430–449. [doi:10.1161/CIRCULATIONAHA.123.067626]"
        "(https://doi.org/10.1161/CIRCULATIONAHA.123.067626)\n"
        "- [Calculadora PREVENT de la AHA]"
        "(https://professional.heart.org/en/guidelines-and-statements/prevent-calculator)\n"
        "- Coeficientes tomados de la implementación abierta [PyPREVENT]"
        "(https://github.com/lhegstrom/PyPREVENT) (`src/covariates.rs`, `src/utils.rs`); caso de verificación del "
        "paquete R [preventr](https://github.com/martingmayer/preventr).\n"
        "- Categorías de riesgo: Grundy SM et al. 2018 AHA/ACC Cholesterol Guideline. "
        "[doi:10.1161/CIR.0000000000000625](https://doi.org/10.1161/CIR.0000000000000625)"
    )
