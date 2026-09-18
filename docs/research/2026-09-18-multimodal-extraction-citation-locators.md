# Multimodal extraction and precise citation locators for TutorDesk

**Research date:** 2026-09-18

**Question:** Which primary-source-supported extraction, transcription, segmentation, and locator techniques can provide verifiable citations for text, images, tables, charts, audio, and video in a local-first Python stack?

## Decision

TutorDesk should build a local **Evidence Ledger** around immutable source revisions and W3C-inspired compound selectors. A citation must identify a content-hashed source revision and enough selectors to reopen and visibly verify the evidence. Extracted Markdown, RAG chunks, transcripts, chart tables, embeddings, and model descriptions are derived artifacts; none is the citation source of truth.

Use this stack behind replaceable adapters:

1. **Docling** as the default local document normalizer and structure-aware chunking front door. Its `DoclingDocument` already represents text, tables, and pictures, and its layout provenance carries page number, bounding box, and character span. Its current format matrix includes PDF, Office files, HTML, EPUB, images, audio, video-audio transcription, and WebVTT ([supported formats](https://docling-project.github.io/docling/usage/supported_formats/), [provenance schema](https://docling-project.github.io/docling/reference/docling_document/), [MIT license](https://github.com/docling-project/docling/blob/main/LICENSE)). Treat that provenance as an extraction result, not as a replacement for TutorDesk's ledger.
2. **pdfplumber** as the permissively licensed PDF inspection and verification path for machine-generated PDFs. It exposes character/word coordinates, lines, rectangles, images, table cells, and visual table debugging; it explicitly says it works best on machine-generated rather than scanned PDFs and does not provide OCR ([project documentation](https://github.com/jsvine/pdfplumber/blob/stable/README.md), [MIT license](https://github.com/jsvine/pdfplumber/blob/stable/LICENSE.txt)).
3. **Tesseract 5** for local OCR of scans and image regions, storing word/line boxes and engine confidence. Its TSV and hOCR outputs include hierarchy and bounding boxes; the API exposes per-word confidence and boxes. Official language packs include both `eng` and `vie` ([output formats](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html), [iterator API](https://tesseract-ocr.github.io/tessdoc/APIExample.html), [language list](https://github.com/tesseract-ocr/tesseract/blob/main/doc/tesseract.1.asc)). Tesseract confidence is not a calibrated probability, so it cannot by itself justify a factual threshold ([Tesseract paper](https://tesseract-ocr.github.io/docs/tesseracticdar2007.pdf)).
4. **FFmpeg/ffprobe plus faster-whisper** for local audio/video demuxing, canonical PCM, speech segmentation, multilingual transcription, and timestamps. ffprobe can enumerate streams, packets, frames, PTS, and duration ([ffprobe documentation](https://ffmpeg.org/ffprobe-all.html)). Faster-whisper exposes segment and word timestamps and an integrated Silero VAD filter ([project documentation](https://github.com/SYSTRAN/faster-whisper/blob/master/README.md)); OpenAI Whisper includes Vietnamese and derives word timings from cross-attention plus dynamic time warping ([language registry](https://github.com/openai/whisper/blob/main/whisper/tokenizer.py), [transcription implementation](https://github.com/openai/whisper/blob/main/whisper/transcribe.py)). Word times are estimates, not frame-accurate ground truth.
5. **Native chart data first; model extraction second.** For OOXML spreadsheets and presentations, preserve the worksheet/series references and embedded workbook data when present. OOXML standardizes the package and markup vocabularies, and a native spreadsheet chart can reference worksheet ranges for its categories and values ([ECMA-376](https://ecma-international.org/publications-and-standards/standards/ecma-376/), [openpyxl chart reference example](https://openpyxl.readthedocs.io/en/stable/charts/bar.html)). For a rasterized chart, a local chart-to-table model such as DePlot is only a candidate derived extractor. DePlot's primary contribution is translating a plot image to a linearized table before reasoning, not proving that every recovered value is correct ([paper](https://aclanthology.org/2023.findings-acl.660/), [released code](https://github.com/google-research/pix2struct)). Unverified chart values must not silently become citable facts.

This is not a recommendation to let one library define the domain model. Adapters should emit TutorDesk-owned `SourceRevision`, `Representation`, `EvidenceAnchor`, and `Derivation` records so that parsers and models can be replaced without breaking citations.

## 1. What “verifiable citation” means

A citation is verifiable only if the application can perform all of the following without rerunning an AI model:

1. resolve the exact immutable input revision;
2. locate the quoted text, table cells, image region, audio interval, or video interval in that revision or in a reproducible rendering of it;
3. show the evidence in a viewer, with text highlight, spatial overlay, or bounded playback;
4. show how any derived representation was produced;
5. detect stale, missing, or mismatched evidence and abstain instead of displaying a plausible-looking citation.

The W3C Web Annotation model is a useful selector vocabulary rather than a complete storage design. It defines `TextQuoteSelector`, `TextPositionSelector`, `CssSelector`, `XPathSelector`, `FragmentSelector`, and refinements that can combine selectors ([Web Annotation Data Model](https://www.w3.org/TR/annotation-model/#selectors), [Selectors and States](https://www.w3.org/TR/selectors-states/)). W3C Media Fragments adds half-open temporal ranges and top-left `xywh` spatial regions for audio, images, and video ([Media Fragments URI 1.0](https://www.w3.org/TR/media-frags/)). W3C PROV supplies the vocabulary for derived entities and generating activities, including `wasDerivedFrom` and `wasGeneratedBy` ([PROV-O](https://www.w3.org/TR/prov-o/)).

TutorDesk should adopt those semantics in a compact application schema, not require RDF internally.

### 1.1 Required source identity

Every ingest creates a new immutable `SourceRevision` even when it belongs to an existing logical source:

```json
{
  "source_id": "src_...",
  "revision_id": "rev_sha256:...",
  "blob_sha256": "...",
  "media_type": "application/pdf",
  "byte_length": 123456,
  "original_name": "lecture-notes.pdf",
  "ingested_at": "2026-09-17T...Z"
}
```

The raw blob is content-addressed and never overwritten. Re-importing edited bytes creates a new revision. Deletion may remove the blob under the application's deletion policy, but any remaining anchor must then resolve as deliberately unavailable rather than drifting to a different revision.

### 1.2 Required extraction provenance

Every normalized document, render, transcript, OCR layer, table, or chart table is a `Representation` generated from a revision:

```json
{
  "representation_id": "rep_...",
  "source_revision_id": "rev_sha256:...",
  "kind": "docling-document",
  "artifact_sha256": "...",
  "generator": {
    "name": "docling",
    "version": "pinned-version",
    "model_digests": ["sha256:..."],
    "config_sha256": "..."
  },
  "created_at": "..."
}
```

Model weights, parser version, normalization settings, OCR languages, render DPI, coordinate transforms, and prompts used for model-derived extraction are part of the derivation record. This is what makes a future re-extraction comparable rather than destructive.

### 1.3 Compound evidence anchors

An `EvidenceAnchor` uses redundant selectors. A structural or spatial selector gives navigation; an exact quote/digest verifies that navigation still resolves to the intended evidence.

```json
{
  "anchor_id": "anc_...",
  "source_revision_id": "rev_sha256:...",
  "representation_id": "rep_...",
  "modality": "document-text",
  "selectors": [
    {"type": "page", "number": 12},
    {
      "type": "xywh",
      "unit": "page-point",
      "origin": "top-left",
      "x": 72.1,
      "y": 144.0,
      "w": 388.4,
      "h": 39.2,
      "canvas_w": 612.0,
      "canvas_h": 792.0
    },
    {"type": "text-position", "start": 418, "end": 491, "normalization": "NFC-LF-v1"},
    {"type": "text-quote", "exact": "...", "prefix": "...", "suffix": "..."}
  ],
  "evidence_sha256": "...",
  "extraction_class": "verbatim",
  "verification": "machine-resolved"
}
```

Offsets are zero-based and end-exclusive. The schema must always name the text normalization profile and coordinate system. Spatial selectors include canvas dimensions so a renderer can transform them safely. Store native coordinates where useful, but also store one canonical top-left coordinate system for the viewer.

## 2. Locator contract by modality

| Evidence | Required locator | Verification payload | Notes |
|---|---|---|---|
| Plain text / Markdown / code | revision hash + UTF-8 byte or normalized character range + line range + exact quote/context | exact text and digest | RFC 5147 defines character/line fragments and optional integrity information for `text/plain` ([RFC 5147](https://www.rfc-editor.org/rfc/rfc5147)). |
| HTML / EPUB | revision hash + package part/URL + element ID or XPath/CSS selector + text position + text quote | exact text and DOM/package digest | EPUB defines Canonical Fragment Identifiers for arbitrary publication content ([EPUB 3.3](https://www.w3.org/TR/epub-33/)); keep a quote fallback because structure changes. |
| PDF / paged document text | revision hash + 1-based page + top-left page box + item/character span + quote/context | highlighted page render and exact text | PDF text order can differ from visual reading order. Coordinates are necessary but not sufficient. |
| Reflowable DOCX | revision hash + OOXML part/XPath or paragraph/run identity + text position/quote; optional canonical-render page/box | native text and optional rendered highlight | Do not pretend that a reflowable source has stable pages. A PDF rendering is a separate representation with its own hash. |
| PPTX | revision hash + slide relationship/id + shape id/path + text span; rendered slide `xywh` | slide/shape render and exact text | For chart claims, add the underlying series/cell selector where available. |
| XLSX / CSV | revision hash + sheet/table name + A1 cell/range (or CSV row/column) + formula/value mode | selected cells, headers, raw formula and cached value | Cite the smallest cells that support the claim; do not cite a whole workbook. |
| Image / scan | revision hash + pixel `xywh` (or polygon extension) + image dimensions + OCR quote/word ids | cropped original pixels and OCR token boxes | Media Fragments defines top-left pixel/percent `xywh`. Hash the crop recipe, not only a lossy crop file. |
| Extracted table in a document/image | parent page/image anchor + table box + row/column/cell ids + cell boxes + header relations | highlighted table/cells and canonical cell matrix | A table reconstruction is derived. Keep each cell linked to the source words/region. |
| Chart | parent page/image/slide anchor + chart box; native series/data ranges if available; otherwise derived chart-table cell anchors | chart crop, labels/legend/axes, and extracted table diff | A model-derived numeric value requires verification; a chart-region citation alone proves location, not the decoded number. |
| Audio | revision hash + audio stream index + sample range on canonical PCM + time range + transcript quote/word ids | bounded playback with waveform/transcript highlight | Time is half-open. Sample ranges are exact for the canonical PCM; word boundaries remain estimated. |
| Video speech | video revision + audio stream + time/sample range + transcript quote | bounded playback and transcript highlight | Preserve the parent video's timeline when VAD removes silence. |
| Video visual evidence | video revision + video stream + PTS/time base + time interval + frame digest + optional `xywh` | frame/clip playback with region overlay | Use source PTS rather than only a decoded frame number, especially for variable-frame-rate media. |
| Existing captions | caption revision or embedded track + cue id + cue start/end + quote | cue and synchronized playback | WebVTT defines cues as time-aligned payloads with start/end offsets ([WebVTT](https://www.w3.org/TR/webvtt1/)). |

An answer citation should render a friendly label such as `Lecture notes, p. 12, table 2, cells R3C2–R4C4` or `Week 4 recording, 12:31–12:48`. The label is presentation. The anchor ID is the durable contract.

## 3. Extraction and segmentation pipeline

### 3.1 Ingest and probe

1. Stream the original bytes into local content-addressed storage while computing SHA-256.
2. Detect media type from content as well as extension; record both and quarantine mismatches for parser hardening.
3. Use ffprobe for audiovisual stream metadata before decoding. Preserve stream index, codec parameters, duration, time base, and rotation/display metadata.
4. Create a new source revision before any extraction starts. Extraction failure must not erase the source.

### 3.2 Documents, images, tables, and charts

1. Convert supported documents locally to a lossless Docling JSON representation. Keep each item's native `prov` references and original document path.
2. For PDFs, independently retain page geometry and word/character boxes. Docling provides broad structure; pdfplumber provides a transparent coordinate/table inspection path. PyMuPDF is technically attractive because `get_text("words")`, image rectangles, OCR text pages, and `find_tables()` expose page boxes and cells ([text extraction](https://pymupdf.readthedocs.io/en/latest/recipes-text.html), [page API](https://pymupdf.readthedocs.io/en/latest/page.html)), but it is dual-licensed AGPL/commercial and therefore needs an explicit product licensing decision before adoption ([official license statement](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)).
3. Use native text when it is present and coherent. Invoke OCR per page/region only when there is no usable text layer or when a quality check flags it. Retain native and OCR representations separately; never interleave them into an untraceable duplicate text stream.
4. OCR at a recorded render DPI with `eng+vie` (or detected language set). Store token, line, block, confidence, and image-pixel box. Transform boxes back to the canonical page/image coordinate system and test the transform.
5. Preserve tables as a grid plus spans, headers, captions, and per-cell source anchors. Pdfplumber exposes table/cell bounding boxes and its algorithm is inspectable; Docling's schema also keeps table cells and can retain cell boxes ([pdfplumber table extraction](https://github.com/jsvine/pdfplumber/blob/stable/README.md#extracting-tables), [Docling document source](https://github.com/docling-project/docling-core/blob/main/docling_core/types/doc/document.py)).
6. For charts, extract native series/category/value references before invoking vision. If only pixels exist, save the chart region and OCR anchors for title, axes, ticks, labels, and legend. A DePlot- or VLM-produced table is `model-derived`, linked to that region. Numeric claims remain review-required until a deterministic rule or user verifies relevant values.

### 3.3 Audio and video

1. Preserve the container revision, then create a reproducible canonical audio representation (for example mono PCM at the transcription model's declared rate) while retaining the exact FFmpeg command/config and artifact hash. OpenAI Whisper's reference loader uses FFmpeg to decode, down-mix, and resample audio ([audio loader](https://github.com/openai/whisper/blob/main/whisper/audio.py)).
2. Run VAD to identify speech intervals, but maintain a piecewise map from VAD-packed samples back to the original timeline. Faster-whisper's VAD can remove silence; citations must never use the compressed timeline ([VAD documentation](https://github.com/SYSTRAN/faster-whisper/blob/master/README.md#vad-filter)).
3. Transcribe with an explicitly selected language (`en`, `vi`, or auto-detected plus recorded probability), model digest, decoding settings, and word timestamps. Store segment-level confidence signals such as average log probability and no-speech probability without calling them calibrated truth.
4. Emit a versioned WebVTT representation for navigation. Each cue maps back to original sample/time ranges and to word records.
5. If product testing shows that word-level timing is too loose, add forced alignment behind a separate adapter. WhisperX demonstrates the VAD + ASR + phoneme-alignment pattern, but alignment model availability and quality are language-dependent and need a Vietnamese evaluation before it becomes a default ([WhisperX paper](https://arxiv.org/abs/2303.00747), [implementation](https://github.com/m-bain/whisperX)).
6. For video, keep speech and visual evidence as separate tracks. Use ffprobe frame PTS/time base to extract candidate keyframes. Scene boundaries can improve retrieval granularity, but a scene ID is not a citation; visual citations use time/PTS plus frame digest and region.

### 3.4 Structure-aware RAG segmentation

Chunking is an index concern, not an evidence-addressing concern.

- Start from semantic units: heading with following paragraphs, list, table row group with repeated headers, figure/chart with caption, transcript turn/cue, or video scene segment.
- Split only oversized units, keeping sentence, table-row, and cue boundaries where possible.
- Merge small adjacent units only when their structural context matches.
- Every chunk stores an ordered list of evidence anchor IDs and covered subranges. A chunk that combines two pages or modalities keeps both anchors.
- Context added for embeddings—heading trails, table headers, speaker names—is marked as context and never quoted as if it occurred inside the evidence span.
- Retrieval returns chunks; generation receives resolved evidence units and their anchors. The final citation targets anchors, never vector IDs or chunk ordinal numbers.

Docling's native `HierarchicalChunker` starts from document elements, while `HybridChunker` adds tokenizer-aware splitting and merging; table headers can be repeated when a table spans chunks ([chunking documentation](https://docling-project.github.io/docling/concepts/chunking/)). This is a sound baseline if TutorDesk persists the original Docling item references and replaces Docling chunk IDs with its own versioned index records.

## 4. Evidence classes and answer policy

Every evidence unit declares one extraction class:

| Class | Examples | May directly support an answer claim? |
|---|---|---|
| `verbatim` | native document text, spreadsheet cell value, existing caption cue | Yes, after anchor resolution. |
| `machine-read` | OCR text, ASR transcript, PDF table reconstruction | Yes when quality gates pass; UI identifies OCR/ASR and allows opening the source. Material ambiguity requires abstention or qualification. |
| `computed` | sum calculated from cited spreadsheet cells, duration derived from timestamps | Yes when the deterministic operation and input anchors are stored. |
| `model-derived` | raster chart-to-table output, image description, inferred speaker label | Not as an unqualified fact. It requires corroboration, deterministic validation, or user approval; otherwise report it as uncertain or abstain. |

The answer composer must produce a claim-to-anchor map. A deterministic verifier then enforces:

1. every factual claim has at least one allowed anchor;
2. every cited anchor resolves against the claimed source revision;
3. text quotes match after the named normalization;
4. page/space/time ranges are within bounds;
5. table citations include the cells used, not only the table caption;
6. derived claims link to their input anchors and operation;
7. unsupported claims are removed or explicitly presented as questions/uncertainty.

“Citation coverage” and “citation correctness” are separate. Full coverage with the wrong regions is still failure.

## 5. Validation plan

Build a checked-in bilingual golden corpus before treating ingestion as complete. It should contain licensed or synthetic fixtures for:

- English and Vietnamese born-digital PDF, two-column PDF, ligatures, rotated text, and scanned PDF;
- DOCX with headings/tables/images and PPTX with speaker-visible text plus native and raster charts;
- XLSX with formulas, cached values, merged cells, hidden rows, and native charts;
- photographs and scans with Vietnamese diacritics, rotation, low contrast, and mixed languages;
- tables with ruled, borderless, merged, and multi-page structures;
- clean/noisy audio with English, Vietnamese, code-switching, numbers, and overlapping speakers;
- constant- and variable-frame-rate video with speech, slides, on-screen text, and scene changes.

For every golden anchor, test four layers:

1. **Resolution:** source and representation hashes match; selectors are in range.
2. **Localization:** expected text/cells/region/time are recovered, with IoU or timing-tolerance metrics where exact equality is inappropriate.
3. **Presentation:** automated snapshots show the correct page/frame overlay or playback bounds.
4. **Claim grounding:** seeded supported and unsupported answers prove that the verifier accepts the former and rejects the latter.

Track character/word error rate separately for English and Vietnamese OCR/ASR, table structure and cell accuracy, chart value accuracy, locator resolution rate, spatial IoU, timestamp boundary error, and claim-level citation precision/recall. Thresholds must be chosen from this corpus, not copied from engine confidence scores.

## 6. Rejected shortcuts

1. **Cite the Markdown chunk.** Exported Markdown can reorder text, flatten tables, omit images, and change after extractor upgrades. It is useful for retrieval, not source identity.
2. **Use only page numbers.** A page is too coarse for verification and does not exist stably for reflowable formats.
3. **Use only character offsets.** Normalization or parser changes move offsets. Pair them with exact quote/context and a revision hash.
4. **Use only bounding boxes.** A box locates pixels but does not prove the decoded text or number. Pair it with captured evidence and extraction provenance.
5. **Treat ASR word times as exact.** Whisper word alignment is model-derived. Keep original sample/time mappings and allow a safety margin in playback.
6. **Treat chart descriptions as citations.** The chart crop is citable; a generated interpretation is a derivation that still needs validation.
7. **Trust one universal parser.** Broad format coverage and precise, auditable localization are different capabilities. Cross-check adapters are intentional architecture, not duplication.

## 7. Implementation slices

1. Define and test the ledger schema, canonical coordinate/time conventions, content-addressed storage, and a resolver API.
2. Implement plain-text/Markdown and machine-generated PDF vertical slices, including viewer highlights and claim-to-anchor verification.
3. Add image/scanned-PDF OCR with English/Vietnamese golden tests.
4. Add native spreadsheets/tables, then document tables, preserving cell anchors.
5. Add audio ingestion, WebVTT transcript navigation, and original-timeline playback.
6. Add video speech, frame/region anchors, and keyframe extraction.
7. Add native charts; keep raster chart-to-table behind a review-required experimental flag until its benchmark passes.
8. Add structure-aware multimodal chunks only after anchor resolution is stable.

## 8. Remaining decisions and fog

These should become explicit follow-up tickets rather than hidden implementation assumptions:

1. **Dependency and model-license audit.** Decide whether AGPL/commercial PyMuPDF is acceptable; audit Docling model weights, FFmpeg build/codecs, Tesseract data, Whisper/faster-whisper, and any chart/alignment models before distribution.
2. **Bilingual extraction benchmark.** Build the golden corpus and choose parser/OCR/ASR thresholds from measured English/Vietnamese performance and target hardware.
3. **Vietnamese alignment and diarization spike.** Evaluate faster-whisper timestamps versus a forced aligner; decide whether speaker diarization is useful enough to justify gated model downloads and complexity.
4. **Raster-chart policy spike.** Compare native-data extraction, DePlot/local VLM, and Gemini vision on the chart fixture set; define when values are accepted, review-required, or rejected.
5. **Untrusted-file processing threat model.** Office, PDF, image, and codec parsers process attacker-controlled bytes. Define resource limits, decompression-bomb defenses, subprocess isolation, and patch/update policy even though TutorDesk is single-user.
6. **Artifact retention budget.** Choose which page renders, crops, PCM files, keyframes, OCR layers, and model outputs are retained or reproducibly regenerated; citations must fail explicitly if a required artifact was deleted.

## Primary sources

- W3C: [Web Annotation Data Model](https://www.w3.org/TR/annotation-model/), [Selectors and States](https://www.w3.org/TR/selectors-states/), [Media Fragments URI 1.0](https://www.w3.org/TR/media-frags/), [PROV-O](https://www.w3.org/TR/prov-o/), [WebVTT](https://www.w3.org/TR/webvtt1/), [EPUB 3.3](https://www.w3.org/TR/epub-33/).
- IETF: [RFC 5147 — URI Fragment Identifiers for `text/plain`](https://www.rfc-editor.org/rfc/rfc5147).
- Docling: [supported formats](https://docling-project.github.io/docling/usage/supported_formats/), [document model](https://docling-project.github.io/docling/reference/docling_document/), [chunking](https://docling-project.github.io/docling/concepts/chunking/), [source](https://github.com/docling-project/docling).
- PDF tooling: [pdfplumber documentation/source](https://github.com/jsvine/pdfplumber), [PyMuPDF text extraction](https://pymupdf.readthedocs.io/en/latest/recipes-text.html), [PyMuPDF page API](https://pymupdf.readthedocs.io/en/latest/page.html), [PyMuPDF licensing](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright).
- OCR: [Tesseract documentation](https://tesseract-ocr.github.io/tessdoc/), [CLI output formats](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html), [API example](https://tesseract-ocr.github.io/tessdoc/APIExample.html), [official language/model listing](https://github.com/tesseract-ocr/tesseract/blob/main/doc/tesseract.1.asc).
- Audio/video: [FFmpeg/ffprobe documentation](https://ffmpeg.org/ffprobe-all.html), [OpenAI Whisper source](https://github.com/openai/whisper), [Whisper paper](https://cdn.openai.com/papers/whisper.pdf), [faster-whisper source](https://github.com/SYSTRAN/faster-whisper), [WhisperX paper](https://arxiv.org/abs/2303.00747).
- Charts: [DePlot paper](https://aclanthology.org/2023.findings-acl.660/), [Pix2Struct/DePlot code and checkpoints](https://github.com/google-research/pix2struct).
- Office formats: [ECMA-376 Office Open XML](https://ecma-international.org/publications-and-standards/standards/ecma-376/), [openpyxl chart range example](https://openpyxl.readthedocs.io/en/stable/charts/bar.html), [Microsoft PresentationML structure](https://learn.microsoft.com/en-us/office/open-xml/presentation/structure-of-a-presentationml-document).
