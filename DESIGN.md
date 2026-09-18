---
name: TutorDesk Evidence Conservation Lab
description: A source-first learning workstation built from archival evidence, examination layers, and explicit human approval.
colors:
  mineral-paper: "#f0f3f0"
  specimen-white: "#fbfcfa"
  mineral-muted: "#dce2de"
  graphite: "#24302b"
  graphite-muted: "#58645e"
  measurement-line: "#9da59e"
  hairline-soft: "#cbcfc8"
  oxidized-green: "#477c72"
  oxidized-green-deep: "#29564e"
  oxidized-green-wash: "#d9e6e1"
  accession-orange: "#93411f"
  accession-orange-wash: "#f2ddd1"
  caution-oxide: "#733421"
  focus-blue: "#0b67a0"
  inverse-white: "#ffffff"
typography:
  display:
    fontFamily: "Atkinson, system-ui, sans-serif"
    fontSize: "clamp(1.7rem, 2.6vw, 2.7rem)"
    fontWeight: 700
    lineHeight: 1.02
    letterSpacing: "-0.028em"
  title:
    fontFamily: "Atkinson, system-ui, sans-serif"
    fontSize: "1.22rem"
    fontWeight: 700
    lineHeight: 1.2
  body:
    fontFamily: "Atkinson, system-ui, sans-serif"
    fontSize: "clamp(1rem, 1.1vw, 1.12rem)"
    fontWeight: 400
    lineHeight: 1.66
  label:
    fontFamily: "Barlow Lab, Arial Narrow, sans-serif"
    fontSize: "0.73rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.11em"
rounded:
  square: "0px"
  capsule: "999px"
spacing:
  micro: "4px"
  compact: "7px"
  control: "11px"
  field: "12px"
  panel: "16px"
  section: "24px"
components:
  button-primary:
    backgroundColor: "{colors.oxidized-green-deep}"
    textColor: "{colors.inverse-white}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "7px 11px"
  button-secondary:
    backgroundColor: "{colors.specimen-white}"
    textColor: "{colors.graphite}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "7px 11px"
  button-reject:
    backgroundColor: "{colors.specimen-white}"
    textColor: "{colors.caution-oxide}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "7px 11px"
  citation-trigger:
    backgroundColor: "{colors.specimen-white}"
    textColor: "{colors.oxidized-green-deep}"
    typography: "{typography.label}"
    rounded: "{rounded.capsule}"
    padding: "1px 6px 2px"
  status-pending:
    backgroundColor: "{colors.specimen-white}"
    textColor: "{colors.accession-orange}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "2px 7px"
  status-approved:
    backgroundColor: "{colors.specimen-white}"
    textColor: "{colors.oxidized-green-deep}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "2px 7px"
  examination-card:
    backgroundColor: "{colors.specimen-white}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.square}"
    padding: "12px"
  review-card:
    backgroundColor: "{colors.accession-orange-wash}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.square}"
    padding: "12px"
---

# Design System: TutorDesk Evidence Conservation Lab

## Overview

**Creative North Star: "Evidence Conservation Lab"**

TutorDesk treats knowledge as material under examination. Mineral paper, graphite notation, oxidized-green evidence marks, accession-orange review layers, hairline rules, and tabular identifiers make the interface feel like a working conservation bench: exacting, quiet, and visibly accountable.

The active source is the artifact, not background for a chat stream. Explanations, questions, provenance, and learner-state proposals appear as reversible examination layers beside the evidence that produced them. The system is dense without feeling compressed, and every consequential state change remains visibly subject to human approval.

**Key Characteristics:**

- Source-as-artifact rather than chat-as-center.
- Archival labels, accession marks, and hairline measurement rules.
- Mineral-white planes with graphite text and sparing chromatic state.
- Exact provenance exposed beside claims and learner-state inferences.
- Square controls and layered review materials with explicit approval states.

## Colors

The palette behaves like a mineral light table: warm-cool whites carry the working planes, graphite carries content, oxidized green marks evidence, and accession orange reserves attention for reviewable state.

### Primary

- **Oxidized Green:** Use the base, deep, and wash tokens for evidence, grounded or selected state, citation paths, and active learning instruments.

### Secondary

- **Accession Orange:** Use the saturated mark and pale wash for pending review, accession identifiers, and human-approval layers; it is not a general decorative accent.

### Tertiary

- **Caution Oxide:** Reserve for rejection or caution actions that require an explicit semantic distinction from pending review.
- **Instrument Focus Blue:** Reserve for keyboard focus outlines so accessibility state remains unmistakable against both chromatic systems.

### Neutral

- **Mineral Paper:** The primary environmental plane and quiet source-vault surface.
- **Specimen White:** The clearest reading, control, and source-sheet surface.
- **Muted Mineral:** The application ground, disabled control fill, and scrollbar track.
- **Graphite:** Primary text, strong dividers, and structural outlines.
- **Muted Graphite:** Metadata and subordinate explanation.
- **Measurement Line and Soft Hairline:** Structural partitions, evidence steps, and low-emphasis separators.
- **Inverse White:** Text placed on deep evidence or graphite fields.

### Named Rules

**The Chromatic Evidence Rule.** Green means grounded, selected, or traceable; orange means pending human review; neither color is ambient decoration.

**The Visible Focus Rule.** Keyboard focus uses the dedicated blue outline and must never be replaced by a subtle color shift.

## Typography

**Display Font:** Atkinson (with system-ui and sans-serif fallback)

**Body Font:** Atkinson (with system-ui and sans-serif fallback)

**Label Font:** Barlow Condensed, exposed by the runtime alias Barlow Lab (with Arial Narrow and sans-serif fallback)

