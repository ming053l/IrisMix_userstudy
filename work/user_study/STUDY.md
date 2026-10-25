# IrisMix user study (pairwise preference, 2AFC)

Goal: human judgement of multi-reference makeup transfer, complementing the automatic metrics of Tab. 2 and the VLM judge.

## Design
- **Task**: each trial shows the source face, the three references with the part taken from each (eyes / lips / face paint
  or forehead), and two results A and B. Raters answer three forced-choice questions:
  1. *Makeup*: which result reproduces the requested makeup from the references more faithfully?
  2. *Identity*: which result better keeps the person of the source (face, expression, hair, background)?
  3. *Realism*: which result looks more like a natural photograph?
- **Comparisons**: IrisMix (+ Stage II, the Tab. 2 row) vs. MagicMakeup, ART, FLUX-Makeup and Stable-Makeup (the
  diffusion baselines of Tab. 2), on the hybrid looks of `work/gpt_compare/pairs_100_v2.json` (public LayerBeauty data
  only; CPM-Real and MF2K images are never shown).
- **Per rater**: 40 trials = 10 per baseline, looks drawn at random without repetition for that rater, left/right
  position randomised per trial, method names hidden. Plus 4 attention checks (one side is the unchanged source with no
  makeup; the makeup question has a known answer). Expected time about 15 minutes.
- **Raters**: real people only (no AI raters - that is the VLM judge). Target 20-30 raters. No personal data collected
  beyond an optional self-reported makeup experience level; each rater gets a random id.
- **Exclusion rule (declared now)**: drop a rater who fails 2 or more of the 4 attention checks, or whose median response
  time per trial is below 3 s.
- **Analysis**: per baseline and question, the IrisMix win rate with a 95% Wilson interval over all trials, plus a
  per-rater bootstrap; a two-sided binomial test against 0.5; agreement as Fleiss' kappa on items rated by several raters.

## Files
- `build_trials.py` - writes `site/trials.json` and the resized images `site/img/` from the method outputs (run after
  every method has finished on pairs_100_v2; it lists any look missing an output and leaves it out).
- `site/index.html` - self-contained questionnaire (no external libraries). Results are POSTed as JSON to the endpoint in
  `site/config.json` (`submit_url`), or downloaded as a file when no endpoint is set.
- `analyze.py` - reads the collected result files and prints the table (win rates, intervals, tests, exclusions).

## Before running
- Check whether the institution requires IRB / ethics review or an exemption for anonymous preference ratings.
- Freeze `trials.json` (md5 in this file) before the first rater; do not change it during collection.

## Deployment readiness (2026-10-25)
- Current snapshot: 9 complete public v2 looks. Formal 40+4 materials are **not frozen**.
- Technical preview only: four comparisons (one per baseline) plus four checks; eight distinct looks. This does not validate the formal duration or sample size.
- Private preview and D1 collection are implemented. Three questions and the declared exclusion thresholds are unchanged. Resume, active-time measurement, materials-version validation and deduplicated receipts are implemented.
- Image sources are restricted to v2 `syn/test`, `creative/test` and `creative/unseen_style`; references are public Creative held-out splits. Builder provenance records source and displayed-image SHA-256 values. No CPM-Real or MF2K material is copied.
- IRB/ethics confirmation, the 2–3 real-person full-length pilot and formal recruitment remain researcher tasks. Automated QA is flagged separately and excluded from human analysis.
- Statistical reporting: the binomial test/Wilson interval are unadjusted trial-level summaries; participant bootstrap intervals address rater clustering only. Conventional Fleiss kappa is undefined for an unbalanced number of ratings and is not fabricated for those samples.
