import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

MODEL = "qwen3:14b"
OLLAMA_URL = "http://127.0.0.1:11434"
HTTP_TIMEOUT = 180


def ollama(path, body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(
        OLLAMA_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urlopen(request, timeout=HTTP_TIMEOUT) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read(4096).decode(errors="replace")
        raise RuntimeError(f"Ollama HTTP {error.code}: {detail}") from error
