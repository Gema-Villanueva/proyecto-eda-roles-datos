from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:  # pragma: no cover - Streamlit shows a friendly setup message.
    px = None
    go = None


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_EDA = PROJECT_ROOT / "data" / "eda"
DATA_CLEAN = PROJECT_ROOT / "data" / "clean"


st.set_page_config(
    page_title="DataTalent - EDA interactivo",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def read_first_available(*paths: Path) -> pd.DataFrame:
    """Load the first CSV that exists from an ordered list of candidates."""
    for path in paths:
        if path.exists():
            return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, pd.DataFrame]:
    jobs = read_first_available(DATA_EDA / "jobs_eda.csv", DATA_CLEAN / "jobs_all_clean.csv")

    skills = read_first_available(DATA_CLEAN / "job_skills_long.csv")
    if skills.empty and "skills" in jobs.columns:
        skills = explode_skills_from_jobs(jobs)

    rankings = read_first_available(
        DATA_EDA / "technology_rankings_eda.csv",
        DATA_CLEAN / "technology_rankings.csv",
    )
    used = read_first_available(
        DATA_EDA / "technology_rankings_used_eda.csv",
        DATA_CLEAN / "technology_rankings_used.csv",
    )
    wanted = read_first_available(
        DATA_EDA / "technology_rankings_wanted_eda.csv",
        DATA_CLEAN / "technology_rankings_wanted.csv",
    )
    validation = read_first_available(
        DATA_EDA / "cleaning_validation_summary_eda.csv",
        DATA_CLEAN / "cleaning_validation_summary.csv",
    )

    return {
        "jobs": prepare_jobs(jobs),
        "skills": prepare_skills(skills),
        "rankings": rankings,
        "used": used,
        "wanted": wanted,
        "validation": validation,
    }


