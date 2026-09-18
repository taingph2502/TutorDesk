# TutorDesk

TutorDesk is a personal learning workspace that turns user-approved evidence into citation-grounded study experiences and an inspectable learner model.

## Study organization

**Workspace**:
A bounded area of study containing its selected sources, sessions, practice activity, and generated learning artifacts. Contextual memory belongs to a Workspace.
_Avoid_: Notebook, project, knowledge base

**Source Vault**:
The permanent, user-approved collection of versioned sources available for study and citation across Workspaces.
_Avoid_: Corpus, library, knowledge base

**Source Candidate**:
Immutable content held in private staging while Source Admission determines whether it may become a Source Revision. It is unavailable to retrieval and Capabilities, and rejection destroys its staged bytes.
_Avoid_: Uploaded source, quarantined source, temporary source

**Source Admission**:
The policy evaluation that either accepts a Source Candidate as a Source Revision or returns a typed rejection. Admission establishes structural processability under bounded controls, never trust in the source's content or instructions.
_Avoid_: Upload validation, safety scan, trusted import

**Source Processing Record**:
The payload-free provenance of Source Admission and Evidence Representation processing, including content and configuration hashes, policy and parser versions, applied limits, outcomes, security findings, and derived identities.
_Avoid_: Parser log, scan result, processing dump

**Research Evidence Set**:
A versioned collection of external Source Revisions captured for one Research activity. It may support clearly identified research claims immediately, but each Source Revision joins the Source Vault only through individual user approval. Promotion preserves the revision's Research Evidence Set provenance and does not retroactively change the research status of earlier claims or select the revision into any Workspace.
_Avoid_: Temporary knowledge base, web results

**Source Revision**:
An immutable version of a Source's content. It exists before extraction and may be partially usable as its derived Evidence Representations become ready. Workspace selections and citations remain pinned to the selected Source Revision until the user explicitly adopts another revision.
_Avoid_: Latest source, mutable document

**Supported Source Format**:
A local source format covered by TutorDesk's complete-release contract: the original bytes can be safely probed and retained as an immutable Source Revision, rendered or played locally, given an explicit extraction outcome, and used to produce at least one verifiable, claim-eligible Evidence Representation for the format's core content. Retaining bytes without a usable representation does not by itself make a format supported.
_Avoid_: Accepted file, importable extension

**Evidence Representation**:
A versioned form derived from a Source Revision for retrieval, navigation, or verification, such as normalized text, a transcript, or a rendered page. Each Evidence Representation has independent readiness and provenance and never replaces the Source Revision as the evidence source of truth. Retrieval chunks and indexes are reproducible builds tied to their inputs and configuration; they have no durable citation identity.
_Avoid_: Canonical source, mutable extraction

**Representation Outcome**:
The retained result of attempting to produce or validate one Evidence Representation. It reports processing state, coverage, and claim eligibility independently, including the reason for any blocked, partial, review-required, or ineligible result. Successful representations from the same Source Revision may be used while other representations remain unavailable.
_Avoid_: Extraction status, confidence score, source readiness

**Claim Eligibility**:
Whether one exact Evidence Representation revision may support a Source Claim: eligible, review-required, or ineligible. Native evidence requires resolvable anchors; machine-read evidence must also pass its modality quality gates; deterministic computations retain their operation and input anchors; and model-derived or materially ambiguous evidence cannot support an unqualified claim without corroboration or explicit approval. Approval applies only to the reviewed representation revision.
_Avoid_: Trusted source, parser confidence, globally approved extractor

**Representation Correction**:
A learner-approved successor to an Evidence Representation whose corrected content remains linked to the original representation, exact source anchors, and a recorded diff. It never changes the Source Revision or silently changes the behavior of an extractor; Claim Eligibility applies only to the approved corrected revision.
_Avoid_: Editing the source, corrected source, parser training

**Retrieval Generation**:
An immutable, reproducible set of lexical and semantic retrieval structures built from exact Source Revisions, Evidence Representations, and a recorded configuration. Activating a new generation changes retrieval behavior without changing citation identity.
_Avoid_: Live index, mutable embeddings

