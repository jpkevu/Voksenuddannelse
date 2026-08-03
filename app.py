import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Brancherettede asbestkurser for el- og vvs-branchen",
    layout="wide"
)


# @st.cache_data(ttl=300)
def load_data():

    try:
        response = requests.get(
            "https://voksenuddannelse.dk",
            timeout=10
        )

        st.write("Status:", response.status_code)

    except Exception as e:
        st.write("FEJL:")
        st.exception(e)

    return pd.DataFrame({
        "holdTitle": ["Test"],
        "institution": ["EVU"]
    })

st.title("Brancherettede asbestkurser for el- og vvs-branchen")

st.write(
    "Kurser på AMU 22906 med ledige pladser og åben tilmelding."
)

if st.button("Opdater data"):
    st.cache_data.clear()
    st.rerun()

with st.spinner("Henter data..."):
    try:
        df = load_data()
    except Exception as e:
        st.error("Der opstod en fejl.")
        st.exception(e)
        st.stop()

if df.empty:
    st.warning(
        "Ingen hold fundet med åben tilmelding."
    )
    st.stop()

st.markdown(f"### Fundet {len(df)} hold")

if "ledigePladser" in df.columns:
    st.write(
        f"Samlet antal ledige pladser: **{int(df['ledigePladser'].sum())}**"
    )

filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])

with filter_col1:
    query = st.text_input(
        "Søg i titel eller beskrivelse"
    )

with filter_col2:
    schools = ["Alle"] + sorted(
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
        "Min. ledige",
        min_value=1,
        value=1
    )

filtered_df = df.copy()

if query:
    filtered_df = filtered_df[
        filtered_df["holdTitle"].str.contains(
            query,
            case=False,
            na=False
        )
        |
        filtered_df["beskrivelse"].str.contains(
            query,
            case=False,
            na=False
        )
    ]

if selected_school != "Alle":
    filtered_df = filtered_df[
        filtered_df["institution"] == selected_school
    ]

filtered_df = filtered_df[
    filtered_df["ledigePladser"] >= min_ledige
]

st.markdown(
    f"### Viser {len(filtered_df)} hold"
)

for _, row in filtered_df.iterrows():

    st.subheader(
        row.get("holdTitle", "Hold uden titel")
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.write(
            f"**Skole:** {row.get('institution', '')}"
        )
        st.write(
            f"**Sted:** {row.get('lokationSted', '')}"
        )

    with col2:

        start = row.get("startDate")

        if pd.notna(start):
            start = start.strftime("%d-%m-%Y")

        end = row.get("endDate")

        if pd.notna(end):
            end = end.strftime("%d-%m-%Y")

        st.write(f"**Start:** {start}")
        st.write(f"**Slut:** {end}")

    with col3:

        frist = row.get("tilmeldingsFrist")

        if pd.notna(frist):
            frist = frist.strftime("%d-%m-%Y")

        st.write(f"**Tilmeldingsfrist:** {frist}")
        st.write(
            f"**Undervisning:** {row.get('undervisningsform', '')}"
        )

    with col4:

        st.write(
            f"**Deltagere:** {int(row.get('currentParticipantAmount', 0))}"
        )

        st.write(
            f"**Kapacitet:** {int(row.get('participantCapacity', 0))}"
        )

        st.write(
            f"**Ledige pladser:** {int(row.get('ledigePladser', 0))}"
        )

    beskrivelse = row.get("beskrivelse", "")

    if beskrivelse:
        st.markdown("**Beskrivelse**")
        st.write(beskrivelse)

    with st.expander("Kontaktoplysninger"):
        st.write(
            f"**Kontaktperson:** {row.get('kontaktPerson', '')}"
        )
        st.write(
            f"**Mail:** {row.get('kontaktMail', '')}"
        )
        st.write(
            f"**Telefon:** {row.get('kontaktPersonTlfNummer', '')}"
        )

    link = row.get("link", "")

    if link:
        st.link_button(
            "Åbn hold på voksenuddannelse.dk",
            link
        )

    st.divider()