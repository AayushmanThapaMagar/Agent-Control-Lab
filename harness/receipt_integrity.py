import hmac
import json


PREFIX = b"agent-control-lab:receipt:v1\n"


def receipt_tag(receipt, key):
    if not isinstance(key, bytes) or len(key) != 32:
        raise ValueError("Expected a 32-byte harness key.")

    encoded = json.dumps(
        receipt,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")

    return hmac.digest(key, PREFIX + encoded, "sha256")


def seal_receipt(receipt, key):
    if not isinstance(receipt, dict):
        raise ValueError("Receipt must be a JSON object.")

    return {
        "receipt": receipt,
        "tag": receipt_tag(receipt, key).hex(),
    }


def open_receipt(envelope, key):
    if not isinstance(envelope, dict) or set(envelope) != {"receipt", "tag"}:
        raise ValueError("Invalid receipt envelope.")

    receipt = envelope["receipt"]
    tag = envelope["tag"]
    if not isinstance(receipt, dict) or not isinstance(tag, str) or len(tag) != 64:
        raise ValueError("Invalid receipt or tag.")

    try:
        supplied = bytes.fromhex(tag)
    except ValueError as error:
        raise ValueError("Invalid receipt tag.") from error

    if not hmac.compare_digest(receipt_tag(receipt, key), supplied):
        raise ValueError("Receipt authentication failed.")

    return receipt