**Evidence Anchor**:
A precise, verifiable reference from a Source Claim to the supporting span, region, cells, or time interval in one Source Revision.
_Avoid_: Chunk ID, vector result, page-only citation

**Evidence Packet**:
A bounded retrieval result containing resolved evidence, Evidence Anchors, source and revision context, support quality, and detected Evidence Conflicts for one request. Retrieval chunks and index internals do not cross this interface.
_Avoid_: Search results, chunk list, retrieval context

**Grounding Gap**:
A structured account of evidence that is absent, below quality thresholds, or insufficient to support part or all of a request. A Grounding Gap causes claim-level qualification or abstention rather than retrieval of weaker evidence or reliance on model knowledge.
_Avoid_: No results, model uncertainty

**Session**:
A continuous sequence of learner interactions inside one Workspace that shares agent context.
_Avoid_: Chat, conversation, thread

**Turn**:
One learner or system trigger within a Session together with its complete orchestrated response. A Turn has one entry Capability Run and may contain bounded child Capability Runs.
_Avoid_: Message, request, chat turn

**Capability**:
A mode of the shared learning loop, such as Chat, Quiz, Research, or Visualize, that owns specialized behavior without becoming an independent agent.
_Avoid_: Agent, plugin, mode-specific agent

**Capability Definition**:
The versioned declaration of a Capability's accepted inputs and outputs, runtime requirements, permitted dependencies, and validation obligations. It does not expose the Capability's internal pipeline.
_Avoid_: Agent manifest, plugin manifest, workflow specification

**Capability Run**:
A bounded execution of one Capability within a Turn. It may use a specialized internal pipeline, but lifecycle, routing, budgets, and cross-Capability coordination remain governed by the shared orchestrator.
_Avoid_: Agent run, workflow, mode session

**Run Envelope**:
The immutable scope, authorization, route options, budgets, and control constraints governing one Capability Run. Replanning may narrow or rearrange work within it but cannot widen it.
_Avoid_: Runtime config, request options, execution context

**Route Plan**:
The ordered set of pre-authorized exact provider and model routes eligible for a Capability Run. A fallback outside the Route Plan requires a new learner authorization.
_Avoid_: Provider preference, model list, fallback chain

**Run Event**:
An ordered semantic record of a Capability Run's lifecycle, progress, effects, or outcome. Ephemeral token deltas and provider-native events are not Run Events.
_Avoid_: Provider event, stream chunk, log entry

**Background Run**:
A checkpointed Capability Run authorized to continue without an actively attached client. It retains the same or a narrower Run Envelope and remains part of its originating Turn.
_Avoid_: Background agent, detached task, scheduled agent

**Run Context Manifest**:
The immutable record of the exact Session history, source revisions, learner-state revisions, policies, and other scoped inputs used by one Capability Run.
_Avoid_: Prompt dump, mutable context window, latest state

**Run Outcome**:
The immutable terminal account of a Capability Run's validated result, incomplete scope, resource usage, effects, and available recovery actions.
_Avoid_: Final message, provider response, job result

## Evidence and learner state

**Source Claim**:
A structured, independently checkable factual proposition supported by one or more Evidence Anchors in the active Workspace's selected Source Revisions or the active Research Evidence Set. Each Source Claim declares whether its support is direct, computed, or inferred; computed and inferred claims are visibly identified. An inferred Source Claim also records its reasoning and is disallowed when materially contradicted or too weakly supported. Model knowledge may guide retrieval but cannot itself support a Source Claim. When evidence is incomplete or conflicting, TutorDesk preserves supported claims, identifies the Grounding Gap or disagreement, and abstains from unsupported conclusions.
_Avoid_: Grounded answer, model fact

**Evidence Conflict**:
A first-class, auditable relation among incompatible Source Claims and their Evidence Anchors. It remains unresolved, qualified, or resolved by a scoped user decision rather than being silently removed through retrieval ranking. A resolution defaults to one Workspace and records its rationale without deleting or rewriting conflicting evidence.
_Avoid_: Low-ranked evidence, model disagreement

