import os
from web3 import Web3

ALCHEMY_HTTP_URL = os.getenv("ALCHEMY_HTTP_URL")
w3 = Web3(Web3.HTTPProvider(ALCHEMY_HTTP_URL))

COMMON_TEXT_KEYS = [
    "avatar","description","email","url",
    "com.twitter","com.github","org.telegram",
    "vnd.linkedin","vnd.discord","notice","keywords"
]

def fetch_ens_profile(name: str):
    if not ALCHEMY_HTTP_URL:
        return {"error": "ALCHEMY_HTTP_URL not set in .env"}
    if not w3.is_connected():
        return {"error": "Web3 not connected. Check ALCHEMY_HTTP_URL."}

    address = w3.ens.address(name)
    if not address:
        return None

    try:
        resolver = w3.ens.resolver(name)
        resolver_addr = resolver.address if resolver else None
    except Exception:
        resolver_addr = None

    try:
        contenthash = w3.ens.content_hash(name)
    except Exception:
        contenthash = None

    text_records = {}
    for k in COMMON_TEXT_KEYS:
        try:
            v = w3.ens.get_text(name, k)
            if v:
                text_records[k] = v
        except Exception:
            pass

    try:
        primary_name = w3.ens.name(address)
    except Exception:
        primary_name = None

    return {
        "ens": name,
        "address": Web3.to_checksum_address(address),
        "resolver_address": resolver_addr,
        "contenthash": contenthash,
        "text_records": text_records,
        "reverse_record_primary_name": primary_name,
    }
