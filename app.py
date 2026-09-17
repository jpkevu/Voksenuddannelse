import streamlit as st
import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# SIDEOPSÆTNING
# ---------------------------------------------------------

st.set_page_config(
    page_title="Brancherettede asbestkurser for el- og vvs-branchen",
    layout="wide"
)


# ---------------------------------------------------------
# DESIGN OG FARVER
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    /* Hele sidens baggrund */
    [data-testid="stAppViewContainer"] {
        background-color: #466764;
    }

    /* Streamlits øverste bjælke */
    [data-testid="stHeader"] {
        background-color: rgba(70, 103, 100, 0.96);
    }

    /* Ryk hele indholdet lidt ind */
    .block-container {
        max-width: 100%;
        padding-top: 2rem;
        padding-left: 4rem;
        padding-right: 2rem;
        padding-bottom: 4rem;
    }

    /* Generel hvid tekst */
    h1,
    h2,
    h3,
    h4,
    h5,
    h6,
    p,
    label,
    li,
    [data-testid="stMarkdownContainer"] {
        color: #ffffff;
    }

    /* Hovedoverskrift */
    h1 {
        font-size: 3rem;
        line-height: 1.15;
        font-weight: 750;
        margin-top: 0;
        margin-bottom: 0.75rem;
    }

    /* Underoverskrifter */
    h2,
    h3 {
        font-weight: 700;
    }

    /* Introafsnit */
    .intro-text {
        color: #ffffff;
        font-size: 1.15rem;
        line-height: 1.6;
        max-width: 850px;
        margin-bottom: 1.25rem;
    }

    /* Labels over inputfelter */
    [data-testid="stWidgetLabel"] p {
        color: #ffffff;
        font-weight: 600;
    }

    /* Tekstinput */
    [data-testid="stTextInput"] input {
        background-color: #ffffff;
        color: #1f2937;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 8px;
    }

    /* Placeholder i tekstinput */
    [data-testid="stTextInput"] input::placeholder {
        color: #6b7280;
    }

    /* Nummerfelt */
    [data-testid="stNumberInput"] input {
        background-color: #ffffff;
        color: #1f2937;
    }

    /* Knapper i nummerfelt */
    [data-testid="stNumberInput"] button {
        background-color: #ffffff;
        color: #1f2937;
    }

    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background-color: #ffffff;
        color: #1f2937;
        border-radius: 8px;
    }

    [data-baseweb="select"] div {
        color: #1f2937;
    }

    /* Dropdown-menu */
    [role="listbox"] {
        background-color: #ffffff;
    }

    [role="option"] {
        color: #1f2937;
    }

    /* Almindelige knapper og linkknapper */
    .stButton > button,
    .stLinkButton > a {
        background-color: #00d43b;
        color: #17332f;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        padding: 0.6rem 1.15rem;
        transition: 0.2s ease-in-out;
    }

    .stButton > button:hover,
    .stLinkButton > a:hover {
        background-color: #00ef45;
        color: #17332f;
        border: none;
        transform: translateY(-1px);
    }

    .stButton > button:focus,
    .stLinkButton > a:focus {
        color: #17332f;
        border-color: #00ef45;
    }

    /* Statistikbokse */
    .stat-card {
        background-color: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        min-height: 100px;
        margin-top: 0.75rem;
        margin-bottom: 1rem;
    }

    .stat-label {
        color: rgba(255, 255, 255, 0.82);
        font-size: 0.95rem;
        margin-bottom: 0.3rem;
    }

    .stat-value {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 750;
        line-height: 1.2;
    }

    /* Kontaktoplysninger */
    [data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 10px;
    }

    [data-testid="stExpander"] summary {
        color: #ffffff;
        font-weight: 600;
    }

    [data-testid="stExpander"] svg {
        fill: #ffffff;
    }

    /* Vandrette skillelinjer */
    hr {
        border-color: rgba(255, 255, 255, 0.30);
        margin-top: 1.75rem;
        margin-bottom: 1.75rem;
    }

    /* Spinnertekst */
    [data-testid="stSpinner"] p {
        color: #ffffff;
    }

    /* Kampagnebillede */
    [data-testid="stImage"] img {
        width: 100%;
        max-width: 430px;
        border-radius: 12px;
        display: block;
        margin-left: auto;
        margin-right: 0;
    }

    /* Billedkolonnen gøres fast ved scroll på store skærme */
    .sticky-image {
        position: sticky;
        top: 2rem;
    }

    /* Beskeder */
    [data-testid="stAlert"] p {
        color: inherit;
    }

    /* Tilpasning til mindre skærme */
    @media (max-width: 900px) {

        .block-container {
            padding-top: 1.25rem;
            padding-left: 1.25rem;
            padding-right: 1.25rem;
        }

        h1 {
            font-size: 2.2rem;
        }

        [data-testid="stImage"] img {
            max-width: 320px;
            margin-left: auto;
            margin-right: auto;
        }

        .sticky-image {
            position: static;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# INDLÆSNING AF DATA
# ---------------------------------------------------------

@st.cache_data(ttl=300)
def load_data():

    csv_path = Path("amu22906.csv")

    if not csv_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig"
    )

    date_columns = [
        "startDate",
        "endDate",
        "tilmeldingsFrist"
    ]

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )

    numeric_columns = [
        "currentParticipantAmount",
        "participantCapacity",
        "ledigePladser"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

    text_columns = [
        "beskrivelse",
        "institution",
        "lokationSted",
        "holdTitle",
        "kviknummer",
        "kontaktPerson",
        "kontaktMail",
        "kontaktPersonTlfNummer",
        "undervisningsform",
        "lokationGade",
        "lokationPostNr",
        "link"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
            )

    if "startDate" in df.columns:
        df = df.sort_values(
            "startDate",
            na_position="last"
        )

    return df


# ---------------------------------------------------------
# HJÆLPEFUNKTIONER
# ---------------------------------------------------------

def format_date(value):

    if pd.isna(value) or value == "":
        return "Ikke oplyst"

    parsed_date = pd.to_datetime(
        value,
        errors="coerce"
    )

    if pd.isna(parsed_date):
        return "Ikke oplyst"

    return parsed_date.strftime("%d-%m-%Y")


def format_number(value):

    if pd.isna(value) or value == "":
        return 0

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def clean_text(value, fallback="Ikke oplyst"):

    if pd.isna(value):
        return fallback

    cleaned_value = str(value).strip()

    if not cleaned_value:
        return fallback

    return cleaned_value


# ---------------------------------------------------------
# HENT DATA FØR KOLONNERNE OPRETTES
# ---------------------------------------------------------

with st.spinner("Indlæser kursusdata..."):
    df = load_data()


if df.empty:
    st.warning(
        "Der er ikke fundet nogen hold i den seneste datafil."
    )
    st.stop()


# ---------------------------------------------------------
# OVERORDNEDE TAL
# ---------------------------------------------------------

total_ledige = 0

if "ledigePladser" in df.columns:
    total_ledige = int(
        df["ledigePladser"].sum()
    )


# ---------------------------------------------------------
# HOVEDLAYOUT
# ---------------------------------------------------------

left_column, right_column = st.columns(
    [3.2, 1],
    gap="large",
    vertical_alignment="top"
)


# ---------------------------------------------------------
# VENSTRE KOLONNE
# Titel, statistik, filtre og samtlige hold
# ---------------------------------------------------------

with left_column:

    st.markdown(
        """
        <h1>
            Brancherettede asbestkurser for el- og vvs-branchen
        </h1>

        <div class="intro-text">
            Her vises aktive AMU-hold for kursus 22906 med ledige
            pladser og åben tilmeldingsfrist.
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Genindlæs data",
        type="primary"
    ):
        st.cache_data.clear()
        st.rerun()

    # -----------------------------------------------------
    # STATISTIK
    # -----------------------------------------------------

    stat_col1, stat_col2, stat_col3 = st.columns(
        [1, 1, 1.5]
    )

    with stat_col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Fundne hold</div>
                <div class="stat-value">{len(df)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with stat_col2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Ledige pladser</div>
                <div class="stat-value">{total_ledige}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with stat_col3:
        st.empty()

    # -----------------------------------------------------
    # FILTRE
    # -----------------------------------------------------

    st.markdown("### Find et kursushold")

    filter_col1, filter_col2, filter_col3 = st.columns(
        [2, 1.5, 1]
    )

    with filter_col1:

        query = st.text_input(
            "Søg i titel eller beskrivelse",
            value="",
            placeholder="Skriv eksempelvis sikkerhed eller asbest"
        )

    with filter_col2:

        schools = ["Alle"]

        if "institution" in df.columns:

            institutions = (
                df["institution"]
                .replace("", pd.NA)
                .dropna()
                .drop_duplicates()
                .sort_values()
                .tolist()
            )

            schools.extend(institutions)

        selected_school = st.selectbox(
            "Skole",
            schools
        )

    with filter_col3:

        min_ledige = st.number_input(
            "Min. ledige pladser",
            min_value=1,
            value=1,
            step=1
        )

    # -----------------------------------------------------
    # FILTRERING
    # -----------------------------------------------------

    filtered_df = df.copy()

    if query.strip():

        query_mask = pd.Series(
            False,
            index=filtered_df.index
        )

        if "holdTitle" in filtered_df.columns:
            query_mask = (
                query_mask
                | filtered_df["holdTitle"].str.contains(
                    query.strip(),
                    case=False,
                    na=False,
                    regex=False
                )
            )

        if "beskrivelse" in filtered_df.columns:
            query_mask = (
                query_mask
                | filtered_df["beskrivelse"].str.contains(
                    query.strip(),
                    case=False,
                    na=False,
                    regex=False
                )
            )

        filtered_df = filtered_df[query_mask]

    if (
        selected_school != "Alle"
        and "institution" in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df["institution"] == selected_school
        ]

    if "ledigePladser" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["ledigePladser"] >= min_ledige
        ]

    if "startDate" in filtered_df.columns:
        filtered_df = filtered_df.sort_values(
            "startDate",
            na_position="last"
        )

    # -----------------------------------------------------
    # VIS HOLD
    # -----------------------------------------------------

    st.markdown(
        f"### Viser {len(filtered_df)} hold"
    )

    if filtered_df.empty:

        st.info(
            "Der er ingen hold, der matcher de valgte filtre."
        )

    else:

        for _, row in filtered_df.iterrows():

            title = clean_text(
                row.get("holdTitle", ""),
                fallback="Hold uden titel"
            )

            st.subheader(title)

            startdato = format_date(
                row.get("startDate", "")
            )

            slutdato = format_date(
                row.get("endDate", "")
            )

            tilmeldingsfrist = format_date(
                row.get("tilmeldingsFrist", "")
            )

            deltagere = format_number(
                row.get("currentParticipantAmount", 0)
            )

            kapacitet = format_number(
                row.get("participantCapacity", 0)
            )

            ledige = format_number(
                row.get("ledigePladser", 0)
            )

            institution = clean_text(
                row.get("institution", "")
            )

            location = clean_text(
                row.get("lokationSted", "")
            )

            address = clean_text(
                row.get("lokationGade", ""),
                fallback=""
            )

            post_number = clean_text(
                row.get("lokationPostNr", ""),
                fallback=""
            )

            undervisningsform = clean_text(
                row.get("undervisningsform", "")
            )

            # Tre kolonner giver bedre plads i venstre hovedkolonne
            info_col1, info_col2, info_col3 = st.columns(
                [1.5, 1.3, 1]
            )

            with info_col1:

                st.write(
                    f"**Skole:** {institution}"
                )

                st.write(
                    f"**Sted:** {location}"
                )

                if address:
                    st.write(
                        f"**Adresse:** {address}"
                    )

                if post_number:
                    st.write(
                        f"**Postnr.:** {post_number}"
                    )

            with info_col2:

                st.write(
                    f"**Startdato:** {startdato}"
                )

                st.write(
                    f"**Slutdato:** {slutdato}"
                )

                st.write(
                    f"**Tilmeldingsfrist:** {tilmeldingsfrist}"
                )

                st.write(
                    f"**Undervisning:** {undervisningsform}"
                )

            with info_col3:

                st.write(
                    f"**Deltagere:** {deltagere}"
                )

                st.write(
                    f"**Kapacitet:** {kapacitet}"
                )

                st.write(
                    f"**Ledige pladser:** {ledige}"
                )

            beskrivelse = clean_text(
                row.get("beskrivelse", ""),
                fallback=""
            )

            if beskrivelse:

                st.markdown("**Beskrivelse**")

                st.write(beskrivelse)

            with st.expander("Kontaktoplysninger"):

                hold_id = clean_text(
                    row.get("id", "")
                )

                kviknummer = clean_text(
                    row.get("kviknummer", "")
                )

                kontaktperson = clean_text(
                    row.get("kontaktPerson", "")
                )

                kontaktmail = clean_text(
                    row.get("kontaktMail", "")
                )

                telefon = clean_text(
                    row.get("kontaktPersonTlfNummer", "")
                )

                st.write(
                    f"**Hold-id:** {hold_id}"
                )

                st.write(
                    f"**Kviknummer:** {kviknummer}"
                )

                st.write(
                    f"**Kontaktperson:** {kontaktperson}"
                )

                st.write(
                    f"**Kontaktmail:** {kontaktmail}"
                )

                st.write(
                    f"**Telefon:** {telefon}"
                )

            link = clean_text(
                row.get("link", ""),
                fallback=""
            )

            if link:
                st.link_button(
                    "Åbn hold på voksenuddannelse.dk",
                    link
                )

            st.divider()


# ---------------------------------------------------------
# HØJRE KOLONNE
# Kun kampagnebilledet
# ---------------------------------------------------------

with right_column:

    st.image(
        "images/asbest_banner.png",
        use_container_width=True
    )

    st.markdown(
        """
        <div style="height: 1500px;"></div>
        """,
        unsafe_allow_html=True
    )

    st.image(
        "images/Gr├©n mand 1.png",
        use_container_width=True
    )