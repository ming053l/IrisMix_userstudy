# Hand-off: what is left for the user-study tooling

Ready (tested): `STUDY.md` (design, exclusion rule, analysis), `build_trials.py` (materials), `site/index.html`
(questionnaire, zh-TW / English, randomised 40 trials + 4 attention checks, results POST or download), `analyze.py`
(exclusions, win rates, Wilson intervals, binomial test, per-rater bootstrap; tested on synthetic files).

To do:
1. **Hosting**: serve `site/` as static files (any static host). The page reads `trials.json`, `config.json` and `img/`.
2. **Result collection**: set `site/config.json` -> `submit_url` to an endpoint that accepts a JSON POST and stores one file
   per rater (e.g. a small serverless function, or a Google Apps Script web app writing to a sheet / Drive). It must allow
   CORS from the hosting origin. Without an endpoint the page offers a download instead.
3. **Freeze**: after every baseline has finished on `pairs_100_v2.json`, run `python build_trials.py` once, record the
   printed `trials.json` md5 in STUDY.md, and do not change the materials during collection.
4. **Pilot**: 2-3 people; check timing (~15 min), image loading on phones, and that the attention checks are obvious.
5. **Analysis**: put the collected JSON files in `results/` and run `python analyze.py`.

Constraints: only the public LayerBeauty hybrid looks (no CPM-Real / MF2K images); raters must be people (no AI raters);
no personal data beyond the optional experience level; check IRB / ethics requirements before the first rater.

## Codex implementation status (2026-10-25)
Completed in `ming053l/IrisMix_userstudy`:
- Sites private preview, same-origin JSON POST collector backed by D1, protected researcher dashboard/export.
- Idempotent storage receipts, full-plan/version validation, CORS allowlist, local backups, optional experience, consent, saved plan/answers, and active viewing time excluding hidden tabs/image loads.
- Generator now refuses an incomplete formal freeze; current 9 looks serve an explicit 8-trial technical pilot covering all four baselines plus four checks. Formal 40+4 is preserved for complete materials.
- Analysis validates complete plans, deduplicates IDs, separates QA/pilot/formal, preserves exclusions, and reports reproducible statistics with limitations.
- Unit, simulated-analysis, API and browser QA are available under this directory.

Still pending: baseline completion; final regeneration + freeze/MD5; researcher ethics/IRB confirmation before any human rater; 2–3 actual full-study human pilots; explicit respondent access and formal recruitment opening. No scheduled automation or invitation has been created.
