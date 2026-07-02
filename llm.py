import requests
import base64
from typing import Optional

from structure import Receipt


class BaseLLM:
    def generate(self, prompt: str, image: Optional[str] = None) -> str:
        raise NotImplementedError


class OllamaLLM(BaseLLM):

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        timeout: int = 300
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    # helper: image encoding
    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    # main generation method
    def generate(self, prompt: str, image: Optional[str] = None) -> str:

        url = f"{self.base_url}/api/chat"

        messages = []

        # Vision mode (image + text)
        if image is not None:
            image_b64 = self._encode_image(image)

            messages.append({
                "role": "user",
                "content": prompt,
                "images": [image_b64]
            })

        # Text-only mode
        else:
            messages.append({
                "role": "user",
                "content": prompt
            })

        payload = {
            "model": self.model,
            "messages": messages,
            "format": Receipt.model_json_schema(),
            "stream": False,
            "think": True
        }

        response = requests.post(
            url,
            json=payload,
            timeout=self.timeout
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Ollama error [{response.status_code}]: {response.text}"
            )

        data = response.json()

        return data["message"]["content"]