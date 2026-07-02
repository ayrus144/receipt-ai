# RECEIPT AI

This a small and lean project I am working on, to enable **accurate text extraction with local AI**  from receipts, for further downstream automation jobs. I use OLLAMA to enable efficient local deployment. Below is the high level project design that does a better job at explaining what the project is about.


### HIGH LEVEL DESIGN
```

         Receipt (Image)
                |
                ▼
     Preprocess + Extraction
                │
        ┌───────┼───────┐
        ▼       ▼       ▼
 OCR+Regex  OCR → LLM  VisionLLM
        │       │       │
        └───────┼───────┘
                ▼
         Consensus Engine
      (Per-field Confidence)
                │
       Final Structured JSON
                │
          SQLite Storage

```

**Important USAGE details:**
* The current solution works for Images only, but very soon this will also include support for PDFs.
* The [structure.py](structure.py) contains the output structure expected from the extraction modes.
* Changes in expected output structure (for now) also requires changing the LLM prompts in [config.py](config.py) and database format in [database.py](database.py).
* For more implementation details see [main ideas]() and [project directory](project-directory) sections.


### MAIN IDEAS:
* The guiding design principle is to make the solution as accurate as possible while keeping it fast.
* **Multi-pronged Approach**: The critical idea with many extraction modes is that one of the modes could possibly recover the field value/text detail we are looking for. This increases the potential for accurate output while also allowing for validation/ cross-checks.
* **Concurrency**: We deal with the downside in latency costs from using multiple modes by launching CPU-side Python threads for all the extractors to execute concurrently. This overlaps I/O-bound operations (ex. to/from ollama server) and native compute workloads (ex. OpenCV) and reduces total latency to approximately the duration of the slowest extractor.
* **Parallelism**: Ollama, which operates as an independent inference server, defaults to GPU offloading for LLM inference if it detects GPU(s) with sufficient VRAM (yes, it can use multiple GPUs too depending on backend configuration and model setup).
* **Consensus-based**: To enable for a synergizing effect from the many modes we use, I also introduce a consensus approach (confidence based) for each expected field. Confidence provided by LLM itself may not be a good idea since they could also be hallucinated, so looking to improve it with complementary approaches (see [future work](future-work,-ideas-and-thoughts)).


### PROJECT DIRECTORY:
* `config.py`     - set your respective LLM model and prompt used by OCR → LLM and VisionLLM modes.
* `structure.py`  - contains the output structure expected from the extractions (using pydantic). Used to check and enforce output strucutre of both the LLMs and the extractors.
* `ocr.py`        - simple OCR implementation using PaddleOCR. Used by mutiple extractors.
* `llm.py`        - flexible LLM implementation for OLLAMA models to support text and image modalities.
* `extractors.py` - implements all the extractor modes (OCR+Regex, OCR → LLM, VisionLLM).
* `consensus.py`  - simple consensus implementation. Uses assigned confidence scores (manually set for OCR+Regex, self-rated for LLM-based modes).
* `database.py`   - simple SQlite based output storage implementation.
* `main.py`       - implements extractors concurrently and stores the output as database.


### FUTURE WORK, IDEAS and THOUGHTS:
- [ ] Extend support for extracting fields from PDF documents.
- [ ] Enable DI for prompts, extractors and database formats based on structure.py.
- [ ] Add an option to log which extraction mode populated each field (and meta data like latency, confidence etc.). This would help users identify which extraction mode works best for them.
- [ ] Add a consistency checker after each extraction mode to enable checks for some fields we know should adhere to a pattern (ex. date can't have 32nd day/ 13th month). Using Pydantic model already checks if the output fields are structured as expected.

* For consensus in each field, I could have gone with majority vote among the extraction modes, but it can be misleading. Even ignoring failed fields extracted by some modes, a simple counter example is when mutiple modes detect and report `Subtotal` instead of `Total` as invoice amount.

Happy to hear from you if you have any ideas, or want to flag any issues or contribute in any manner :)