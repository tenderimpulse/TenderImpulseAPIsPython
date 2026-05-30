from tender_impulse_client import TenderImpulseClient

# Local folder where tender documents will be stored.
store_path = "documents"

# Access token provided by Tender Impulse.
access_token = "your_access_token"

# AES decryption key provided by Tender Impulse.
key = "your_encryption_key"

client = TenderImpulseClient(
    store_path,
    access_token,
    key
)

last_id = 6771840

result = client.get_tenders(last_id)

if result["status"] == "success":

    print(f"Tenders Fetched: {len(result['tenders'])}")

    print(f"Last Fetch Id: {result['last_fetch_id']}")

    print(result["tenders"])

else:

    print(f"Error: {result['msg']}")