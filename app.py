import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Brancherettede asbestkurser for el- og vvs-branchen",
    layout="wide"
)


@st.cache_data(ttl=300)
def load_data():
    subject_code = "22906"

    url = "https://voksenuddannelse.dk/soeg-api/api/search/hold/searchHold"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://voksenuddannelse.dk/"
    }

    all_rows = []
    page = 1

    while True:
        params = {
            "subject_code": subject_code,
            "level": "-",
            "type": "AMU",
            "pageCount": str(page)
        }

        st.write(f"Henter side {page}...")

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        rows = data.get("holdCardDtos", [])

        if not rows:
            break

        all_rows.extend(rows)

        page += 1

        if page > 100:
            break

    df = pd.DataFrame(all_rows)

    if df.empty:
        return df

    today = pd.Timestamp.today().normalize()

    text_columns = [
        "beskrivelse",
        "institution",
        "lokationSted",
        "holdTitle",
        "kviknummer"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna("")

    if "startDate" in df.columns:
        df["startDate"] = pd.to_datetime(
            df["startDate"],
            errors="coerce"
        )

        df = df[
            df["startDate"] >= today
        ]

    if "endDate" in df.columns:
        df["endDate"] = pd.to_datetime(
            df["endDate"],
            errors="coerce"
        )

    if "tilmeldingsFrist" in df.columns:
        df["tilmeldingsFrist"] = pd.to_datetime(
            df["tilmeldingsFrist"],
            errors="coerce"
        )

        df = df[
            df["tilmeldingsFrist"] >= today
        ]

    if "currentParticipantAmount" in df.columns:
        df["currentParticipantAmount"] = pd.to_numeric(
            df["currentParticipantAmount"],
            errors="coerce"
        ).fillna(0)

    if "participantCapacity" in df.columns:
        df["participantCapacity"] = pd.to_numeric(
            df["participantCapacity"],
            errors="coerce"
        ).fillna(0)

    if (
        "currentParticipantAmount" in df.columns
        and "participantCapacity" in df.columns
    ):
        df["ledigePladser"] = (
            df["participantCapacity"]
            - df["currentParticipantAmount"]
        )

        df = df[
            df["ledigePladser"] > 0
        ]

    if "aflyst" in df.columns:
        df = df[
            df["aflyst"] == False
        ]

    if "kviknummer" in df.columns:
        df["link"] = (
            "https://voksenuddannelse.dk/soeg/uddannelser/amu/filtrering/kurs"
            + "?subject_code=22906"
            + "&level=-"
            + "&type=amu"
            + "&kviknummer="
            + df["kviknummer"].astype(str)
        )

    if "startDate" in df.columns:
        df = df.sort_values("startDate")

    return df


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