# Documents

**Pick the document from the reader's goal, then follow its shape.**

Ten document types cover what gets made across these projects. Each has a default shape: the sections in order, with a rough size. Start from the shape and cut what the content does not need. Add a section only when the reader needs it to act.

## Choosing

| Reader's goal | Make | Mode | Pattern | Medium |
| --- | --- | --- | --- | --- |
| Understand something | Explainer page | Explain | Overview + detail | Web |
| Decide | Decision memo | Read | Decision + next step | Web or document |
| Know where things stand | Status summary | Read | Claim + evidence | Chat or web |
| Resume work in a fresh session | Handoff prompt | Operate | Decision + next step | Markdown |
| Trust a result | Preprint | Read | Annotated result | Web reader and PDF |
| Notice a finding | Figure card | Explain | Annotated result | Card |
| Follow a talk or a lesson | Slide deck | Persuade | Claim + evidence | Slides |
| Learn what a thing is | Landing page | Persuade | Artifact + inspection | Web |
| Run a tool | README | Operate | Artifact + inspection | Markdown and web |
| Answer a request | Form answer or email | Read | Claim + evidence | Plain text |

Modes are defined in [PHILOSOPHY.md](PHILOSOPHY.md); patterns in [patterns/README.md](patterns/README.md); media in [adapters/](adapters/).

## Defaults

- **Informational documents are local web pages.** Markdown is the editable source. The page is designed: takeaway first, a diagram or figure where it explains something, detail in disclosures or linked references.
- **Internal and public are different documents.** A plan, a handoff and a status summary may use gates, phases and file paths. Anything a stranger reads follows [VOICE.md](VOICE.md).
- **One document per goal.** If a page is trying to explain and persuade at once, split it.
- **Length is a ceiling.** Every size below is a maximum, not a target.

Sizes: *short* is a sentence or two, *medium* is a paragraph or a small figure, *long* is several paragraphs, a full figure or a table.

## Explainer page

For a reader who needs to understand a system, a result or a set of options. Default format for informational docs.

**Shape**

1. Title and takeaway (short)
2. The picture: diagram or figure (long)
3. Sections, one idea each (long)
4. What to do next (short)
5. Detail and sources in disclosures (medium)

Done when the takeaway and the picture alone would let the reader explain it to someone else.

## Decision memo

For you, or whoever signs off, when there is a choice to make.

**Shape**

1. The decision, as a question (short)
2. Recommendation (short)
3. Options compared on the same dimensions (long)
4. Risks and what would change the answer (medium)
5. Open questions (short)

Done when the reader can say yes, no or "option B" without asking anything.

## Status summary

For a returning reader or a supervisor who wants to know where things stand.

**Shape**

1. One-line state (short)
2. Done (medium)
3. What we have: outputs and where they live (medium)
4. What we found (medium)
5. Next (short)

Done when someone who missed the last week knows what exists and what happens next.

## Handoff prompt

For an agent starting a fresh session. Internal; file paths and gate names are fine here.

**Shape**

1. Read first: files, in order (short)
2. Goal for this session (short)
3. Where we stopped (medium)
4. Constraints and decisions already made (medium)
5. First action (short)

Done when a new session can begin work without asking what to read.

## Preprint

For a reader who needs to trust a result: researchers, analysts, reviewers.

**Shape**

1. Title stating the question or result (short)
2. Abstract (medium)
3. Key figure (long)
4. Method (long)
5. Results with uncertainty (long)
6. Limits and what it does not show (medium)
7. Sources, data and AI disclosure (short)

Follow the venue's structure when there is one. The web reader has a section sidebar; the PDF is the citable export. Done when every number traces to a source file and every figure has a source line.

## Figure card

For a phone reader scrolling past. Uses the card medium (1200 × 1200).

**Shape**

1. Wordmark (short)
2. Finding as the title (short)
3. One figure (long)
4. Measure, sample and source (short)

Done when the finding survives at phone width without zooming.

## Slide deck

For a room, a reviewer or a learner moving through an argument.

**Shape**

1. Title slide: the question (short)
2. One assertion per slide, with its evidence (long)
3. Qualification slide (medium)
4. Implication or ask (short)

Slide titles are assertions, not topics. Done when reading only the titles tells the story.

## Landing page

For a stranger deciding whether this is for them.

**Shape**

1. What it is, in one line (short)
2. Proof: the artifact, a figure or a working demo (long)
3. What you get (medium)
4. One action (short)

Done when a stranger can say what it is and what to click within five seconds. No slogans.

## README

For someone about to run the tool, or their agent.

**Shape**

1. Name and what it reads or does (short)
2. One working command (short)
3. What it does not do: privacy, limits (short)
4. Options (medium)
5. Development (short)

Done when the first command works on a clean machine.

## Form answer or email

For one reader who asked something specific: a grant form, an application, a boss.

**Shape**

1. The answer (short)
2. Supporting facts (medium)
3. The ask or next step (short)

Answer the question asked, at the length asked. Done when nothing in it could be cut without the reader asking for it back.
