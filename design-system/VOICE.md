# Voice

**Say what it is, show the number, stop.**

These are the corrections that come up again and again when editing technical and research writing, whether a person or an agent drafted it. They are written down as rules so nobody has to ask for them twice.

## The rules

1. **Say what it is in the first line.** Use words a smart outsider already knows. A tool page that never says what the tool reads or produces has failed, however precise it is.
2. **Keep the workshop out of public copy.** Gates, phases, checkpoints, run IDs, claim IDs and internal codenames stay in plans and handoffs. Public copy says what was done and what was found.
3. **Let the number carry the confidence.** Give the figure, its unit and its scope. Drop the adjective that was doing the number's job.
4. **Write one point where you drafted three.** If a section has three bullets, check whether one of them is the point and the other two are padding.
5. **Vary sentence length.** Short sentences are welcome. A paragraph of identical medium-length sentences reads as generated.
6. **No em dashes.** Use a period, comma, colon or parentheses. This applies to published prose, UI copy, captions and social posts.
7. **Define a technical term once, in passing.** "Mechanistic interpretability, which looks inside a model for what drives its outputs." Then use the term.
8. **Disclose what, not how.** For commercial work, describe capability and results. Methods, model stacks and internal tool names stay private unless you choose to publish them.
9. **No launch theatre.** No "Introducing", no slogans as headings, no status dots or badges as decoration, no emojis, no titles on social posts.
10. **End handoffs with the next move.** A command, a link, a question or a decision. Not a summary of what was just said.

## Registers

One set of facts, three ways of speaking. Pick the register from the reader, not the project.

| Register | Reader | Sounds like | Avoid |
| --- | --- | --- | --- |
| Organization | Partners, funders, reviewers | Confident, factual, sparing. "Most reports arrive a week after the data. Ours arrive the same morning." | Process detail, hedged adjectives, method disclosure |
| Personal | People who found your site or a post | Dry, specific, a little odd, not too serious. "I build small tools for reading my own data, and tend to take a question further than I meant to." | Career-page polish, mission statements, humblebrag lists |
| Research | Quantitative readers, analysts, reviewers | Neutral and exact. What was done, what was found, how sure, what it does not show. | Experiment tracking language, enthusiasm, causal claims the design cannot support |

Prompts to agents are often lowercase shorthand. That is a working register between a person and a tool. Published work does not copy it.

## Kept and cut

Typical edits, before and after.

| Before | After | What changed |
| --- | --- | --- |
| Validated on 39 benchmark cases (Gate 0 passed with 27/43 reviewer-verified results), scaling to production workloads. | Validated on 39 benchmark cases, with 27 reviewer-verified results, scaling to production workloads. | The gate is gone; the numbers stay. |
| The method combines retrieval—finding the passages that matter—with re-ranking: ordering them by how well they answer the question. | The method combines retrieval, which finds the passages that matter, with re-ranking, which orders them by how well they answer the question. | Em dashes become definitions in passing. |
| Your data, reimagined. | Ledger. Your spending by category and month, drawn from the CSV your bank exports. | A slogan becomes a name and a description. |
| Introducing Ledger (with a glowing dot) | Ledger / spending reports from bank exports | Launch theatre becomes a plain label. |
| Three bullets on continuous learning | One sentence | Two of the three were padding. |

## Phrases to cut on sight

- **Inflated verbs:** spearheaded, leveraged, synergized, elevated, empowered, unlocked, revolutionized, transformed.
- **Empty adjectives:** robust, seamless, cutting-edge, holistic, dynamic, pivotal, passionate, world-class, powerful.
- **Stock frames:** "In today's fast-paced world", "It's not just X, it's Y", "Here's the thing", "Let's dive in", "The result?", "game-changer", "at the intersection of".
- **Self-description:** results-driven, detail-oriented, thought leader, track record, seasoned.
- **Hedge stacks:** "may potentially", "could possibly help to", "it is important to note that".

A banned word is a symptom. Replace it with the specific fact it was hiding, or delete the sentence.

## By document

- **Headlines and titles** state the subject or the finding in plain words. A short display line may end with a period ("Field notes."). Display type is for that one line; everything else uses ordinary headings.
- **Ledes** say who it is for and what they get, in one or two sentences.
- **Figure titles** state the finding. Subtitles state the measure, unit, sample and period. See [data.md](adapters/data.md).
- **Buttons and links** name the action or the destination: "Download the kit", "Read the preprint". Never "Learn more" or "Click here".
- **Errors** name the problem and the fix.
- **Social posts** have no title, no hashtag block, no emojis. Open with the finding or the odd detail. Keep it short and a little humble.
- **Applications and forms** answer the question asked, at the length asked, in the order asked.
- **Handoff prompts** read like a work order: files to read, goal, where we stopped, constraints, first action.

## Check before publishing

- Does the first line say what this is, for someone who has never heard of it?
- Is there any gate, phase, run ID or codename a stranger would not understand?
- Is there an em dash anywhere?
- Is every adjective earning its place, or could a number replace it?
- Read it aloud. Does every sentence have the same rhythm?
- Would you be comfortable if the most expert person in the field read it?
