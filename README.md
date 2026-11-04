# Calculadora de riesgo cardiovascular

App de Streamlit que estima el riesgo a 10 años de infarto o ACV (ASCVD) y de enfermedad cardiovascular total con las ecuaciones **PREVENT** de la AHA (2024, modelo base, sin raza, edades 30–79).

> Herramienta educativa. No reemplaza la evaluación médica.

## Uso

```bash
uv run streamlit run streamlit_app.py
```

Requiere [uv](https://docs.astral.sh/uv/). Las dependencias se instalan solas desde `pyproject.toml` y `uv.lock`.

## Qué incluye

- Colesterol en mg/dL o mmol/L.
- Validación de rangos y de HDL < colesterol total.
- Simulación de cambios (dejar de fumar, presión a 120, colesterol −40 mg/dL).
- Al iniciar, una autocomprobación (`assert`) contra un caso de referencia: mujer de 50 años, colesterol total 200, HDL 45, presión 160, diabetes, tratada para hipertensión, eGFR 90 → 9,2 % ASCVD y 14,7 % total.

## Desarrollo

```bash
uv run ruff check .
uv run ruff format .
```

## Límites

- Las categorías de riesgo (<5 %, 5–7,4 %, 7,5–19,9 %, ≥20 %) son de la guía ACC/AHA 2018 y no están validadas formalmente para PREVENT.
- El caso de verificación es uno solo; los coeficientes se transcribieron de una implementación abierta, no de la tabla suplementaria del artículo.

## Fuentes

- Khan SS et al. *Development and Validation of the American Heart Association's PREVENT Equations.* Circulation 2024;149:430–449. [doi:10.1161/CIRCULATIONAHA.123.067626](https://doi.org/10.1161/CIRCULATIONAHA.123.067626)
- [Calculadora PREVENT de la AHA](https://professional.heart.org/en/guidelines-and-statements/prevent-calculator)
- Coeficientes: [PyPREVENT](https://github.com/lhegstrom/PyPREVENT) (`src/covariates.rs`, `src/utils.rs`); caso de verificación: paquete R [preventr](https://github.com/martingmayer/preventr).
- Categorías: Grundy SM et al. 2018 AHA/ACC Cholesterol Guideline. [doi:10.1161/CIR.0000000000000625](https://doi.org/10.1161/CIR.0000000000000625)
