# Dependency and model distribution license audit

**Research date:** 2026-09-18  
**Question:** Which licenses and distribution constraints apply to the document, OCR, table/chart, audio/video, vector/embedding, and model-runtime candidates identified in issues #4-#6, and which choices are compatible with a self-hosted TutorDesk release?  
**Evidence rule:** Primary sources only: upstream license files, upstream model cards, and provider terms.

> This is an engineering license audit, not legal advice. It establishes a safe default dependency policy and identifies items that need counsel or a product decision before public distribution.

## Decision

TutorDesk can ship the recommended stack as a self-hosted application if it adopts a **permissive core plus an explicit model-artifact allowlist**:

1. Ship permissively licensed code and reviewed weights with their required copyright, license, and NOTICE material. This includes Docling, pdfplumber, openpyxl, Tesseract with official English/Vietnamese data, faster-whisper/CTranslate2/Silero VAD, OpenAI Whisper weights, DePlot when enabled, PostgreSQL, pgvector, and the official cloud-provider SDKs.
2. Ship FFmpeg only as a pinned, reproducible **LGPL-only** build invoked as a separate executable. Its build must exclude `--enable-gpl` and `--enable-nonfree`, retain the exact source/build configuration, and satisfy LGPL redistribution requirements. Codec patent exposure is separate from copyright licensing and needs a release-territory review.
3. Do **not** ship or import PyMuPDF under the default policy. It is AGPL/commercial; adopt it only after buying a commercial license or deliberately licensing the relevant combined application under AGPL with counsel-confirmed compliance.
4. Do not bundle arbitrary Ollama generation or embedding weights. Ollama's runtime is MIT, but model licenses are independent. A model may be enabled only when TutorDesk records and approves its exact tag, content digest, license text/source, and restrictions. Prefer user-initiated upstream pulls instead of redistributing the weights in TutorDesk images.
5. Treat Gemini, OpenAI, and Anthropic as remote services, not redistributable model dependencies. TutorDesk may ship their permissive SDKs and a bring-your-own-key adapter, but must surface and enforce material service constraints. In particular, the current Gemini API terms make the adapter unsuitable for a product directed toward or likely to be accessed by people under 18.
6. Generate a release SBOM and third-party notice bundle from the final lockfiles and container image. This report audits the named architectural candidates; it cannot close the transitive dependency set before implementation versions and base images are locked.

This preserves the issue #4 extraction architecture and issue #6 PostgreSQL/pgvector decision without forcing TutorDesk into a strong-copyleft application license or silently redistributing unknown model terms.

## Release assumptions

The classification below assumes TutorDesk distributes Docker images and application source/binaries for local use, may later charge for the product, and has not selected an AGPL license for its own code. Running a dependency only in development is different from distributing it, but the release policy should not depend on a developer remembering that distinction.

The API key included in the original project prompt was not used. Provider credentials must remain runtime secrets supplied by the user.

## Candidate matrix

### Documents, PDF, tables, charts, and OCR

