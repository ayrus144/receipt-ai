import re
from abc import ABC, abstractmethod

from structure import Receipt, Field
from ocr import OCR
from llm import OllamaLLM
import config


class BaseExtractor(ABC):

    @abstractmethod
    def extract(self, file_path: str) -> dict:
        pass


def empty_result():
    return Receipt(
        company=Field(),
        invoice_number=Field(),
        date=Field(),
        total=Field()
    )

def extract_json(text: str) -> dict:
    import json
    import re

    text = text.strip()

    # remove markdown fences
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text.strip())

    # fix escaped junk that models produce
    text = text.replace('\\"', '"')

    # extract first JSON object safely
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON found")

    return json.loads(text[start:end+1])


class RegexExtractor(BaseExtractor):

    def __init__(self):
        self.ocr = OCR()

    def extract(self, file_path: str) -> dict:

        text = self.ocr.extract_text(file_path)

        result = empty_result()

        # crude but effective MVP regex patterns
        invoice_match = re.search(r"(invoice\s*(no|number)?\s*[:\-]?\s*\w+)", text, re.I)
        date_match = re.search(r"(\d{2}[\/\-]\d{2}[\/\-]\d{2,4})", text)
        total_match = re.search(r"\b(total|amount due)\s*[:\-]?\s*([\d,.]+)", text, re.I)

        if invoice_match:
            result.invoice_number.value = invoice_match.group(0)
            result.invoice_number.confidence = 0.5

        if date_match:
            result.date.value = date_match.group(1)
            result.date.confidence = 0.5

        if total_match:
            result.total.value = float(total_match.group(2).replace(",", ""))
            result.total.confidence = 0.5

        # company is hard via regex → leave empty
        return result


class OCRLLMExtractor(BaseExtractor):

    def __init__(self, model: str = "llama3.2"):
        self.ocr = OCR()
        self.llm = OllamaLLM(model=config.OCR_LLM_MODEL)

    def build_prompt(self, text: str) -> str:
        return config.OCR_LLM_PROMPT + f"{text}"

    def extract(self, file_path: str) -> dict:

        text = self.ocr.extract_text(file_path)

        prompt = self.build_prompt(text)

        response = self.llm.generate(prompt)

        try:
            data = extract_json(response)
            return Receipt.model_validate(data)
        except Exception as e:
            print("JSON PARSE ERROR:", e)
            return empty_result()


class VisionExtractor(BaseExtractor):

    def __init__(self, model: str = "llama3.2"):
        self.llm = OllamaLLM(model=config.VISION_LLM_MODEL)

    def build_prompt(self) -> str:
        return config.VISION_LLM_PROMPT

    def extract(self, file_path: str) -> dict:

        prompt = self.build_prompt()

        # NOTE: image handling depends on Ollama vision model support
        response = self.llm.generate(prompt, image=file_path)

        try:
            data = extract_json(response)
            return Receipt.model_validate(data)
        except Exception as e:
            print("JSON PARSE ERROR:", e)
            return empty_result()