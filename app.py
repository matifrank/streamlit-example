import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

# Cargar y preparar datos
df = pd.read_excel("career_milestones_english.xlsx")
df.columns = [col.strip() for col in df.columns]  # limpiar espacios

# Convertir a fechas año-mes
df["Inicio"] = pd.to_datetime(df["Inicio"], format="%Y-%m", errors="coerce")
df["Fin"] = pd.to_datetime(df["Fin"], format="%Y-%m", errors="coerce")
df = df.dropna(subset=["Inicio"])
df = df.sort_values("Inicio")

# -----------------------------
# Filtros
# -----------------------------

# Filtro por categoría
categorias = st.multiselect("Filtrar por categoría:", df["Categoría"].dropna().unique(), default=df["Categoría"].dropna().unique())

# Filtro por herramienta
todas_herramientas = sorted(set(sum(df['Herramientas'].dropna().str.split(", "), [])))
herramientas = st.multiselect("Filtrar por herramienta:", todas_herramientas)

# Aplicar filtros
df_filtrado = df[df["Categoría"].isin(categorias)]
if herramientas:
    df_filtrado = df_filtrado[df_filtrado["Herramientas"].apply(
        lambda x: any(h in x for h in herramientas) if pd.notna(x) else False
    )]

# -----------------------------
# Crear eventos para el timeline
# -----------------------------
events = []

for _, row in df_filtrado.iterrows():
    start = row["Inicio"]
    event = {
        "start_date": {
            "year": start.year,
            "month": start.month
        },
        "text": {
            "headline": f"{row['Rol']}",
            "text": f"""
                <b>Position:</b> {row['Proyecto o Hito']}<br>
                <b>Contexto:</b> {row['Desafío / Contexto']}<br>
                <b>Acción:</b> {row['Acción / Solución']}<br>
                <b>Impacto:</b> {row['Impacto / Resultado']}<br>
                <b>Herramientas:</b> {row['Herramientas']}
            """
        },
        "group": row.get("Categoría", "Otro")
    }
    if pd.notna(row["Fin"]):
        event["end_date"] = {
            "year": row["Fin"].year,
            "month": row["Fin"].month
        }
    events.append(event)

# -----------------------------
# Timeline base
# -----------------------------
timeline = {
    "title": {
        "text": {
            "headline": "🕒 Professional Timeline",
            "text": "Hitos principales de mi formación, experiencia y logros."
        }
    },
    "events": events
}

timeline_json = json.dumps(timeline)

# -----------------------------
# Mostrar en la app con CSS extra
# -----------------------------

components.html(
    f"""
    <style>
        /* Evitar que eventos tapen las etiquetas de categoría */
        .tl-timenav-category {{
            z-index: 1000 !important;
            background-color: white !important;
            position: relative !important;
        }}

        /* Centrar el contenido del slide */
        .tl-slide-content-container {{
            max-width: 800px !important;
            margin: 0 auto !important;
            z-index: 500 !important;
        }}

        .tl-slide {{
            padding-left: 0px !important;
            padding-right: 0px !important;
        }}
    </style>

    <div id="timeline-embed" style="width: 100%; height: 600px"></div>
    <script src="https://cdn.knightlab.com/libs/timeline3/latest/js/timeline.js"></script>
    <link href="https://cdn.knightlab.com/libs/timeline3/latest/css/timeline.css" rel="stylesheet" />
    <script type="text/javascript">
      var additionalOptions = {{
        initial_zoom: 2,
        timenav_position: "bottom"
      }};
      window.timeline = new TL.Timeline('timeline-embed', {timeline_json}, additionalOptions);
    </script>
    """,
    height=650
)