| Candidate | Upstream terms | Distribution decision | Required control |
|---|---|---|---|
| **Docling code and `docling-ibm-models` code** | MIT ([Docling license](https://github.com/docling-project/docling/blob/main/LICENSE), [`docling-ibm-models` license](https://github.com/docling-project/docling-ibm-models/blob/main/LICENSE)) | **Ship** | Retain the MIT copyright and permission notice in binary/source distributions. |
| **Docling layout/TableFormer weights** | The official model card declares CDLA-Permissive-2.0 and Apache-2.0, rather than treating weights as covered by Docling's MIT code license ([official model card](https://huggingface.co/docling-project/docling-models/blob/main/README.md)). CDLA-Permissive 2.0 permits use, modification, and sharing, but sharing requires the agreement text to accompany the data ([CDLA text](https://cdla.dev/permissive-2-0/)). | **Ship only from an artifact allowlist** | Pin repository revision and file digests. Carry both declared license texts unless the locked artifact has an unambiguous per-file mapping. Preserve Apache NOTICE material if present. |
| **pdfplumber / pdfminer path** | MIT ([pdfplumber license](https://github.com/jsvine/pdfplumber/blob/stable/LICENSE.txt)) | **Ship; preferred PDF inspection path** | Retain notice. Audit the locked transitive `pdfminer.six` version in the release SBOM. |
| **PyMuPDF / MuPDF** | Dual AGPL and commercial licensing; upstream directs users who cannot meet AGPL to obtain a commercial license ([official licensing statement](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright), [AGPL text in distribution](https://github.com/pymupdf/PyMuPDF/blob/main/COPYING)) | **Exclude by default** | A commercial license or deliberate AGPL product decision is a prerequisite. Do not make it an unreviewed optional extra: importing it into the backend still creates a distribution question. |
| **openpyxl** | MIT/Expat ([upstream license](https://foss.heptapod.net/openpyxl/openpyxl/-/blob/branch/3.1/LICENCE.rst)) | **Ship** | Retain notice; use it for native OOXML chart/cell extraction before vision inference. |
| **Tesseract engine** | Apache-2.0; upstream also calls out Leptonica as BSD-2-Clause and warns that other dependencies have their own licenses ([official README](https://github.com/tesseract-ocr/tesseract/blob/main/README.md), [Apache license](https://github.com/tesseract-ocr/tesseract/blob/main/LICENSE)) | **Ship** | Include Apache license/NOTICE obligations and transitive notices for the actual packaged build. |
| **Official `eng` and `vie` Tesseract trained data** | The official `tessdata`, `tessdata_fast`, and `tessdata_best` repositories are Apache-2.0; Tesseract documents these as its official trained-data sources ([data documentation](https://github.com/tesseract-ocr/tessdoc/blob/main/Data-Files.md), [`tessdata` license](https://github.com/tesseract-ocr/tessdata/blob/main/LICENSE)) | **Ship exact reviewed files** | Pin repository/tag and SHA-256 for `eng.traineddata` and `vie.traineddata`; include the Apache license. Do not substitute community models without a new audit. |
| **DePlot / Pix2Struct chart-to-table** | The Google DePlot model card declares Apache-2.0 and distributes the model weights; Pix2Struct code is also Apache-2.0 ([DePlot model card](https://huggingface.co/google/deplot), [Pix2Struct license](https://github.com/google-research/pix2struct/blob/main/LICENSE)) | **Compatible but optional** | Download by reviewed revision/digest, include Apache notices, and keep model-derived chart values review-required for evidentiary reasons independent of licensing. |

Docling itself warns that its code license does not automatically govern every model it can load. Therefore, enabling arbitrary Docling VLM presets or OCR extras must go through the same artifact gate as Ollama models; the package's MIT license is not a blanket model-license approval.

### Audio and video

| Candidate | Upstream terms | Distribution decision | Required control |
|---|---|---|---|
| **FFmpeg / ffprobe** | Most FFmpeg is LGPL-2.1-or-later. Enabling GPL parts changes the resulting FFmpeg license to GPL; `--enable-nonfree` can produce an unredistributable binary. External libraries can also change the effective license ([upstream license matrix](https://ffmpeg.org/doxygen/trunk/md_LICENSE.html), [official compliance checklist and patent notes](https://ffmpeg.org/legal.html)). | **Ship conditionally** | Build without `--enable-gpl`, `--enable-nonfree`, or GPL libraries such as x264/x265; invoke the executable for ingestion and dynamically link only where a Python dependency requires libraries; publish the exact corresponding source, patches, configure line, and notices; permit replacement/relinking as required. Review codec patents separately before commercial distribution. |
| **faster-whisper** | MIT ([license](https://github.com/SYSTRAN/faster-whisper/blob/master/LICENSE)) | **Ship** | Retain notice and audit the locked native wheels. |
| **PyAV (faster-whisper media decode)** | BSD-3-Clause ([license](https://github.com/PyAV-Org/PyAV/blob/main/LICENSE.txt)) | **Ship conditionally** | Retain its notice/disclaimer. Do not accept an opaque wheel's bundled multimedia libraries: build or verify PyAV against the same audited LGPL-only FFmpeg shared libraries, or prove the selected wheel's complete library/license inventory. |
| **CTranslate2** | MIT ([license](https://github.com/OpenNMT/CTranslate2/blob/master/LICENSE)) | **Ship CPU runtime** | Retain notice. Treat CUDA/cuDNN/NVIDIA redistribution as a separate GPU-image audit; do not put those binaries in the default CPU image. |
| **Silero VAD** | MIT ([license](https://github.com/snakers4/silero-vad/blob/master/LICENSE)) | **Ship reviewed runtime/weights** | Pin release and model digest; retain notice. |
| **OpenAI Whisper code and weights** | The upstream project explicitly releases both code and model weights under MIT ([official README](https://github.com/openai/whisper#license), [license](https://github.com/openai/whisper/blob/main/LICENSE)) | **Ship or download** | Retain MIT notice and pin the selected model/checksum. A converted faster-whisper artifact must retain the same source-model license and derivation metadata. |
| **WhisperX** | BSD-2-Clause ([license](https://github.com/m-bain/whisperX/blob/main/LICENSE)) | **Code is compatible; do not enable arbitrary alignment/diarization models** | Retain BSD notice. Each separately downloaded alignment or diarization model needs its own license approval; the wrapper's BSD license does not cover those weights. |

The safest first release is CPU-first. GPU acceleration is technically optional and introduces separately licensed vendor redistributables that were not selected in issues #4-#6.

### Persistence, vector search, and embeddings

| Candidate | Upstream terms | Distribution decision | Required control |
|---|---|---|---|
| **PostgreSQL** | PostgreSQL License, a permissive BSD/MIT-like license ([official license](https://www.postgresql.org/about/licence/)) | **Ship; authoritative store** | Include the copyright/license text in the database image's notices. |
| **pgvector** | PostgreSQL License ([upstream license](https://github.com/pgvector/pgvector/blob/master/LICENSE)) | **Ship; selected vector extension** | Retain license text and pin extension/image digest. |
| **SQLite** | Public domain for deliverable code and documentation ([official copyright statement](https://www.sqlite.org/copyright.html)) | **Compatible but deferred** | Audit build scripts and any extensions separately if a no-Docker edition is later created. |
| **sqlite-vec** | Dual Apache-2.0/MIT ([Apache license](https://github.com/asg017/sqlite-vec/blob/main/LICENSE-APACHE), [MIT license](https://github.com/asg017/sqlite-vec/blob/main/LICENSE-MIT)) | **Compatible but deferred** | Select and carry one valid license path plus required notices; maturity, not licensing, remains the blocker. |
| **Chroma** | Apache-2.0 ([license](https://github.com/chroma-core/chroma/blob/main/LICENSE)) | **License-compatible but architecturally rejected as system of record** | No additional license blocker if revisited; audit its full server image and dependencies then. |
| **Qdrant server/client** | Apache-2.0 ([server license](https://github.com/qdrant/qdrant/blob/master/LICENSE), [Python client license](https://github.com/qdrant/qdrant-client/blob/master/LICENSE)) | **License-compatible but deferred** | If a measured trigger adds it, include Apache notices and audit the selected container image. |

No local embedding-weight default was selected in issues #5-#6. That is important: a permissive vector database license says nothing about the model that creates the vectors. Cloud embedding models remain services; an Ollama embedding model must pass the per-digest model gate below before it can become a supported default.

### Model runtimes and provider adapters

| Candidate | Code/distribution terms | Service or model terms | Decision |
|---|---|---|---|
| **Google Gen AI Python SDK** | Apache-2.0 ([license](https://github.com/googleapis/python-genai/blob/main/LICENSE)) | Gemini API terms apply at runtime; no Gemini weights are distributed. | **Ship SDK/adapter**, with runtime eligibility gate. |
| **OpenAI Python SDK** | Apache-2.0 ([license](https://github.com/openai/openai-python/blob/main/LICENSE)) | OpenAI's Services Agreement permits integrating the API into customer applications and making them available to end users, while reserving the service/model IP and imposing use restrictions ([agreement sections 2-4 and 9](https://openai.com/policies/services-agreement/)). | **Ship SDK/adapter**, bring your own key. |
| **Anthropic Python SDK** | MIT ([license](https://github.com/anthropics/anthropic-sdk-python/blob/main/LICENSE)) | Commercial terms permit powering customer products, assign output rights to the customer to the extent permitted, prohibit reverse engineering/competing-model use, and require user notice that factual output needs checking ([commercial terms](https://www.anthropic.com/legal/commercial-terms)). | **Ship SDK/adapter**, bring your own key and required notice. |
| **Ollama runtime** | MIT ([license](https://github.com/ollama/ollama/blob/main/LICENSE)) | Each local model has independent terms. Ollama's Modelfile has a `LICENSE` instruction and `/api/show` exposes model license metadata ([Modelfile reference](https://github.com/ollama/ollama/blob/main/docs/modelfile.mdx), [API schema](https://github.com/ollama/ollama/blob/main/docs/openapi.yaml)). | **Support; do not bundle arbitrary weights.** Prefer connecting to user-installed Ollama. If runtime binaries are bundled, retain MIT notice. |
| **Ollama generation/embedding tags** | Not covered by Ollama's MIT runtime license | License varies by model, quantization, adapter, and upstream conversion. A tag can move while the content digest changes. | **Deny until reviewed.** Store endpoint, tag, digest, full license text/source, upstream model, and approval. Re-approve on digest change. |

## Provider service constraints that affect product scope

Remote APIs avoid model-weight redistribution, but they are not license-free infrastructure. Their current terms impose product behavior that must be reflected in requirements and onboarding.

### Gemini is development-default only until the learner-age decision is resolved

The Gemini API Additional Terms effective 2026-03-23 state that API users must be at least 18 and that API clients may not be directed toward or likely accessed by people under 18. They also describe AI Studio/Gemini API as professional/business rather than consumer use and restrict regions ([Gemini terms, Age Requirements and Use Restrictions](https://ai.google.dev/gemini-api/terms)). This is materially stricter than merely requiring parental consent.

Consequences:

- `gemini-3.8-flash` may remain the development test model only for eligible adult professional/business use with synthetic or non-sensitive fixtures.
- The production Gemini adapter must stay disabled until TutorDesk either explicitly targets adults and records the required acknowledgement, or moves that workload to a Google offering whose applicable terms have been separately verified for the chosen audience.
- A generic “education” label is not enough; the launch audience and provider eligibility must be an explicit product decision.

The same terms say content sent through unpaid Gemini services may be used to improve Google's products and may be reviewed by humans, and instruct users not to submit sensitive, confidential, or personal information. Paid services do not use prompts/responses to improve products, although limited safety logging still applies ([Gemini terms, Unpaid and Paid Services](https://ai.google.dev/gemini-api/terms)). TutorDesk must therefore:

- use only synthetic fixtures with unpaid quota during development;
- require an active paid/billing-backed Gemini project before sending real learner sources, memory, quiz results, or Boardroom packets; and
- show a provider/data-boundary disclosure before first use.

OpenAI's current Services Agreement allows minors only with parental/guardian consent and makes the customer responsible for input rights and output review ([OpenAI agreement](https://openai.com/policies/services-agreement/)). Anthropic's commercial terms permit powering products but require notice that factual assertions need independent checking ([Anthropic terms](https://www.anthropic.com/legal/commercial-terms)). These requirements fit TutorDesk's citation verifier and approval flows, but they belong in provider acceptance tests and UI copy, not only legal documentation.

## Required compliance architecture

### 1. License and model registry

Every shipped package, native binary, container, and model artifact must have a machine-readable record:

```yaml
component: docling-tableformer
kind: model
version_or_revision: <immutable revision>
sha256: <artifact digest>
source_url: <upstream URL>
licenses:
  - CDLA-Permissive-2.0
  - Apache-2.0
license_text_paths:
  - licenses/CDLA-Permissive-2.0.txt
  - licenses/Apache-2.0.txt
redistribution: approved
reviewed_at: 2026-09-18
```

Default policy:

- auto-allow MIT, BSD-2/3-Clause, Apache-2.0, PostgreSQL License, and public-domain artifacts when notices are complete;
- conditional review for LGPL, CDLA, or custom terms;
- deny AGPL, GPL, non-commercial, research-only, no-derivatives, unknown, or missing-license artifacts unless an explicit product/license decision overrides the default;
- treat model weights independently from their loader/runtime; and
- invalidate approval when the content digest, source, license text, or upstream model changes.

### 2. Build and CI gates

Before a release image is publishable, CI must:

1. resolve lockfiles and container packages into an SBOM with versions, source URLs, licenses, and hashes;
2. fail on an unapproved or missing license and on any notice absent from the generated `THIRD_PARTY_NOTICES` bundle;
3. inspect `ffmpeg -buildconf` and fail if GPL/nonfree flags or unapproved external libraries are present;
4. archive the corresponding FFmpeg source, patches, and build recipe alongside the release;
5. verify every bundled model against the allowlist and reject moving tags without a pinned digest;
6. scan every final container layer, not only Python/JavaScript manifests; and
7. compare the generated inventory with the previous release so a license change cannot arrive as a routine dependency update.

### 3. Runtime gates

- Provider setup must link the currently applicable terms and ask the user to attest that they are eligible to use that provider; terms URLs and acknowledgement version are audit metadata, not blanket acceptance on the user's behalf.
- Gemini must additionally enforce the decided age/audience and paid-project policy before real learner data can leave the machine.
- Ollama `/api/show` license metadata and content digest must be recorded before a model is enabled. Empty or custom license text routes to manual review; it is never interpreted as permission.
- The UI must show whether an artifact is local, bundled, downloaded from an upstream source, or sent to a cloud service.
- Deleting a model does not delete its historical license/provenance record; old session provenance must continue to explain which artifact produced an output.

## First-release allowlist

The following is safe to put on the implementation backlog now:

- Docling MIT code plus only the pinned default layout/TableFormer artifacts documented above;
- pdfplumber, openpyxl, Tesseract, official `eng`/`vie` Tesseract data;
- an audited LGPL-only FFmpeg/ffprobe build, with PyAV built or verified against the same approved shared libraries;
- faster-whisper, CTranslate2 CPU, Silero VAD, and a pinned MIT Whisper model conversion;
- PostgreSQL + pgvector;
- official Google, OpenAI, and Anthropic SDKs;
- an Ollama HTTP adapter that connects to a user-managed runtime and begins with no pre-approved model tags.

Explicitly outside the default release:

- PyMuPDF;
- GPL or nonfree FFmpeg builds and GPL codec libraries;
- CUDA/cuDNN/NVIDIA redistribution;
- arbitrary Docling VLM, Ollama, alignment, diarization, or embedding weights;
- DePlot bundled by default (it is license-compatible, but should remain an optional reviewed download until the raster-chart quality spike justifies its size and value);
- Chroma, Qdrant, SQLite/sqlite-vec as production state foundations, consistent with issue #6.

## Remaining fog and follow-up decisions

1. **Learner age and launch audience:** decide whether TutorDesk is explicitly adult-only. If minors are in scope, Gemini API cannot be the production default under the current terms, even with parental consent.
2. **TutorDesk's own license:** select it before accepting dependencies with reciprocal terms or external contributions. The default allowlist does not require a copyleft application license.
3. **Commercial codec/patent review:** the LGPL FFmpeg decision does not answer patent-pool obligations in every release territory.
4. **Production embedding model:** approve a specific cloud service or exact local model/digest before the first retrieval index is created.
5. **GPU distribution:** audit the exact CUDA/cuDNN/vendor stack only if a separately distributed GPU image becomes a release requirement.

These are not reasons to change the core architecture. They are release gates around audience, artifact selection, and distribution packaging.

## Primary source index

- Document stack: [Docling license](https://github.com/docling-project/docling/blob/main/LICENSE), [Docling model card](https://huggingface.co/docling-project/docling-models/blob/main/README.md), [CDLA-Permissive-2.0](https://cdla.dev/permissive-2-0/), [pdfplumber license](https://github.com/jsvine/pdfplumber/blob/stable/LICENSE.txt), [PyMuPDF licensing](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright), [openpyxl license](https://foss.heptapod.net/openpyxl/openpyxl/-/blob/branch/3.1/LICENCE.rst).
- OCR and chart models: [Tesseract license/readme](https://github.com/tesseract-ocr/tesseract/blob/main/README.md), [official trained-data documentation](https://github.com/tesseract-ocr/tessdoc/blob/main/Data-Files.md), [DePlot model card](https://huggingface.co/google/deplot), [Pix2Struct license](https://github.com/google-research/pix2struct/blob/main/LICENSE).
- Audio/video: [FFmpeg license](https://ffmpeg.org/doxygen/trunk/md_LICENSE.html), [FFmpeg legal/compliance page](https://ffmpeg.org/legal.html), [faster-whisper license](https://github.com/SYSTRAN/faster-whisper/blob/master/LICENSE), [PyAV license](https://github.com/PyAV-Org/PyAV/blob/main/LICENSE.txt), [CTranslate2 license](https://github.com/OpenNMT/CTranslate2/blob/master/LICENSE), [Silero VAD license](https://github.com/snakers4/silero-vad/blob/master/LICENSE), [Whisper license statement](https://github.com/openai/whisper#license), [WhisperX license](https://github.com/m-bain/whisperX/blob/main/LICENSE).
- Persistence/vector: [PostgreSQL license](https://www.postgresql.org/about/licence/), [pgvector license](https://github.com/pgvector/pgvector/blob/master/LICENSE), [SQLite public-domain statement](https://www.sqlite.org/copyright.html), [sqlite-vec licenses](https://github.com/asg017/sqlite-vec), [Chroma license](https://github.com/chroma-core/chroma/blob/main/LICENSE), [Qdrant license](https://github.com/qdrant/qdrant/blob/master/LICENSE).
- Provider/runtime: [Google Gen AI SDK license](https://github.com/googleapis/python-genai/blob/main/LICENSE), [Gemini API terms](https://ai.google.dev/gemini-api/terms), [OpenAI SDK license](https://github.com/openai/openai-python/blob/main/LICENSE), [OpenAI Services Agreement](https://openai.com/policies/services-agreement/), [Anthropic SDK license](https://github.com/anthropics/anthropic-sdk-python/blob/main/LICENSE), [Anthropic Commercial Terms](https://www.anthropic.com/legal/commercial-terms), [Ollama runtime license](https://github.com/ollama/ollama/blob/main/LICENSE), [Ollama Modelfile license field](https://github.com/ollama/ollama/blob/main/docs/modelfile.mdx), [Ollama API model-license field](https://github.com/ollama/ollama/blob/main/docs/openapi.yaml).