**Citation Validation**:
The combined deterministic and semantic verification that every Source Claim has resolvable Evidence Anchors and that those anchors support the claim. A failed claim receives at most one bounded repair against the same Evidence Packet before it is removed or replaced by abstention.
_Avoid_: Citation formatting, link check, model confidence

**Grounding Audit Record**:
The retained account of how a grounded answer was produced, including retrieval scope and query metadata, derived-build versions, ranked Evidence Anchors, Source Claims, support relationships, Evidence Conflicts, and Citation Validation outcomes. It references rather than duplicates source evidence.
_Avoid_: Full prompt dump, copied Evidence Packet

**Learner Model**:
The evidence-backed representation of the learner across Workspaces, including approved profile and mastery conclusions plus a derived review schedule.
_Avoid_: User profile, memory blob

**Learner Profile**:
The approved, provenance-backed goals, preferences, accommodations, language proficiency, background, and durable constraints that apply to the learner across Workspaces. Demonstrated ability and review timing do not belong in the Learner Profile.
_Avoid_: Mastery profile, user settings, profile prose

**Learning Objective**:
A Workspace-scoped, assessable ability against which TutorDesk records evidence and estimates mastery. Topics and source sections may organize or support Learning Objectives but do not carry mastery themselves.
_Avoid_: Topic mastery, source mastery, question mastery

**Objective Equivalence**:
An approved relation asserting that Learning Objectives from different Workspaces assess the same ability, allowing their evidence to contribute to a shared Learner Model conclusion.
_Avoid_: Automatic objective merge, global topic match

**Assessment Evidence**:
A typed record of a learner performance or self-report associated with a Learning Objective and backed by a Raw Event. Its evidence class, evaluation confidence, and support conditions determine how it contributes to mastery.
_Avoid_: Mastery score, learner impression, engagement signal

**Evaluation Confidence**:
The confidence that a particular learner response was evaluated correctly. Low Evaluation Confidence makes Assessment Evidence provisional rather than directly weakening a Mastery Estimate.
_Avoid_: Mastery confidence, model confidence

**Mastery Estimate**:
A deterministic projection of accepted Assessment Evidence describing expected unaided performance on a Learning Objective, its uncertainty and evidence sufficiency, the latest demonstration, and a human-readable mastery stage.
_Avoid_: Mastery fact, knowledge score, writable mastery

**Mastery Stage**:
An auditable interpretation of a Mastery Estimate as unassessed, acquiring, practicing, proficient, or durable. Proficient and durable require independent unaided demonstrations and cannot be assigned from a point estimate alone.
_Avoid_: Score band, proficiency label

**Mastery Uncertainty**:
The uncertainty around a Mastery Estimate given the available Assessment Evidence.
_Avoid_: Evaluation confidence, evidence quality

**Evidence Sufficiency**:
Whether the quantity and diversity of accepted Assessment Evidence justify a learner-state conclusion.
_Avoid_: Confidence score, evidence count

**Retrievability**:
The estimated availability of a learned ability for successful recall now. It may decline with time without erasing previously demonstrated mastery.
_Avoid_: Current mastery, forgetting score

**Challenge Profile**:
The typed description of why a learning activity is difficult, including its cognitive operation, objective breadth, source integration, response complexity, transfer distance, scaffolding, and constraints. A single effective-difficulty estimate may be derived from this profile but does not replace it.
_Avoid_: Difficulty label, hard or easy tag

**Raw Event (L1)**:
An immutable record of an interaction, assessment result, user action, system action, or memory decision. Normal correction adds another Raw Event rather than rewriting history; explicit privacy erasure may remove its payload while preserving a Tombstone.
_Avoid_: Transcript, log line

**Contextual Fact (L2)**:
A typed observation within one Workspace that cites the exact Raw Events supporting it. Accepted Assessment Evidence is a Contextual Fact.
_Avoid_: Summary, note, memory item

**Learner Insight (L3)**:
An approved cross-Workspace conclusion synthesized from Contextual Facts, with exact references to every L2 revision used in its synthesis.
_Avoid_: Profile text, global summary

