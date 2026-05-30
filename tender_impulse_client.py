"""
Tender Impulse API client library for Python.

Provides functionality to:
- Retrieve tenders and contract awards
- Authenticate using Bearer tokens
- Decrypt API responses
- Validate response integrity using CRC/MD5 checksums
- Download and store tender documents
- Process API data into Python dictionaries/lists
"""

import os
import json
import base64
import hashlib
import requests

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


class TenderImpulseClient:
    def __init__(self, store_path: str, access_token: str, key: str):
        """
        Initialize the Tender Impulse client.

        Args:
            store_path: Local folder where tender documents will be stored.
            access_token: Access token provided by Tender Impulse.
            key: AES decryption key provided by Tender Impulse.
        """
        self.store_path = store_path.rstrip("/\\") + os.sep
        self.access_token = access_token
        self.key = key

    def get_tenders(self, last_id: int) -> dict:
        """
        Calls Tender Impulse API and retrieves tender records.

        Args:
            last_id: Last tender ID already processed.

        Returns:
            Dictionary containing status and tender data.
        """
        try:
            url = (
                f"https://tenderimpulse.com/web-api/tender/v2/uat.php"
                f"?lastid={last_id}"
            )

            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                timeout=90,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Could not connect to tenderimpulse.com, "
                    f"error code: {response.status_code}"
                )

            api_response = response.json()

            decrypted = self.decrypt(api_response["data"])

            calculated_crc = hashlib.md5(
                decrypted.encode("utf-8")
            ).hexdigest()

            if calculated_crc.lower() != api_response["crc"].lower():
                raise Exception("Message transmission error")

            details = json.loads(decrypted)

            if details["status"] != "success":
                raise Exception(details["msg"])

            response_tenders = []

            for tender in details["tenders"]:

                response_tender = {
                    "tender_id": tender.get("tender_id"),
                    "title": tender.get("title"),
                    "authority_name": tender.get("authority_name"),
                    "address": tender.get("address"),
                    "tel": tender.get("tel"),
                    "fax": tender.get("fax"),
                    "email": tender.get("email"),
                    "web": tender.get("web"),
                    "contact_name": tender.get("contact_name"),
                    "contract_type": tender.get("contract_type"),
                    "sectors": tender.get("sectors"),
                    "cpv_codes": tender.get("cpv_codes"),
                    "country": tender.get("country"),
                    "original_source": tender.get("original_source"),
                    "location": tender.get("location"),
                    "reference": tender.get("reference"),
                    "contract_duration": tender.get("contract_duration"),
                    "value_of_contract": tender.get("value_of_contract"),
                    "deadline": tender.get("deadline"),
                    "other_information": tender.get("other_information"),
                    "filename": os.path.join(
                        self.store_path,
                        tender["filename"]
                    ),
                }

                self.download_file(
                    tender["filepath"],
                    tender["filename"]
                )

                response_tender["filepath"] = os.path.join(
                    self.store_path,
                    tender["filename"]
                )

                response_tenders.append(response_tender)

            return {
                "status": "success",
                "tenders": response_tenders,
                "last_fetch_id": details["fetchid"],
            }

        except Exception as e:
            return {
                "status": "error",
                "msg": str(e),
            }

    def download_file(self, url: str, file_name: str) -> None:
        """
        Downloads a tender document and stores it locally.

        Args:
            url: Remote file URL.
            file_name: Relative file path from API.
        """
        local_path = os.path.join(self.store_path, file_name)

        directory = os.path.dirname(local_path)
        os.makedirs(directory, exist_ok=True)

        response = requests.get(url, stream=True, timeout=120)

        if response.status_code != 200:
            raise Exception(f"Unable to download file: {file_name}")

        with open(local_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

    def decrypt(self, data: str) -> str:
        """
        Decrypts encrypted payload received from API.

        Expected format:
            encryptedData:iv

        Uses AES-128-CBC.
        """
        try:
            parts = data.split(":")

            if len(parts) != 2:
                raise Exception("Invalid encrypted payload")

            encrypted_data = base64.b64decode(parts[0])
            iv = base64.b64decode(parts[1])

            key = self.key.encode("utf-8")

            # Ensure AES-128 key length
            if len(key) < 16:
                key = key.ljust(16, b"0")
            elif len(key) > 16:
                key = key[:16]

            cipher = AES.new(key, AES.MODE_CBC, iv)

            decrypted = unpad(
                cipher.decrypt(encrypted_data),
                AES.block_size
            )

            return decrypted.decode("utf-8")

        except Exception:
            raise Exception("Unable to decrypt")