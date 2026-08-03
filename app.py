import streamlit as st
import pandas as pd
from pathlib import Path


st.set_page_config(
    page_title="Brancherettede asbestkurser for el- og vvs-branchen",
    layout="wide"
)


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
            df[col] = df[col].fillna("")

    if "startDate" in df.columns:
        df = df.sort_values("startDate")

    return df


st.title("Brancherettede asbestkurser for el- og vvs-branchen")

st.write(
    "Her vises aktive AMU-hold for kursus 22906 med ledige pladser og åben tilmeldingsfrist."
)

if st.button("Genindlæs data"):
    st.cache_data.clear()
    st.rerun()


with st.spinner("Indlæser kursusdata..."):
    df = load_data()


if df.empty:
    st.warning(
        "Der er ikke fundet nogen hold i den seneste datafil."
    )
    st.stop()


st.markdown(f"### Fundet {len(df)} hold")

if "ledigePladser" in df.columns:
    total_ledige = int(df["ledigePladser"].sum())

    st.write(
        f"Samlet antal ledige pladser: **{total_ledige}**"
    )


filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])

with filter_col1:
    query = st.text_input(
        "Søg i titel eller beskrivelse",
        value=""
    )

with filter_col2:
    schools = ["Alle"]

    if "institution" in df.columns:
        schools += sorted(
            df["institution"]
            .dropna()
            .unique()
            .tolist()
        )

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


filtered_df = df.copy()

if query:
    query_mask = pd.Series(
        False,
        index=filtered_df.index
    )

    if "holdTitle" in filtered_df.columns:
        query_mask = query_mask | filtered_df["holdTitle"].str.contains(
            query,
            case=False,
            na=False
        )

    if "beskrivelse" in filtered_df.columns:
        query_mask = query_mask | filtered_df["beskrivelse"].str.contains(
            query,
            case=False,
            na=False
        )

    filtered_df = filtered_df[query_mask]

if selected_school != "Alle":
    filtered_df = filtered_df[
        filtered_df["institution"] == selected_school
    ]

if "ledigePladser" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["ledigePladser"] >= min_ledige
    ]


st.markdown(f"### Viser {len(filtered_df)} hold")


for _, row in filtered_df.iterrows():

    title = row.get("holdTitle", "")

    if not title:
        title = "Hold uden titel"

    st.subheader(title)

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        st.write(f"**Skole:** {row.get('institution', '')}")
        st.write(f"**Sted:** {row.get('lokationSted', '')}")

        address = row.get("lokationGade", "")
        post_number = row.get("lokationPostNr", "")

        if address:
            st.write(f"**Adresse:** {address}")

        if post_number:
            st.write(f"**Postnr.:** {post_number}")

    with col2:
        startdato = row.get("startDate", "")
        slutdato = row.get("endDate", "")

        if pd.notna(startdato) and startdato != "":
            startdato = startdato.strftime("%d-%m-%Y")

        if pd.notna(slutdato) and slutdato != "":
            slutdato = slutdato.strftime("%d-%m-%Y")

        st.write(f"**Startdato:** {startdato}")
        st.write(f"**Slutdato:** {slutdato}")

    with col3:
        tilmeldingsfrist = row.get("tilmeldingsFrist", "")

        if pd.notna(tilmeldingsfrist) and tilmeldingsfrist != "":
            tilmeldingsfrist = tilmeldingsfrist.strftime("%d-%m-%Y")

        st.write(f"**Tilmeldingsfrist:** {tilmeldingsfrist}")
        st.write(f"**Undervisning:** {row.get('undervisningsform', '')}")

    with col4:
        deltagere = row.get("currentParticipantAmount", 0)
        kapacitet = row.get("participantCapacity", 0)
        ledige = row.get("ledigePladser", 0)

        if pd.notna(deltagere):
            deltagere = int(deltagere)

        if pd.notna(kapacitet):
            kapacitet = int(kapacitet)

        if pd.notna(ledige):
            ledige = int(ledige)

        st.write(f"**Deltagere:** {deltagere}")
        st.write(f"**Kapacitet:** {kapacitet}")
        st.write(f"**Ledige pladser:** {ledige}")

    beskrivelse = row.get("beskrivelse", "")

    if beskrivelse:
        st.markdown("**Beskrivelse**")
        st.write(beskrivelse)

    with st.expander("Kontaktoplysninger"):
        st.write(f"**Hold-id:** {row.get('id', '')}")
        st.write(f"**Kviknummer:** {row.get('kviknummer', '')}")
        st.write(f"**Kontaktperson:** {row.get('kontaktPerson', '')}")
        st.write(f"**Kontaktmail:** {row.get('kontaktMail', '')}")
        st.write(f"**Telefon:** {row.get('kontaktPersonTlfNummer', '')}")

    link = row.get("link", "")

    if link:
        st.link_button(
            "Åbn hold på voksenuddannelse.dk",
            link
        )

    st.divider()