**Character:** Atkinson keeps dense source reading unusually clear, while Barlow Condensed gives accession labels and controls the compressed authority of archival equipment. The contrast comes from role, width, case, and spacing rather than ornamental display type.

### Hierarchy

- **Display:** The display token is reserved for source titles and primary artifact identity.
- **Title:** The title token names ledger rows, panels, and evidence groupings without competing with the source title.
- **Body:** The body token carries source excerpts and sustained reading, with source copy constrained to approximately 71 characters per line.
- **Label:** The label token is uppercase and tightly line-boxed for accession IDs, instrument names, state stamps, and compact navigation.

### Named Rules

**The Two-Voice Rule.** Atkinson carries meaning; Barlow Condensed carries classification, state, and control.

## Layout

The system is desktop-first and information-dense. It gives the active source the largest uninterrupted region, keeps workspace, source-vault, and capability context visible, and attaches provenance and approvals to the evidence they describe. A persistent consolidated review entry point prevents contextual proposals from becoming hidden obligations.

Spatial rhythm is built from hairline-divided regions and the frontmatter spacing scale rather than floating card gutters. Full-workstation arrangements adapt at the observed intermediate breakpoint of 1050px; at 760px, context condenses, parallel planes become a readable sequence, and controls meet a 44px touch target. This responsive change preserves source priority and review access rather than reproducing desktop columns at a smaller size.

**The Source Majority Rule.** In every workstation composition, the source remains the largest or first reading plane; capability controls orbit it rather than becoming a dominant chat rail.

## Elevation & Depth

The system is flat by default and layered when meaning requires it. Tonal washes, transparency, borders, grid paper, and physical overlap carry most depth. The raised-plane shadow is reserved for an examination sheet or an open review drawer; selected ledger rows use an inset evidence edge instead of ambient lift.

### Shadow Vocabulary

- **Raised Examination Plane:** A broad graphite-tinted shadow separates a source sheet or active drawer from the lab bench.
- **Selected Evidence Edge:** A solid inset oxidized-green edge marks the active source row without implying that it floats.

### Named Rules

**The Evidentiary Depth Rule.** A layer may rise only when its overlap communicates source, provenance, or approval state.

## Shapes

Working surfaces and controls are square, bordered, and aligned to the archival grid. Hairline rectangles are the default silhouette; clipped geometry may appear as an accession detail, but rounded cards are outside the language. The single deliberate exception is the fully rounded citation capsule, whose distinct outline signals an inline path back to evidence.

**The Capsule Exception Rule.** Only inline citation triggers use the capsule radius; actions, stamps, panels, and navigation remain square.

## Components

Components should feel like precise lab instruments: terse, bordered, stateful, and legible under sustained use.

### Buttons

- **Shape:** Square archival controls with a strong hairline border.
- **Primary:** Deep oxidized green with inverse text marks a positive approval or selected instrument.
- **Hover / Focus:** Hover uses the oxidized-green wash; keyboard focus uses the dedicated blue outline. Pressed and selected state must remain visible without motion.
- **Secondary:** Specimen white with graphite text is the default instrument treatment.
- **Reject:** Specimen white with caution-oxide text and border distinguishes rejection from both pending and approved state.
- **Disabled:** Muted mineral with muted graphite, a struck label, and a not-allowed cursor makes resolution explicit.

### Chips

- **Citation Trigger:** The capsule exception pairs specimen white with a deep oxidized-green outline; selected and hover states invert to the deep green field.
- **Status Stamp:** Square, uppercase, and outlined in the semantic state color. Pending uses accession orange; approved or grounded uses deep oxidized green.

### Cards / Containers

- **Corner Style:** Square, with no ambient corner softening.
- **Background:** Specimen white for evidence; oxidized-green wash for selected or grounded material; accession-orange wash for reviewable proposals.
- **Shadow Strategy:** Flat by default; only raised examination planes use the shadow vocabulary.
- **Border:** One-pixel measurement lines define containment and sequence.
- **Internal Padding:** Dense field or panel spacing from the normative scale.

### Navigation

Workspace identity, source-vault context, capabilities, and review state use divided instrument bars. Default controls stay transparent or specimen white; active controls invert to deep oxidized green. On narrow screens, global context condenses into a two-part bar and capabilities become a sticky horizontal dock.

### Evidence Peel and Provenance Path

Selecting a claim reveals its complete evidence path as an examination layer. The reveal uses a short left-origin peel, while nodes remain square and connected by one-pixel oxidized-green rules. Learner insights must show the full Learner Insight → Contextual Fact → Raw Event chain; source claims must terminate at an immutable source revision.

### Review Layer

Memory Proposals and Boardroom Recommendations use accession-orange review material, a visible pending stamp, and adjacent approve/reject actions. Resolved items switch to the grounded wash, retain their decision, and remain available in the consolidated review drawer.

## Do's and Don'ts

### Do:

- **Do** make the source the primary visual artifact and attach claims to exact visible provenance.
- **Do** use accession labels, revision identifiers, and tabular numerals to make evidence feel inspectable.
- **Do** keep contextual approval controls beside the proposal and repeat every unresolved item in the consolidated queue.
- **Do** preserve readable body copy, clear keyboard focus, reduced-motion behavior, and 44px narrow-screen touch targets.
- **Do** use material layers, hairlines, and tonal washes before reaching for shadow.

### Don't:

- **Don't** organize the workstation around a dominant chat rail.
- **Don't** use gradients, glassy floating cards, soft rounded dashboards, or decorative color as substitutes for hierarchy.
- **Don't** hide provenance behind a secondary journey or summarize away the exact citation path.
- **Don't** use green and orange interchangeably; their evidentiary meanings are fixed.
- **Don't** imply that a learner-state mutation has happened before explicit human approval.
