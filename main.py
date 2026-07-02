from concurrent.futures import ThreadPoolExecutor, as_completed

from extractors import RegexExtractor, OCRLLMExtractor, VisionExtractor
from consensus import ConsensusEngine
from database import Database


def run(file_path: str):

    # Initialize extractors
    regex_extractor = RegexExtractor()
    ocr_llm_extractor = OCRLLMExtractor()
    vision_extractor = VisionExtractor()

    extractors = {
        "regex": regex_extractor,
        "ocr_llm": ocr_llm_extractor,
        "vision": vision_extractor,
    }

    results = {}

    # Run in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:

        future_to_name = {
            executor.submit(ext.extract, file_path): name
            for name, ext in extractors.items()
        }

        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                results[name] = future.result()
            except Exception as e:
                print(f"[ERROR] {name}: {e}")
                results[name] = None

    # Consensus step
    merged = ConsensusEngine().merge([
        r for r in results.values() if r is not None
    ])

    # Storage
    Database(db="data/data.db").save(merged)

    return merged


if __name__ == "__main__":
    print(run("data/sample2.png"))