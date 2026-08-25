import os
import json

from tender_impulse_tender_news_client import TenderImpulseTenderNewsClient

# Access token provided by Tender Impulse.
access_token = "your_access_token"

# AES decryption key provided by Tender Impulse.
key = "your_encryption_key"

# File where the last fetch id is stored between runs.
state_file = os.path.abspath("tender-news-state.json")

# Fetch id to start from the very first time this example is run.
initial_last_id = 18016

client = TenderImpulseTenderNewsClient(
    access_token,
    key
)


def read_last_id() -> int:
    """Reads the stored fetch id, or falls back to the initial one."""

    if not os.path.exists(state_file):
        return initial_last_id

    with open(state_file, "r", encoding="utf-8") as file:
        state = json.load(file)

    return state["fetchid"]


def write_last_id(fetch_id: int) -> None:
    """Stores the fetch id so the next call resumes from here."""

    with open(state_file, "w", encoding="utf-8") as file:
        json.dump({"fetchid": fetch_id}, file, indent=2)


last_id = read_last_id()

print(f"Last Id: {last_id}")

result = client.get_tender_news(last_id)

if result["status"] == "success":

    print(f"Tender News Fetched: {len(result['tender_news'])}")

    print(f"Last Fetch Id: {result['last_fetch_id']}")

    # Only the headline fields are printed here. Every article also
    # carries longdescription, which holds the full article HTML.
    for article in result["tender_news"]:

        print({
            "blogid": article["blogid"],
            "blogtitle": article["blogtitle"],
            "publishdate": article["publishdate"],
            "countries": article["countries"],
            "sectors": article["sectors"],
        })

    # Store the fetch id only after the batch has been handled,
    # so nothing is skipped if the run fails midway.
    write_last_id(result["last_fetch_id"])

else:

    print(f"Error: {result['msg']}")