def explode_skills_from_jobs(jobs: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for _, row in jobs.iterrows():
        raw_skills = row.get("skills", [])
        if isinstance(raw_skills, str):
            try:
                parsed = ast.literal_eval(raw_skills)
            except (ValueError, SyntaxError):
                parsed = [part.strip() for part in raw_skills.split(",")]
        else:
            parsed = raw_skills

        for skill in parsed or []:
            skill_text = str(skill).strip().lower()
            if skill_text:
                rows.append(
                    {
                        "job_id": row.get("job_id"),
                        "job_title": row.get("job_title"),
                        "source_dataset": row.get("source_dataset"),
                        "skill": skill_text,
                    }
                )
    return pd.DataFrame(rows)


def prepare_jobs(jobs: pd.DataFrame) -> pd.DataFrame:
    if jobs.empty:
        return jobs

    prepared = jobs.copy()
    prepared["salary_clean"] = pd.to_numeric(prepared.get("salary_clean"), errors="coerce")
    prepared["salary_clean_outlier"] = (
        prepared["salary_clean_outlier"].fillna(False).astype(bool)
        if "salary_clean_outlier" in prepared.columns
        else False
    )
    prepared["is_remote"] = (
        prepared["is_remote"].fillna(False).astype(bool) if "is_remote" in prepared.columns else False
    )

    if "job_family" not in prepared.columns:
        prepared["job_family"] = prepared["job_title"].fillna("unknown").map(classify_job_family)
    if "work_modality" not in prepared.columns:
        prepared["work_modality"] = prepared.apply(classify_work_modality, axis=1)

    for column in ["seniority_level", "industry", "city_clean", "source_dataset"]:
        prepared[column] = (
            prepared[column].fillna("Sin informar") if column in prepared.columns else "Sin informar"
        )
    prepared["skills_count"] = prepared.get("skills", "").map(count_skills)
    prepared["salary_available"] = prepared["salary_clean"].notna()
    return prepared


def prepare_skills(skills: pd.DataFrame) -> pd.DataFrame:
    if skills.empty:
        return skills
    prepared = skills.copy()
    prepared["skill"] = prepared["skill"].astype(str).str.strip().str.lower()
    prepared = prepared[prepared["skill"].ne("")]
    return prepared


def classify_job_family(title: object) -> str:
    text = str(title).lower()
    if any(token in text for token in ["scientist", "machine learning", "ai", "ml"]):
        return "data_science_ai"
    if any(token in text for token in ["engineer", "etl", "pipeline", "architect"]):
        return "data_engineering"
    if any(token in text for token in ["analyst", "business intelligence", "bi"]):
        return "data_analytics_bi"
    return "other_data_roles"


def classify_work_modality(row: pd.Series) -> str:
    text = f"{row.get('location', '')} {row.get('location_clean', '')}".lower()
    if "remote" in text:
        return "remote"
    if "hybrid" in text:
        return "hybrid"
    if "on-site" in text or "onsite" in text:
        return "onsite"
    return "unknown"


def count_skills(raw_skills: object) -> int:
    if isinstance(raw_skills, list):
        return len(raw_skills)
    if pd.isna(raw_skills):
        return 0
    text = str(raw_skills)
    try:
        parsed = ast.literal_eval(text)
        return len(parsed) if isinstance(parsed, list) else 0
    except (ValueError, SyntaxError):
        return 0 if not text.strip() else len([part for part in text.split(",") if part.strip()])


def format_eur(value: float | int | None) -> str:
    if pd.isna(value):
        return "Sin datos"
    return f"{value:,.0f} €".replace(",", ".")


def top_values(df: pd.DataFrame, column: str, limit: int) -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return pd.DataFrame(columns=[column, "ofertas"])
    return (
        df[column]
        .fillna("Sin informar")
        .value_counts()
        .head(limit)
        .rename_axis(column)
        .reset_index(name="ofertas")
    )


def render_empty_state(message: str) -> None:
    st.warning(message)
    st.stop()


def ensure_plotly() -> None:
    if px is None or go is None:
        st.error("Falta Plotly. Instala las dependencias con `pip install -r requirements.txt`.")
        st.stop()


data = load_data()
jobs = data["jobs"]
skills = data["skills"]
rankings = data["rankings"]
used = data["used"]
wanted = data["wanted"]
validation = data["validation"]

ensure_plotly()

if jobs.empty:
    render_empty_state("No se ha encontrado el dataset de ofertas en `data/eda` ni en `data/clean`.")

st.title("EDA interactivo del mercado laboral de datos")
st.caption(
    "Dashboard para DataTalent Solutions S.L.: skills demandadas, salarios, sectores, calidad de datos y sesgos."
)

with st.sidebar:
    st.header("Filtros")
    exclude_outliers = st.checkbox("Excluir outliers salariales", value=True)

    working = jobs.copy()
    if exclude_outliers and "salary_clean_outlier" in working.columns:
        working = working[~working["salary_clean_outlier"]]

    salary_series = working["salary_clean"].dropna()
    if salary_series.empty:
        salary_range = (0, 0)
    else:
        salary_min = int(salary_series.min())
        salary_max = int(salary_series.max())
        salary_range = st.slider(
            "Rango salarial anual",
            min_value=salary_min,
            max_value=salary_max,
            value=(salary_min, salary_max),
            step=1000,
            format="%d €",
        )

    def multiselect_filter(label: str, column: str, limit: int = 80) -> list[str]:
        values = sorted(working[column].dropna().astype(str).unique().tolist())[:limit]
        return st.multiselect(label, values, default=[])

    selected_family = multiselect_filter("Familia de rol", "job_family")
    selected_seniority = multiselect_filter("Seniority", "seniority_level")
    selected_industry = multiselect_filter("Sector", "industry")
    selected_modality = multiselect_filter("Modalidad", "work_modality")
    selected_source = multiselect_filter("Fuente", "source_dataset")

    top_city_options = (
        working["city_clean"].fillna("Sin informar").value_counts().head(40).index.astype(str).tolist()
    )
    selected_city = st.multiselect("Ciudad", top_city_options, default=[])

    top_n = st.slider("Top N en rankings", min_value=5, max_value=30, value=12)


filtered = working.copy()
if salary_range != (0, 0):
    filtered = filtered[
        filtered["salary_clean"].isna()
        | filtered["salary_clean"].between(salary_range[0], salary_range[1])
    ]

for column, selected in {
    "job_family": selected_family,
    "seniority_level": selected_seniority,
    "industry": selected_industry,
    "work_modality": selected_modality,
    "source_dataset": selected_source,
    "city_clean": selected_city,
}.items():
    if selected:
        filtered = filtered[filtered[column].astype(str).isin(selected)]

filtered_skills = skills
if not skills.empty and "job_id" in skills.columns:
    filtered_skills = skills[skills["job_id"].isin(filtered["job_id"])]

salary_filtered = filtered["salary_clean"].dropna()

metric_cols = st.columns(5)
metric_cols[0].metric("Ofertas", f"{len(filtered):,}".replace(",", "."))
metric_cols[1].metric("Salario mediano", format_eur(salary_filtered.median()))
metric_cols[2].metric("Salario medio", format_eur(salary_filtered.mean()))
metric_cols[3].metric("Skills unicas", f"{filtered_skills['skill'].nunique() if not filtered_skills.empty else 0}")
metric_cols[4].metric("% salario informado", f"{filtered['salary_available'].mean() * 100:.1f}%")

st.divider()

tab_market, tab_skills, tab_bias, tab_quality, tab_actions = st.tabs(
    [
        "Mercado laboral",
        "Skills y tecnologias",
        "Salarios y sesgos",
        "Calidad de datos",
        "Recomendaciones",
    ]
)

with tab_market:
    st.subheader("Volumen de ofertas")
    left, right = st.columns(2)

    with left:
        family_counts = top_values(filtered, "job_family", top_n)
        fig = px.bar(
            family_counts,
            x="ofertas",
            y="job_family",
            orientation="h",
            title="Ofertas por familia de rol",
            labels={"ofertas": "Numero de ofertas", "job_family": "Familia de rol"},
            color="ofertas",
            color_continuous_scale="Teal",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            "Lectura de negocio: las familias con mayor volumen deben guiar el diseno del catalogo de reskilling."
        )

    with right:
        city_counts = top_values(filtered, "city_clean", top_n)
        fig = px.bar(
            city_counts,
            x="ofertas",
            y="city_clean",
            orientation="h",
            title="Ciudades con mas ofertas",
            labels={"ofertas": "Numero de ofertas", "city_clean": "Ciudad"},
            color="ofertas",
            color_continuous_scale="Viridis",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            "Lectura de negocio: la concentracion geografica condiciona donde priorizar alianzas, bootcamps y captacion."
        )

    sector_salary = (
        filtered.dropna(subset=["salary_clean"])
        .groupby("industry", as_index=False)
        .agg(ofertas=("job_id", "count"), salario_mediano=("salary_clean", "median"))
        .sort_values("salario_mediano", ascending=False)
        .head(top_n)
    )
    fig = px.scatter(
        sector_salary,
        x="ofertas",
        y="salario_mediano",
        size="ofertas",
        color="industry",
        title="Sectores: volumen vs salario mediano",
        labels={
            "ofertas": "Ofertas con salario",
            "salario_mediano": "Salario mediano",
            "industry": "Sector",
        },
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_skills:
    st.subheader("Skills y tecnologias demandadas")
    left, right = st.columns(2)

    with left:
        if filtered_skills.empty:
            st.warning("No hay datos de skills para el filtro seleccionado.")
        else:
            skill_counts = (
                filtered_skills["skill"]
                .value_counts()
                .head(top_n)
                .rename_axis("skill")
                .reset_index(name="ofertas")
            )
            fig = px.bar(
                skill_counts,
                x="ofertas",
                y="skill",
                orientation="h",
                title="Skills mas frecuentes en ofertas",
                labels={"ofertas": "Apariciones", "skill": "Skill"},
                color="ofertas",
                color_continuous_scale="Cividis",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            st.info(
                "Lectura de negocio: estas skills son candidatas naturales para itinerarios base y pruebas tecnicas."
            )

    with right:
        tech_source = rankings if not rankings.empty else pd.concat([used, wanted], ignore_index=True)
        if tech_source.empty:
            st.warning("No hay rankings tecnologicos disponibles.")
        else:
            category_options = sorted(tech_source["category"].dropna().unique().tolist())
            selected_category = st.selectbox("Categoria tecnologica", category_options)
            selected_type = st.radio("Tipo", sorted(tech_source["type"].dropna().unique().tolist()), horizontal=True)
            tech_filtered = tech_source[
                (tech_source["category"] == selected_category) & (tech_source["type"] == selected_type)
            ].nlargest(top_n, "count")
            fig = px.bar(
                tech_filtered,
                x="count",
                y="technology",
                orientation="h",
                title=f"Tecnologias {selected_type}: {selected_category}",
                labels={"count": "Respuestas", "technology": "Tecnologia"},
                color="count",
                color_continuous_scale="Magma",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            st.info(
                "Lectura de negocio: comparar uso actual y deseo futuro ayuda a separar demanda consolidada de tendencia emergente."
            )

    if not used.empty and not wanted.empty:
        gap = used.merge(
            wanted,
            on=["category", "technology"],
            suffixes=("_used", "_wanted"),
            how="inner",
        )
        gap["gap_wanted_minus_used"] = gap["count_wanted"] - gap["count_used"]
        gap_view = gap.reindex(gap["gap_wanted_minus_used"].abs().sort_values(ascending=False).index).head(top_n)
        fig = px.bar(
            gap_view,
            x="gap_wanted_minus_used",
            y="technology",
            color="category",
            orientation="h",
            title="Brecha entre tecnologias deseadas y usadas",
            labels={"gap_wanted_minus_used": "Wanted - Used", "technology": "Tecnologia"},
        )
        fig.add_vline(x=0, line_width=1, line_color="gray")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Skills con alta demanda y buen salario")
    required_columns = {"job_id", "skill"}
    if filtered_skills.empty or not required_columns.issubset(filtered_skills.columns):
        st.warning("No hay datos suficientes de skills para cruzarlas con salarios.")
    else:
        skill_salary_base = (
            filtered_skills[["job_id", "skill"]]
            .drop_duplicates()
            .merge(filtered[["job_id", "salary_clean"]], on="job_id", how="inner")
            .dropna(subset=["salary_clean"])
        )

        if skill_salary_base.empty:
            st.warning("No hay salarios informados para calcular la combinacion demanda-salario.")
        else:
            max_skill_demand = int(skill_salary_base.groupby("skill")["job_id"].nunique().max())
            max_min_jobs = max(3, min(50, max_skill_demand))
            default_min_jobs = min(5, max_min_jobs)
            min_skill_jobs = st.slider(
                "Minimo de ofertas con salario por skill",
                min_value=1,
                max_value=max_min_jobs,
                value=default_min_jobs,
            )

            skill_salary = (
                skill_salary_base.groupby("skill", as_index=False)
                .agg(
                    demanda=("job_id", "nunique"),
                    salario_mediano=("salary_clean", "median"),
                    salario_medio=("salary_clean", "mean"),
                )
                .query("demanda >= @min_skill_jobs")
            )

            if skill_salary.empty:
                st.warning("No hay skills que cumplan el minimo de ofertas seleccionado.")
            else:
                demand_span = skill_salary["demanda"].max() - skill_salary["demanda"].min()
                salary_span = skill_salary["salario_mediano"].max() - skill_salary["salario_mediano"].min()
                skill_salary["demanda_norm"] = (
                    1 if demand_span == 0 else (skill_salary["demanda"] - skill_salary["demanda"].min()) / demand_span
                )
                skill_salary["salario_norm"] = (
                    1
                    if salary_span == 0
                    else (skill_salary["salario_mediano"] - skill_salary["salario_mediano"].min()) / salary_span
                )
                skill_salary["score_combinado"] = (
                    (skill_salary["demanda_norm"] + skill_salary["salario_norm"]) / 2 * 100
                )
                skill_salary_view = skill_salary.nlargest(top_n, "score_combinado")

                fig = px.scatter(
                    skill_salary_view,
                    x="demanda",
                    y="salario_mediano",
                    size="score_combinado",
                    color="score_combinado",
                    hover_name="skill",
                    hover_data={
                        "demanda": True,
                        "salario_mediano": ":,.0f",
                        "salario_medio": ":,.0f",
                        "score_combinado": ":.1f",
                    },
                    title="Skills con mejor equilibrio entre demanda y salario",
                    labels={
                        "demanda": "Ofertas que piden la skill",
                        "salario_mediano": "Salario mediano",
                        "score_combinado": "Score combinado",
                    },
                    color_continuous_scale="Turbo",
                )
                fig.update_traces(marker={"sizemin": 10, "line": {"width": 1, "color": "white"}})
                st.plotly_chart(fig, use_container_width=True)
                st.info(
                    "Lectura de negocio: prioriza las skills situadas arriba y a la derecha; combinan demanda suficiente "
                    "con salarios competitivos y son buenas candidatas para itinerarios de reskilling premium."
                )

with tab_bias:
    st.subheader("Distribucion salarial y senales de sesgo")
    left, right = st.columns(2)

    with left:
        fig = px.histogram(
            filtered.dropna(subset=["salary_clean"]),
            x="salary_clean",
            nbins=35,
            marginal="box",
            title="Distribucion de salarios ofertados",
            labels={"salary_clean": "Salario anual"},
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            "Lectura de negocio: una distribucion muy dispersa exige segmentar por seniority, sector y fuente antes de fijar rangos."
        )

    with right:
        box_group = st.selectbox("Comparar salario por", ["seniority_level", "industry", "job_family", "work_modality"])
        box_data = filtered.dropna(subset=["salary_clean"]).copy()
        keep_groups = box_data[box_group].value_counts().head(12).index
        box_data = box_data[box_data[box_group].isin(keep_groups)]
        fig = px.box(
            box_data,
            x=box_group,
            y="salary_clean",
            color=box_group,
            title=f"Salario por {box_group}",
            labels={box_group: box_group, "salary_clean": "Salario anual"},
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            "Lectura de negocio: las diferencias entre grupos pueden reflejar mercado real, sesgo de muestra o mezcla de roles."
        )

    missing_group = st.selectbox(
        "Auditar ausencia de salario por grupo",
        ["source_dataset", "city_clean", "industry", "seniority_level", "work_modality"],
    )
    missing = (
        filtered.groupby(missing_group, as_index=False)
        .agg(ofertas=("job_id", "count"), pct_sin_salario=("salary_available", lambda s: 100 * (1 - s.mean())))
        .query("ofertas >= 5")
        .sort_values("pct_sin_salario", ascending=False)
        .head(top_n)
    )
    fig = px.bar(
        missing,
        x="pct_sin_salario",
        y=missing_group,
        orientation="h",
        title="Posible sesgo MNAR: grupos con mas salarios ausentes",
        labels={"pct_sin_salario": "% sin salario", missing_group: "Grupo"},
        color="pct_sin_salario",
        color_continuous_scale="Reds",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.warning(
        "El dataset de ofertas no contiene genero. Por tanto, no seria riguroso afirmar sesgo salarial por genero; "
        "la decision correcta es documentar la limitacion y complementarla con una fuente demografica especifica."
    )

with tab_quality:
    st.subheader("Calidad, limpieza y trazabilidad")
    left, right = st.columns(2)

    with left:
        quality = pd.DataFrame(
            {
                "campo": filtered.columns,
                "pct_nulos": [filtered[col].isna().mean() * 100 for col in filtered.columns],
            }
        ).sort_values("pct_nulos", ascending=False)
        fig = px.bar(
            quality.head(top_n),
            x="pct_nulos",
            y="campo",
            orientation="h",
            title="Campos con mayor porcentaje de nulos",
            labels={"pct_nulos": "% nulos", "campo": "Campo"},
            color="pct_nulos",
            color_continuous_scale="Oranges",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        numeric = filtered[["salary_clean", "skills_count", "salary_clean_outlier", "is_remote"]].copy()
        numeric["salary_available"] = filtered["salary_available"].astype(int)
        numeric["salary_clean_outlier"] = numeric["salary_clean_outlier"].astype(int)
        numeric["is_remote"] = numeric["is_remote"].astype(int)
        corr = numeric.corr(numeric_only=True)
        fig = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Matriz de correlaciones de variables derivadas",
        )
        st.plotly_chart(fig, use_container_width=True)

    if not validation.empty:
        st.dataframe(validation, use_container_width=True, hide_index=True)

    st.info(
        "Lectura de negocio: la calidad de salario, fuente y ubicacion determina hasta donde se pueden automatizar recomendaciones."
    )

with tab_actions:
    st.subheader("Recomendaciones para DataTalent Solutions")
    st.markdown(
        """
        **1. Disenar rutas de reskilling por familias de rol.** Usar el ranking de skills como base,
        pero separar analitica/BI, data engineering y data science/AI para evitar una oferta formativa generica.

        **2. Publicar bandas salariales con cautela.** Cuando el porcentaje de salarios ausentes sea alto,
        presentar rangos por seniority, sector y ciudad, no una media global.

        **3. Auditar sesgos antes de modelar.** La ausencia de salario puede no ser aleatoria y el dataset
        no permite evaluar genero. Cualquier modelo predictivo deberia incorporar controles de representatividad.

        **4. Combinar mercado actual y tecnologias emergentes.** Las tecnologias mas usadas indican empleabilidad
        inmediata; las mas deseadas ayudan a anticipar itinerarios de actualizacion.
        """
    )

    st.download_button(
        "Descargar datos filtrados",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="datatalent_ofertas_filtradas.csv",
        mime="text/csv",
    )

    st.dataframe(
        filtered[
            [
                "job_title",
                "company",
                "city_clean",
                "industry",
                "seniority_level",
                "job_family",
                "work_modality",
                "salary_clean",
            ]
        ].head(200),
        use_container_width=True,
        hide_index=True,
    )
