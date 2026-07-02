from paddleocr import PaddleOCR
import cv2


class OCR:
    """
    Wrapper around PaddleOCR.
    Returns raw extracted text for downstream processing.
    """

    def __init__(self, lang: str = "en", use_gpu: bool = False):
        self.engine = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
        )

    def _load_image(self, file_path: str):
        """
        Loads image from file path and converts it to format PaddleOCR expects.
        """
        image = cv2.imread(file_path)

        if image is None:
            raise ValueError(f"Could not read image: {file_path}")

        return image

    def extract_text(self, file_path: str) -> str:
        image = self._load_image(file_path)

        result = self.engine.predict(image)

        lines = []

        for item in result:
            # PaddleX-style outputs usually store text in "rec_texts"
            if isinstance(item, dict):

                texts = item.get("rec_texts", [])
                scores = item.get("rec_scores", [])

                for t, s in zip(texts, scores):
                    if s > 0.5:
                        lines.append(t)

            # fallback: ignore geometry-only outputs
            else:
                continue

        return "\n".join(lines)