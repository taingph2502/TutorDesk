# Provider capabilities and the normalized TutorDesk model contract

**Research date:** 2026-09-18

**Scope:** official Gemini, OpenAI, Anthropic, and Ollama documentation only

**Decision target:** the provider-neutral contract for generation, streaming, tools, structured output, multimodal input, embeddings, cancellation, citations, and usage accounting

## Decision in one paragraph

TutorDesk should own a small, typed model runtime rather than expose any provider SDK above the adapter layer. The runtime should consist of separate `GenerationGateway` and `EmbeddingGateway` interfaces, an exact-model capability registry, a provider-neutral event stream, application-owned citation identifiers, idempotent cancellation, normalized usage, and preserved raw provider metadata. Capabilities must be negotiated per model and deployment, never inferred from the provider name. Gemini's Interactions API should be the first generation adapter and `gemini-3.8-flash` the default development model; OpenAI Responses, Anthropic Messages, and Ollama `/api/chat` should implement the same semantic contract without pretending that unsupported features exist.

## Verified Gemini model identifier

The requested identifier is correct. Google's current model catalog lists **Gemini 3.8 Flash** with endpoint/model code **`gemini-3.8-flash`**, and the dedicated model page marks it stable and documents text, image, video, audio, and PDF input with text output. The release page also calls the model generally available. This verification used the public documentation, not the API key supplied in the project prompt and not an authenticated API request ([model catalog](https://ai.google.dev/gemini-api/docs/models), [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [release guide](https://ai.google.dev/gemini-api/docs/latest-model)).

Two safeguards are still required:

1. Treat the configured model ID as data, not an enum compiled into business logic. At startup, the Gemini adapter should call `models.get` or `models.list` with the user's configured credentials and fail readiness if the configured ID is unavailable to that account/region; Google documents these endpoints as the authoritative way to discover names and supported generation methods ([Models API](https://ai.google.dev/api/models)).
2. Record the resolved model ID and adapter version on every run because aliases, previews, availability, and capabilities can change independently of TutorDesk.

## Model identifiers and versioning observed on the research date

The contract must keep model identifiers as opaque strings because the four systems use materially different naming and stability schemes. This dated snapshot is for configuration guidance, not a hard-coded allowlist:

| Provider | Current official examples on 2026-09-18 | Contract treatment |
|---|---|---|
| Gemini | `gemini-3.8-flash` is the requested stable default. The catalog also separates preview, live, image/media, agent, and embedding identifiers ([catalog](https://ai.google.dev/gemini-api/docs/models)). | Persist the exact model string returned by the API and refresh model metadata through `models.get/list`. |
| OpenAI | The official catalog recommends `gpt-6-astra` as its flagship and lists `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna` as current general-purpose alternatives ([catalog](https://developers.openai.com/api/docs/models)). | Accept exact model IDs and aliases, but resolve/log the served model when returned. Do not infer capabilities from an ID prefix. |
| Anthropic | The direct Claude API catalog lists `claude-fable-5-1`, `claude-opus-5`, `claude-sonnet-5`, and `claude-haiku-4-5-20251001` ([catalog](https://platform.claude.com/docs/en/models/overview)). Anthropic documents that 4.6-and-later dateless IDs are pinned releases, while some earlier dateless names are moving aliases ([versioning](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)). | Store platform plus exact ID. Never translate direct-API, Bedrock, and Google Cloud names by string convention in core code; an adapter owns that mapping. |
| Ollama | Model names are locally installed tags such as `gemma4`; `/api/tags` returns the tag and immutable content digest, while `/api/show` returns advertised capabilities ([tags](https://docs.ollama.com/api/tags), [show](https://docs.ollama.com/api-reference/show-model-details)). | Identify a deployment by endpoint, tag, and observed digest. A changed digest invalidates the cached capability result even if the tag is unchanged. |

Only the Gemini default is a TutorDesk decision here. OpenAI and Anthropic examples establish identifier handling and test fixtures; selecting their product defaults should remain configuration/evaluation work.

## Capability matrix

`ModelCapabilities` below means the capability of one exact model on one configured endpoint, not a promise made for every model from a provider.

| Concern | Gemini | OpenAI | Anthropic | Ollama | Contract consequence |
|---|---|---|---|---|---|
| Primary generation surface | Interactions is the recommended agentic primitive; `generateContent` remains available ([API overview](https://ai.google.dev/api)) | Responses API ([migration guide](https://developers.openai.com/api/docs/guides/migrate-to-responses)) | Stateless Messages API ([Messages](https://platform.claude.com/docs/en/api/messages/create)) | Local `/api/chat` ([Chat API](https://docs.ollama.com/api/chat)) | Adapter owns history/state translation. Core does not store provider response objects. |
| Streaming | SSE with typed interaction/step events and final usage ([streaming](https://ai.google.dev/gemini-api/docs/streaming)) | SSE with typed response/output events ([streaming](https://developers.openai.com/api/docs/guides/streaming-responses)) | SSE with text, tool-input, thinking, usage, and message events ([streaming](https://platform.claude.com/docs/en/build-with-claude/streaming)) | NDJSON; text, thinking, and tool calls may stream ([streaming](https://docs.ollama.com/api/streaming), [capability guide](https://docs.ollama.com/capabilities/streaming)) | Emit one TutorDesk event algebra and preserve provider event/name under `raw`. |
| Client tools | Function calls have IDs and support parallel and sequential calls ([function calling](https://ai.google.dev/gemini-api/docs/function-calling)) | Function calling supports strict schemas and optional parallel calls ([function calling](https://developers.openai.com/api/docs/guides/function-calling)) | `tool_use` / `tool_result` loop; strict tools are supported on compatible models ([tool loop](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works), [tool overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)) | Function tools and parallel calls are supported only when the installed model can produce them ([tool calling](https://docs.ollama.com/capabilities/tool-calling)) | Core allocates stable internal call IDs, validates every argument payload, and supports zero-to-many calls per model turn. |
| Structured final output | JSON Schema subset; streamed partial JSON can be concatenated ([structured output](https://ai.google.dev/gemini-api/docs/structured-output)) | Strict Structured Outputs use a JSON Schema subset and require `additionalProperties: false` for objects ([structured output](https://developers.openai.com/api/docs/guides/structured-outputs)) | JSON output and strict tools share a constrained schema compiler; refusals/limits can still break schema ([structured output](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)) | `format` accepts `json` or a schema, but the docs still recommend application validation; Ollama Cloud does not support this feature ([structured output](https://docs.ollama.com/capabilities/structured-outputs)) | Define and test a portable schema subset; validate final data again in TutorDesk. A capability bit may be `native`, `best_effort`, or `unsupported`. |
| Direct multimodal/document input | `gemini-3.8-flash`: text, image, video, audio, PDF; Files API supports media upload ([model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [Files API](https://ai.google.dev/gemini-api/docs/files)) | Responses supports images and document/file inputs. PDF sends text plus page images; many office files are text-only, spreadsheets use an augmentation flow ([file inputs](https://developers.openai.com/api/docs/guides/file-inputs), [vision](https://developers.openai.com/api/docs/guides/images-vision)). Audio is model/API-specific rather than a universal Responses capability ([audio overview](https://developers.openai.com/api/docs/guides/audio)) | Messages documents text/image input; PDFs receive visual document processing ([Messages](https://platform.claude.com/docs/en/api/messages/create), [vision](https://platform.claude.com/docs/en/build-with-claude/vision), [PDFs](https://platform.claude.com/docs/en/build-with-claude/pdf-support)) | Vision models accept image parts; the installed model advertises capabilities through `/api/show` ([vision](https://docs.ollama.com/capabilities/vision), [show model](https://docs.ollama.com/api-reference/show-model-details)) | Ingestion owns canonical assets, OCR/transcription/frame extraction, and provenance. Direct provider media is an optimization, not the only path. |
| Embeddings | Text embedding plus a preview multimodal embedding model are exposed separately ([embeddings](https://ai.google.dev/gemini-api/docs/embeddings)) | Dedicated embeddings API/models ([embeddings](https://developers.openai.com/api/docs/guides/embeddings)) | Anthropic explicitly does not offer its own embedding model ([embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)) | `/api/embed` handles text or text batches; vector dimensions depend on the installed model ([embed API](https://docs.ollama.com/api/embed), [embedding guide](https://docs.ollama.com/capabilities/embeddings)) | Embedding is a separate port with its own provider/model, dimension, input type, normalization, and index identity. Generation-provider selection must not silently change the vector space. |
| Cancellation | Background Interactions have an explicit cancel endpoint; status becomes `cancelled` ([background execution](https://ai.google.dev/gemini-api/docs/background-execution)) | Background Responses have idempotent server cancellation; synchronous cancellation terminates the connection ([background mode](https://developers.openai.com/api/docs/guides/background)) | Official TypeScript SDK exposes stream abort; Messages has no documented persisted-job cancel resource ([SDK](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/typescript)) | No server cancel endpoint is listed in the official REST API index; terminate the request/stream locally ([API index](https://docs.ollama.com/llms.txt)) | Always accept an abort signal. Optionally expose a remote execution handle. Distinguish requested, locally aborted, remotely acknowledged, and unknown outcomes. |
| Usage and finish state | Usage distinguishes input, output, cached, thought, tool-use, and modality counts in Interactions ([tokens](https://ai.google.dev/gemini-api/docs/tokens), [streaming](https://ai.google.dev/gemini-api/docs/streaming)) | Responses reports input, output, cached, reasoning, and total tokens plus typed completed/incomplete/failed/cancelled state ([Responses stream reference](https://platform.openai.com/docs/api-reference/responses-streaming/response/refusal)) | Messages reports input/output, cache read/write, thinking, server-tool usage, and `stop_reason` ([Messages](https://platform.claude.com/docs/en/api/messages/create), [stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)) | Final chunk reports prompt, cached-prompt, generated-token counts and durations; mid-stream errors arrive inside NDJSON ([usage](https://docs.ollama.com/api/usage), [errors](https://docs.ollama.com/api/errors)) | Use nullable normalized counters and keep `providerRaw`; never synthesize zero for a metric a provider did not report. |
| Native citations | URL context emits URL citation annotations; other grounding tools have their own metadata ([URL context](https://ai.google.dev/gemini-api/docs/url-context)) | Search/file tools can emit annotations and file citations in response items ([Responses reference](https://platform.openai.com/docs/api-reference/responses)) | Document citations identify page, character, or content-block ranges, but citations are incompatible with strict JSON output ([citations](https://platform.claude.com/docs/en/build-with-claude/citations), [structured output](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)) | No native document-citation contract in `/api/chat` | TutorDesk citations must be generated from its retrieved evidence IDs and verified independently. Native annotations are optional additional evidence. |

## Normalized contract

The following is an architectural shape, not a commitment to a specific programming language.

```ts
type Support = "native" | "best_effort" | "unsupported";

interface ModelRef {
  provider: "gemini" | "openai" | "anthropic" | "ollama";
  model: string;              // exact configured identifier/tag
  endpoint?: string;          // required for local/custom deployments
}

interface ModelCapabilities {
  model: ModelRef;
  inputs: Set<"text" | "image" | "audio" | "video" | "pdf" | "document">;
  streaming: boolean;
  tools: Support;
  parallelTools: boolean;
  structuredOutput: Support;
  nativeCitations: Support;
  backgroundExecution: boolean;
  remoteCancellation: boolean;
  tokenCounting: Support;
  contextTokens?: number;
  maxOutputTokens?: number;
  observedAt: string;
  raw: unknown;
}

interface GenerateRequest {
  runId: string;
  model: ModelRef;
  instructions: string[];
  messages: Message[];
  tools?: ToolDefinition[];
  toolChoice?: "auto" | "none" | "required" | { name: string };
  responseSchema?: PortableJsonSchema;
  maxOutputTokens?: number;
  temperature?: number;
  abortSignal: AbortSignal;
  metadata: Record<string, string>;
}

type ModelEvent =
  | { type: "started"; providerRunId?: string; model: ModelRef }
  | { type: "text_delta"; text: string }
  | { type: "tool_call_start"; callId: string; name: string }
  | { type: "tool_call_arguments_delta"; callId: string; json: string }
  | { type: "tool_call_end"; callId: string; arguments: unknown }
  | { type: "citation"; citation: NativeCitation }
  | { type: "usage"; usage: Usage; cumulative: boolean }
  | { type: "completed"; finish: Finish; usage?: Usage }
  | { type: "failed"; error: ModelError; retryable: boolean };

interface Usage {
  inputTokens?: number;
  outputTokens?: number;
  cachedInputTokens?: number;
  cacheWriteTokens?: number;
  reasoningTokens?: number;
  toolTokens?: number;
  totalTokens?: number;
  providerRaw: unknown;
}

type FinishReason =
  | "stop" | "length" | "tool_call" | "safety" | "refusal"
  | "cancelled" | "error" | "other";

interface Finish {
  reason: FinishReason;
  partial: boolean;
  providerReason?: string;
}
```

### Contract invariants

1. **One ordered stream per model turn.** Adapters must serialize provider events into the order TutorDesk observed them. The orchestrator may execute independent tools concurrently, but tool results remain correlated by `callId`.
2. **Exactly one terminal event.** A stream ends with `completed` or `failed`, including a client-cancelled terminal result. Transport closure alone is not success.
3. **Partial output is explicit.** Length limits, safety stops, cancellation, and mid-stream errors may leave useful text but must set `partial: true`; partial content is never parsed as a valid structured result without full validation.
4. **Unknown is not zero.** Missing usage or capability data remains absent. Estimated token counts are separately labelled and cannot be mixed with billed usage.
5. **Raw metadata survives.** Persist provider request ID, resolved model, finish reason, usage object, and adapter version alongside the normalized record for debugging and cost reconciliation.
6. **No silent downgrade.** If a request requires tools, strict output, or an input modality and the selected model cannot provide it, routing either chooses a declared fallback or fails before generation. It must not quietly drop a tool, source, or schema.

## Portable schema and tool policy

All four surfaces use JSON-schema-like declarations, but each supports a different subset and level of enforcement. TutorDesk should define a deliberately small `PortableJsonSchema` profile:

- root `object` only;
- `properties`, `required`, and `additionalProperties: false` on every object;
- scalar `string`, `number`, `integer`, `boolean`, and `null`;
- arrays with one `items` schema;
- `enum` and descriptions;
- optional values represented as a required property whose type includes `null`;
- bounded nesting and property counts set by TutorDesk, below every provider's documented complexity ceiling;
- no external references, regex constraints, conditionals, or provider-specific keywords.

Adapters compile this profile to provider syntax. TutorDesk validates every completed tool argument and structured final response with its own validator even if the provider promises strict conformance. Refusals, token limits, streaming interruption, provider bugs, and semantic invalidity remain possible. Tool results also need an explicit size limit, content type, error shape, and untrusted-data boundary before they re-enter the next model turn.

Anthropic's documented incompatibility between native citations and structured JSON is especially important: TutorDesk cannot define a universal request flag meaning “strict JSON plus provider-native citations.” The portable path is application-owned evidence IDs inside the structured schema, followed by deterministic citation validation. Provider-native citations may be collected in an unstructured answer path or a separate verification pass.

## Multimodal ingestion boundary

The model contract should accept canonical TutorDesk `AssetRef` values, not arbitrary provider file handles. The ingestion subsystem owns the durable original, MIME detection, hashes, extraction artifacts, timestamps/page coordinates, and source provenance. An adapter may then choose one of two declared strategies:

1. **Direct:** upload/reference the original when the exact model supports the modality.
2. **Derived:** use TutorDesk's transcription, OCR, document extraction, chart/image rendering, or video frame/audio track artifacts.

Every model input part records which asset or derived artifact was actually sent. This is necessary for reproducible citations and avoids making Gemini's broad native input support the accidental lowest-level architecture. It also gives OpenAI, Anthropic, and Ollama viable paths for audio/video or complex office documents that their primary chat contract does not directly understand in the same way.

## Citation and grounding boundary

Provider-native citations are not the product's grounding guarantee. TutorDesk should retrieve immutable evidence chunks with stable IDs and require generated claims to reference those IDs. After generation, a deterministic gate verifies that every citation ID existed in the supplied evidence set, that the cited locator still resolves to the versioned source, and that citation-required answer sections have coverage. Semantic entailment can be evaluated separately, but an adapter must never manufacture an application citation from a provider URL or free-form page number.

A native provider annotation is stored as `NativeCitation` and linked to the run for audit. It can enrich the UI, but it does not replace `answer claim -> TutorDesk evidence chunk` provenance. This design gives the same grounding semantics to Ollama and prevents provider switching from changing what “cited” means.

## Cancellation semantics

`abortSignal` is mandatory for every generation call. On abort, the adapter must stop emitting user-visible deltas, close the transport, and attempt remote cancellation when the provider exposes a persisted background execution. `cancel(runId)` is idempotent and returns one of:

- `remotely_cancelled`: provider acknowledged a terminal cancelled state;
- `locally_aborted`: transport stopped, but no remote job exists;
- `cancel_requested`: remote cancellation was sent but final state is not yet known;
- `already_terminal`;
- `unknown`.

Usage after cancellation is nullable because some providers report it only in the final stream event, which may never arrive after a local abort. TutorDesk may label an estimate for budget dashboards, but must not present it as provider-billed usage.

## Embedding contract

Embeddings need an independent configuration and lifecycle:

```ts
interface EmbeddingRequest {
  model: ModelRef;
  inputs: Array<{ id: string; text: string }>;
  inputType: "document" | "query";
  dimensions?: number;
  abortSignal: AbortSignal;
}

interface EmbeddingBatch {
  vectors: Array<{ id: string; values: number[] }>;
  dimensions: number;
  normalized?: boolean;
  usage?: Usage;
  indexIdentity: string; // provider + exact model + dimensions + preprocessing version
}
```

Never mix vectors with different `indexIdentity` values in one index. A generation-model change must not trigger an implicit re-embedding. Because Anthropic has no first-party embedding model, choosing Claude for generation still requires a separate embedding provider. Gemini's multimodal embedding model is preview in the current catalog, so production adoption needs an explicit stability decision rather than being inherited from the default Gemini generation model.

## Adapter-specific mapping notes

### Gemini

- Use Interactions as the primary adapter because it already exposes typed text/tool/thought steps, server-side continuation, background execution, and final usage. Keep stored provider state optional; TutorDesk's session and L1 event log remain authoritative.
- Preserve thought signatures required for subsequent Gemini tool turns, but do not expose private reasoning as a normalized product feature.
- Map background interaction IDs to optional remote handles; use the cancel endpoint only for background interactions.

### OpenAI

- Use Responses, not Chat Completions, for the normalized adapter.
- Map typed response items/events rather than concatenating all output into one string. Treat `incomplete`, `failed`, `cancelled`, and refusal as distinct terminal conditions.
- Use strict functions/structured output only after compiling the portable schema. File input behavior is type-specific, so the ingestion strategy must record whether page images, extracted text, or spreadsheet augmentation reached the model.

### Anthropic

- Rebuild the stateless Messages history in the adapter, including tool-use and tool-result blocks. Map all documented `stop_reason` values and keep unknown future values in `providerReason`.
- Token counting is a useful preflight estimate, but the docs warn that it may differ from actual billed input and does not accept every server-tool/file form that Messages accepts; it must not be treated as final usage ([token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)).
- Route native citations and strict structured output as incompatible capabilities on the same call.

### Ollama

- Probe `/api/tags` and `/api/show` on readiness. Model tags are local mutable deployment artifacts; record digest and capabilities in addition to tag.
- Treat tools and structured output as `best_effort` unless the selected model passes TutorDesk contract tests. Ollama's HTTP surface may accept a field even when the local model performs poorly or lacks the corresponding trained capability.
- Parse mid-stream `{ "error": ... }` objects even after an HTTP 200 response. Final usage exists only on the `done: true` chunk.

## Acceptance tests for the implementation backlog

Each adapter should run the same fixture suite against configured test models:

1. plain text and multilingual English/Vietnamese turns;
2. ordered text streaming and exactly one terminal event;
3. one tool call, parallel calls when advertised, malformed arguments, tool error, and oversized result;
4. strict response schema, refusal, output limit, and interrupted partial JSON;
5. each advertised input modality and the declared derived-artifact fallback;
6. citation IDs constrained to the supplied evidence set;
7. cancellation before first token, mid-stream, during a tool wait, and after terminal completion;
8. normalized usage with missing fields, cache fields, reasoning fields, and provider raw payload;
9. embedding dimension/index identity and query/document consistency;
10. capability drift: configured model removed, alias changes, Ollama tag replaced under the same name, and feature rejected at runtime.

Gemini CI may use `gemini-3.8-flash` as requested, but credentials must come from environment/secret storage. No API key belongs in fixtures, documentation, issues, commits, or logs.

## Remaining decisions and fog

The provider contract itself is resolved. These follow-up choices belong in implementation tickets rather than this interface decision:

- choose the production embedding model and migration/re-index policy; `gemini-embedding-2-preview` should not become the default merely because Gemini generates by default;
- define the ingestion/transcoding stack and limits for audio, video, complex spreadsheets, and image-heavy non-PDF documents;
- decide which workloads warrant persisted background execution versus synchronous streaming;
- pin the portable JSON Schema profile in executable contract tests and publish provider/model compatibility results;
- set routing policy when a selected model lacks a required capability: ask the user, use a pre-approved fallback, or fail closed.

None of these uncertainties changes the core answer: TutorDesk needs capability-negotiated adapters with application-owned evidence and lifecycle semantics, not a least-common-denominator wrapper and not direct provider SDK types in the agent loop.

## Official source index

- Google Gemini: [API overview](https://ai.google.dev/api), [models](https://ai.google.dev/gemini-api/docs/models), [Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [streaming](https://ai.google.dev/gemini-api/docs/streaming), [function calling](https://ai.google.dev/gemini-api/docs/function-calling), [structured output](https://ai.google.dev/gemini-api/docs/structured-output), [files](https://ai.google.dev/gemini-api/docs/files), [embeddings](https://ai.google.dev/gemini-api/docs/embeddings), [background execution](https://ai.google.dev/gemini-api/docs/background-execution).
- OpenAI: [model catalog](https://developers.openai.com/api/docs/models), [Responses migration](https://developers.openai.com/api/docs/guides/migrate-to-responses), [streaming](https://developers.openai.com/api/docs/guides/streaming-responses), [function calling](https://developers.openai.com/api/docs/guides/function-calling), [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [file inputs](https://developers.openai.com/api/docs/guides/file-inputs), [embeddings](https://developers.openai.com/api/docs/guides/embeddings), [background mode](https://developers.openai.com/api/docs/guides/background).
- Anthropic: [model catalog](https://platform.claude.com/docs/en/models/overview), [model IDs and versioning](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions), [Messages](https://platform.claude.com/docs/en/api/messages/create), [streaming](https://platform.claude.com/docs/en/build-with-claude/streaming), [tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works), [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), [citations](https://platform.claude.com/docs/en/build-with-claude/citations), [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting), [embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings).
- Ollama: [API index](https://docs.ollama.com/llms.txt), [chat](https://docs.ollama.com/api/chat), [streaming](https://docs.ollama.com/api/streaming), [tools](https://docs.ollama.com/capabilities/tool-calling), [structured output](https://docs.ollama.com/capabilities/structured-outputs), [vision](https://docs.ollama.com/capabilities/vision), [embeddings](https://docs.ollama.com/api/embed), [usage](https://docs.ollama.com/api/usage), [errors](https://docs.ollama.com/api/errors), [model details](https://docs.ollama.com/api-reference/show-model-details).