**Memory Proposal**:
An inferred Contextual Fact or any proposed Learner Insight awaiting user approval before it can influence personalization. Boardroom Recommendations always remain Memory Proposals until approved.
_Avoid_: Pending memory, draft profile

**Memory Decision**:
The learner's recorded acceptance, rejection, edit-and-acceptance, or withdrawal of a Memory Proposal, including the reason and exact proposal revision considered.
_Avoid_: Moderation action, silent approval

**Memory Record**:
The stable logical identity of one Contextual Fact or Learner Insight across its immutable revisions.
_Avoid_: Mutable fact, memory row

**Memory Revision**:
An immutable, effectively dated version of a Memory Record created by proposal, acceptance, correction, supersession, or retraction.
_Avoid_: Edit, current value

**Memory Provenance Link**:
A typed exact reference from an L2 revision to an L1 event or from an L3 revision to an L2 revision, identifying evidence that supports, contradicts, or qualifies the revision.
_Avoid_: Loose citation, related memory

**Memory Consolidation**:
The auditable evaluation of eligible Raw Events into Contextual Fact candidates, or accepted Contextual Facts into Learner Insight proposals. A consolidation may create a record, propose a revision, surface a contradiction, or make no change.
_Avoid_: Summarization, automatic memory update

**Consolidation Run**:
The auditable record of one Memory Consolidation, including its trigger, exact inputs, governing versions, and outcomes.
_Avoid_: Background job, memory refresh

**Memory Supersession**:
The replacement of an active Memory Revision by a successor from an effective time while preserving the predecessor's historical validity.
_Avoid_: Overwrite, edit

**Memory Correction**:
A Memory Supersession whose successor records that the preceding content was inaccurate.
_Avoid_: Silent fix, mutation

**Memory Retraction**:
The invalidation of a Memory Revision without a replacement while retaining its history and reason.
_Avoid_: Deletion, erasure

**Memory Trace**:
The exact recursive provenance and lifecycle history of a Memory Revision, including current validity and any unavailable evidence.
_Avoid_: Related items, activity history

**Current Memory View**:
The derived selection of active, actionable Memory Revisions available for personalization at a particular point in history.
_Avoid_: Memory snapshot, latest rows

**Tombstone**:
The minimal non-content provenance marker retained after an explicit privacy erasure removes a Raw Event payload.
_Avoid_: Deleted event, redacted copy

**Review Schedule**:
A deterministic projection from qualifying unaided retrieval evidence describing which Learning Objectives are due for review and when. Generated questions probe scheduled objectives but are not themselves scheduled unless explicitly saved.
_Avoid_: Spaced-repetition memory, mastery profile

## Privacy and data control

**Cloud Disclosure Grant**:
The learner's authorization for a named cloud provider to receive the minimum required context within a visibly disclosed source and Workspace scope. A materially broader scope or background cloud processing requires a new grant.
_Avoid_: Provider consent, cloud enabled

**Local-only Restriction**:
A learner control that prohibits a Source Revision and content derived from it from being disclosed to any cloud provider.
_Avoid_: Private source, offline mode

**Workspace Removal**:
The removal of a Source Revision from one Workspace's selection without removing it from the Source Vault or affecting other Workspaces.
_Avoid_: Delete source, detach file

**Local Trash**:
A recoverable 30-day holding state for normally deleted sources or Workspaces before their payloads and retrievable derivatives are removed.
_Avoid_: Privacy erasure, archive

**Privacy Erasure**:
An immediate learner-directed action that bypasses Local Trash, removes selected payloads and retrievable derivatives, retains only minimal Tombstones, and makes unsupported dependent memory non-actionable.
_Avoid_: Memory Retraction, normal deletion, redaction

**Transient Processing Artifact**:
A non-evidentiary provider request copy, cache, or rebuildable intermediate that expires automatically and carries no durable citation or learner-memory identity.
_Avoid_: Source Revision, Raw Event, Evidence Anchor

**Sensitivity Class**:
The handling category of stored or processed content: standard, sensitive, or secret. It is independent of whether the content is cloud-eligible or subject to a Local-only Restriction.
_Avoid_: Cloud permission, privacy level

