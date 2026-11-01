# Warm Precision

This repository holds the Warm Precision handbook and reusable design system.

Present informational documents as browsable local web pages by default. Keep Markdown as the editable and portable source, include the generated page in the handbook, and provide a direct page link in the handoff. Root-level `README.md` and `AGENTS.md` are not handbook pages; `BRAND_KIT.md` is registered separately.

Design the web edition as a distilled explanation: lead with the takeaway and next decision, visualize relationships or processes where that improves understanding, and move implementation detail into a linked reference or disclosure. A long Markdown-to-HTML transcription is not a finished informational page.

Read `design-system/PHILOSOPHY.md`, the selected profile in `design-system/profiles/` (Warm Precision by default), and the relevant medium adapter before design work. Pick the document type from `design-system/DOCUMENTS.md`, write copy to `design-system/VOICE.md`, and present data with `design-system/adapters/data.md`. For animation and video, use `design-system/adapters/scenes.md`; a scene described in words can be written up with `design-system/templates/SCENE_BRIEF.md`. Exact values belong in the profile's `tokens.json`; the marked tables in `BRAND_KIT.md` are generated.

Edit the source under `design-system/` and rebuild with `python3 design-system/scripts/build.py --embed-fonts`. Add `--watch` to rebuild on every save. Designed handbook sections live in `design-system/scripts/specimens.py`; local working pages in `reviews/` render automatically and are git-ignored. Generated handbook pages live under `handbook/` (ignored build output).

Run `python3 design-system/scripts/build.py --check` and `python3 design-system/scripts/test_build.py` after relevant changes. Review rendered output for changes to layouts or visual rules.
