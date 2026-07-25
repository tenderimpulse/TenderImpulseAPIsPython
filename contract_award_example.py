import os
import json

from tender_impulse_contract_award_client import TenderImpulseContractAwardClient

# Local folder where contract award documents will be stored.
store_path = "contract-award-documents"

# Access token provided by Tender Impulse.
access_token = "your_access_token"

# AES decryption key provided by Tender Impulse.
key = "your_encryption_key"

# File where the last fetch id is stored between runs.
state_file = os.path.abspath("contract-award-state.json")

# Fetch id to start from the very first time this example is run.
initial_last_id = 261374

client = TenderImpulseContractAwardClient(
    store_path,
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

result = client.get_contract_awards(last_id)

if result["status"] == "success":

    print(f"Contract Awards Fetched: {len(result['contracts'])}")

    print(f"Last Fetch Id: {result['last_fetch_id']}")

    print(result["contracts"])

    # Store the fetch id only after the batch has been handled,
    # so nothing is skipped if the run fails midway.
    write_last_id(result["last_fetch_id"])

else:

    print(f"Error: {result['msg']}")