**Secret Material**:
A credential, token, private key, or equivalent authority-bearing value that TutorDesk rejects or redacts from sources, Raw Events, prompts, exports, and backups and stores only through the operating-system credential facility.
_Avoid_: Sensitive source, provider setting

**Cloud Disclosure Record**:
A payload-free audit record of the provider, exact model, purpose, scope identifiers, content categories, size, authorization, timing, status, and usage for one cloud request.
_Avoid_: Prompt log, provider trace

**Portable Archive**:
A passphrase-encrypted export of selected TutorDesk data and provenance with its manifest, schema versions, hashes, Tombstones, and applicable audit metadata.
_Avoid_: Backup, database dump

**Recovery Backup**:
A passphrase-encrypted, installation-complete artifact for restoring one TutorDesk installation as a coherent whole. It is not selectively merge-imported into a running installation.
_Avoid_: Portable Archive, export, raw database dump

**Inspection Export**:
A human-readable export of explicitly selected records that may be unencrypted only after the learner reviews its scope and warning.
_Avoid_: Portable Archive, debug bundle

**Rebuildable Artifact**:
A non-authoritative product derived from retained inputs through a recorded build recipe, such as a retrieval chunk, embedding, render, transcript, or cache. It has no durable citation or learner-memory identity and may be evicted and regenerated.
_Avoid_: Source Revision, Raw Event, Recovery Backup

**Erasure Ledger**:
The current record of privacy erasures that is applied before restored data becomes accessible so historical backups cannot reactivate erased payloads.
_Avoid_: Tombstone list, deletion log

**Privacy Audit Record**:
An append-only, local, payload-free account of disclosure authorizations, cloud disclosures, restriction and retention changes, data-lifecycle actions, exports, backups, restores, and credential lifecycle actions.
_Avoid_: Telemetry, prompt log, activity analytics

**Sensitivity Assessment**:
A local-only classification aid that may recommend a higher Sensitivity Class and block suspected Secret Material but never silently lowers the learner's chosen class.
_Avoid_: Cloud moderation, automatic privacy decision

**Disclosure Bundle**:
The bounded, authorized context assembled for one cloud request from exact Evidence Anchors, required Session turns, required learner-state revisions, and its Cloud Disclosure Grant. It excludes unrelated Workspaces, unrestricted history, and undeclared data classes.
_Avoid_: Prompt dump, retrieval context, Workspace export

**Identifier-free Update Check**:
An optional learner-enabled request for release information that carries no installation identifier, usage data, source metadata, or diagnostics.
_Avoid_: Telemetry, background analytics

**Backup Recovery Key**:
A learner-controlled passphrase or key, independent of the current machine and provider credentials, that encrypts app-managed backups and cannot be recovered by a vendor.
_Avoid_: API key, device key, account recovery

**Retention Policy**:
The learner-controlled schedule governing how long payload classes remain available, including any Workspace-specific expiry and its previewed provenance consequences.
_Avoid_: Cleanup job, storage quota

**Operational Log**:
A local, payload-free, 30-day diagnostic record containing structured execution metadata and sanitized errors but no source excerpts, prompts, responses, credentials, or learner-state content.
_Avoid_: Privacy Audit Record, Raw Event, debug dump

**Local Debug Session**:
A warned, time-bounded diagnostic capture that may include additional local content and can leave TutorDesk only through an explicit Inspection Export.
_Avoid_: Telemetry, crash reporting, verbose logging

**Data Control Center**:
The local control surface for data inventory, sensitivity and execution restrictions, provider grants, retention, trash and erasure, exports, backups, and privacy audit inspection.
_Avoid_: Account settings, admin console, privacy portal

**Provider Data Policy Profile**:
A signed, versioned description of one exact provider route's training use, retention, stateful features, zero-retention eligibility, and processing-region behavior. Cloud eligibility is evaluated against this profile rather than a provider-wide claim.
_Avoid_: Privacy policy link, provider trust level

