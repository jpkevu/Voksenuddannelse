import pandas as pd
import requests


def fetch_data():
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

        print(f"Henter side {page}")

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=60
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
        print("Ingen data hentet.")
        df.to_csv(
            "amu22906.csv",
            index=False,
            encoding="utf-8-sig"
        )
        return

    today = pd.Timestamp.today().normalize()

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
        "lokationPostNr"
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

    df.to_csv(
        "amu22906.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Gemte {len(df)} hold i amu22906.csv")


if __name__ == "__main__":
    fetch_data()