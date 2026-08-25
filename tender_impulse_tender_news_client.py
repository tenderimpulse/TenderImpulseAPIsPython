"""
Tender Impulse tender news API client library for Python.

Provides functionality to:
- Retrieve tender news articles
- Authenticate using Bearer tokens
- Decrypt API responses
- Validate response integrity using CRC/MD5 checksums
- Process API data into Python dictionaries/lists

Tender news articles have no attachments, so this client downloads nothing
and takes no store path.
"""

import json
import base64
import hashlib
import requests

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


class TenderImpulseTenderNewsClient:
    def __init__(self, access_token: str, key: str):
        """
        Initialize the Tender Impulse tender news client.

        Args:
            access_token: Access token provided by Tender Impulse.
            key: AES decryption key provided by Tender Impulse.
        """
        self.access_token = access_token
        self.key = key

    def get_tender_news(self, last_id: int) -> dict:
        """
        Calls Tender Impulse API and retrieves tender news records.

        Args:
            last_id: Last tender news ID already processed.

        Returns:
            Dictionary containing status and tender news data.
        """
        try:
            url = (
                f"https://tenderimpulse.com/web-api/news/v2/uat.php"
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

            response_tender_news = []

            # "news" is the field name used in the API payload.
            for article in details["news"]:

                response_tender_news.append({
                    "blogid": article.get("blogid"),
                    "blogtitle": article.get("blogtitle"),
                    "shortdescription": article.get("shortdescription"),
                    "longdescription": article.get("longdescription"),
                    "seourl": article.get("seourl"),
                    "thumbnail_image": article.get("thumbnail_image"),
                    "publishstatus": article.get("publishstatus"),
                    "publishdate": article.get("publishdate"),
                    "metatitle": article.get("metatitle"),
                    "metakeywords": article.get("metakeywords"),
                    "source": article.get("source"),
                    "blogstatus": article.get("blogstatus"),
                    "sectors": article.get("sectors"),
                    "cpvs": article.get("cpvs"),
                    "countries": article.get("countries"),
                    "regions": article.get("regions"),
                    "createddate": article.get("createddate"),
                    # Spelt this way in the API payload.
                    "ceratedtime": article.get("ceratedtime"),
                    "updatedate": article.get("updatedate"),
                    "updatedtime": article.get("updatedtime"),
                })

            return {
                "status": "success",
                "tender_news": response_tender_news,
                "last_fetch_id": details["fetchid"],
            }

        except Exception as e:
            return {
                "status": "error",
                "msg": str(e),
            }

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