**Processing Region Constraint**:
An optional learner-selected routing requirement that permits cloud execution only when the Provider Data Policy Profile guarantees processing in the allowed region.
_Avoid_: Service availability region, billing region

**Local Execution Attestation**:
The verified runtime fact that a selected model executes on the learner's machine rather than merely being reached through a local endpoint.
_Avoid_: Localhost URL, local model name

**Authorized Egress**:
An outbound request admitted by TutorDesk's default-deny network seam for a declared destination, purpose, data class, and matching authorization.
_Avoid_: Network access, allowed URL

**Installation Erasure**:
The irreversible reset that stops active work and removes all TutorDesk-managed data, credentials, grants, backups, Tombstones, and audit history from the current installation.
_Avoid_: Privacy Erasure, uninstall, factory reset

## Agent Boardroom

**Agent Boardroom**:
A user-triggered, visible deliberation in which role-specialized agents evaluate learning evidence and prepare recommendations without directly changing the Learner Model.
_Avoid_: Meeting room, debate agent, multi-agent mode

**Boardroom Deliberation**:
A bounded Agent Boardroom undertaking governed by a learner-approved charter that fixes its question, Workspace and evidence scope, permitted learner-state scope, research allowance, provider routes, budget ceiling, and requested outcome. A scope expansion starts a linked successor Boardroom Deliberation rather than changing one already underway.
_Avoid_: Boardroom Session, agent run, open-ended debate

**Boardroom Role**:
A named deliberative perspective selected from a versioned catalog or defined by the learner. Every role inherits a non-editable policy core requiring charter compliance, evidence-grounded typed contributions, explicit uncertainty and contradiction handling, and no claim to tool, disclosure, approval, or write authority. Its visible, versioned role brief may shape analysis but cannot widen that authority.
_Avoid_: Agent identity, permission profile, system authority

**Boardroom Chair**:
The non-voting role that mediates immutable contributions between otherwise independent Boardroom Roles, applies the deliberation protocol, maps disagreements, preserves dissent, and assembles the Boardroom Report without gaining truth, approval, or domain authority. It evaluates candidates against declared evidence, relevance, benefit, harm, actionability, reversibility, and uncertainty criteria. Roles never invoke or message one another directly.
_Avoid_: Approver, decision maker, lead agent

**Boardroom Evidence Packet**:
The immutable common factual base for a Boardroom Deliberation, containing exact evidence and learner-state revisions within its approved charter. Role-specific projections may omit irrelevant material but cannot alter or introduce facts; newly admitted evidence creates a new packet revision shared in a later round.
_Avoid_: Prompt context, agent memory, evidence summary

**Boardroom Round**:
A visible phase of deliberation whose contributions use one immutable context manifest and Boardroom Evidence Packet revision. Deliberation begins with independent positions, permits one targeted critique-and-revision cycle and at most one conditionally justified additional cycle, and never continues merely to manufacture consensus. Learner intervention or newly admitted evidence starts a new round rather than rewriting completed reasoning.
_Avoid_: Chat turn, hidden chain of thought, retry

**Boardroom Disposition**:
The Boardroom Chair's non-authoritative classification of one candidate finding or recommendation as supported, contested, insufficiently evidenced, or out of scope under the declared evaluation criteria. It does not accept, reject, or otherwise decide a Memory Proposal for the learner.
_Avoid_: Verdict, vote result, approval

**Boardroom Finding**:
An evidence-backed conclusion in a Boardroom Report that changes no product or learner state.
_Avoid_: Boardroom Recommendation, memory fact, approved decision

**Boardroom Recommendation**:
A proposed learning adjustment produced by the Agent Boardroom at the smallest independently meaningful and reversible granularity, represented one-to-one as a Memory Proposal and unable to affect future learning until the learner explicitly approves it. An inseparable set may form one composite recommendation whose subchanges are exposed and applied all-or-nothing; unrelated changes are never bundled. Only supported or contested adjustments may become Boardroom Recommendations; insufficiently evidenced or out-of-scope candidates remain non-actionable report material.
_Avoid_: Board decision, automatic improvement

**Boardroom Report**:
The immutable, machine-readable outcome of a Boardroom Deliberation containing its charter and context identities, completion and stop state, roles and governing versions, Boardroom Findings, assessed adjustments, separately addressable Boardroom Recommendations, Boardroom Dissent, evidence and transcript references, validation results, resource usage, gaps, exclusions, and safe next actions. The report itself carries no approval authority; correction or continuation produces a linked successor deliberation and report rather than rewriting it.
_Avoid_: Consensus answer, meeting notes, mutable summary

**Boardroom Finalization**:
The idempotent transition that validates a Boardroom Report and submits its complete recommendation set to the memory module for all-or-nothing staging as one-to-one Memory Proposals without changing the Current Memory View. Failed staging leaves no actionable recommendation and is reported as a partial outcome that may be retried safely.
_Avoid_: Memory commit, report approval, automatic acceptance

**Boardroom Acceptance Reversal**:
A learner-directed, history-preserving compensation for an accepted Boardroom Recommendation using Memory Retraction, Correction, or Supersession after current-revision and dependency checks. It never rewrites the report, transcript, proposal, decision, Raw Event, or prior revision; composite recommendations reverse atomically, while recommendations accepted together as a batch remain independently reversible.
_Avoid_: Rollback, delete decision, restore history

**Boardroom Dissent**:
A role-authored, evidence-linked account of material disagreement attached directly to the affected finding or recommendation. It identifies the disputed proposition, alternative conclusion, disagreement kind, evidence, attempted resolution, and consequence if the dissenting view is correct; the Boardroom Chair may summarize but cannot replace it. Material unresolved dissent makes the affected item contested.
_Avoid_: Minority note, hidden objection, validation failure

**Boardroom Transcript**:
The durable semantic record of a Boardroom Deliberation, including its charter, selected and versioned roles, evidence revisions, structured positions, critiques, revisions, dissent, Chair actions, validation results, authorized tool events, usage, cost, and learner interventions. It excludes hidden model reasoning, raw token streams, provider-native traces, and Secret Material.
_Avoid_: Chain of thought, raw provider log, meeting transcript

## Release quality

**Complete Release**:
A TutorDesk release whose declared deployment, capability, source-format, language, and exact provider/model support matrix has passed every applicable Release Gate. Anything excluded or narrowed by a failed threshold is not advertised as complete-release support.
_Avoid_: Feature complete, production ready, generally available

**Release Gate**:
A versioned, reproducible acceptance predicate that must pass before a Complete Release. An invariant gate permits no violation; a threshold gate requires statistically reliable performance above a declared floor. Advisory diagnostics do not satisfy a Release Gate, and failures in provenance, privacy, authority, erasure, isolation, silent mutation, or data integrity cannot be waived.
_Avoid_: Quality metric, release checklist, best-effort test

**Certified Route**:
An exact provider and model route that has passed the applicable adapter-contract, privacy, resilience, budget, and output-quality Release Gates for its declared Capabilities. A material route or policy change requires recertification; an uncertified route is outside the Complete Release support matrix.
_Avoid_: Supported provider, preferred model, configured endpoint

**Evaluation Corpus**:
The versioned, learner-data-free evidence used to measure Release Gates, partitioned into public development fixtures, a locked release holdout excluded from tuning, and an adversarial or fault corpus. Results are reported independently for every material language, modality, Capability, route, and risk stratum so an aggregate score cannot hide a failing stratum.
_Avoid_: Test data, benchmark examples, prompt set

**Release Support Matrix**:
The exact declaration of deployment profiles, Capabilities, source formats, languages, provider/model routes, scale limits, and hardware baselines certified by one Complete Release. Narrowing the matrix removes the excluded behavior from the release claim rather than waiving a failed gate.
_Avoid_: Feature list, compatibility promise, supported providers

**Release Evaluation Report**:
The immutable human-readable and machine-readable evidence that one exact distributable artifact passed the Release Gates for its declared Release Support Matrix. It records artifact and corpus identities, routes, policies, environments, per-stratum results, human adjudication, regressions, exclusions, and certification status without disclosing the locked holdout contents.
_Avoid_: Test report, QA summary, release notes
