# IrisMix user study

Bilingual anonymous makeup comparison study for IrisMix (+ Stage II), MagicMakeup, ART, FLUX-Makeup and Stable-Makeup.

- **Private preview:** https://irismix-userstudy.zuw96work.chatgpt.site
- **Researcher dashboard:** https://irismix-userstudy.zuw96work.chatgpt.site/admin
- **Current materials:** 9/100 v2 public looks have all five outputs. This snapshot serves an **8-trial technical pilot** (one per baseline plus four attention checks), not the formal study. Baseline counts on the dashboard are a build-time snapshot, not live training progress.
- **Formal protocol:** 40 comparisons (10 per baseline) plus four checks; three questions per comparison: makeup fidelity, identity preservation and realism. The original exclusion thresholds are unchanged: at least two failed checks or median active response time below three seconds.

The server stores responses durably in Cloudflare D1, returns a receipt only after storage, validates the materials hash and complete balanced plan, and treats repeated identical submissions idempotently. Conflicting answers under the same response ID are rejected. Names, emails, IPs and user agents are not stored in response rows. Researcher exports require the configured owner account. QA records and pilot records are excluded from formal exports/analysis.

## Files

`work/user_study/STUDY.md` is the protocol, `HANDOFF_CODEX.md` tracks readiness, `build_trials.py` builds materials, `site/` contains the framework-independent questionnaire, and `analyze.py` validates and analyzes exported answers. `app/api/` contains the collector and protected export routes. `public/study/` is the serving copy of `site/`, refreshed with `node scripts/sync-study.mjs`.

## Local setup

Use Node.js 22.13+ and Python with Pillow:

```sh
npm ci
node scripts/sync-study.mjs
npm run build
```

For local collection, apply the generated SQL migration to local D1 using Wrangler (see the Sites starter documentation), then run `npm start -- --port 8183`. The `ADMIN_EMAIL` runtime environment variable must name the researcher account; keep local values in ignored `.dev.vars`, not source. Sites provisions the hosted DB and applies the committed migration at deployment. The production Site starts owner-private; this repository being public does not open respondent access to the Site.

## Update materials and freeze

On the original workstation, after baseline completion:

```sh
python work/user_study/build_trials.py --root /ssd1/chingheng/FlashMakeUp
# Review counts, public-v2 provenance and image loading first.
python work/user_study/build_trials.py --root /ssd1/chingheng/FlashMakeUp --freeze
node scripts/sync-study.mjs
```

`--freeze` refuses until **all 100 v2 looks** have outputs from all five methods. It then switches to 40+4, records the trials MD5/materials SHA-256 in STUDY.md and refuses subsequent overwrites. No current formal freeze is recorded. Changing the protocol/materials during collection requires a new version and separate analysis.

Before the first human rater, the researcher must confirm institution-specific ethics/IRB requirements or exemption (as required by the original handoff). Arrange 2–3 real-person pilots of the complete study after materials are ready; software QA is not a substitute for human participants or a validation of the 15-minute estimate. Record outcomes, then set `recruitment_open` in `work/user_study/site/config.json`, synchronize/build/deploy, and explicitly open the Site to the intended raters. No invitations have been sent and no human pilot has been claimed.

## Export and analyze

Use `/admin` to download response JSON. Exports default to excluding QA records and separate `pilot` from `formal`. The analyzer accepts the combined export or individual downloaded response JSON files:

```sh
python work/user_study/analyze.py responses.json --mode pilot --out pilot-analysis.json
python work/user_study/analyze.py formal-responses.json --mode formal --out analysis.json
```

It checks completeness, rejects materials mismatches, deduplicates response IDs, applies declared exclusions, and reports win rates, Wilson intervals, the unadjusted binomial test and a reproducible participant bootstrap. Wilson/binomial results are trial-level summaries; the participant bootstrap addresses rater clustering, not scene clustering. Conventional Fleiss kappa is only reported for eligible items with equal rater counts; otherwise the output explains why it is undefined.

## Verification

```sh
node work/user_study/test_core.mjs
python work/user_study/test_analysis.py
# With the local Worker and local test ADMIN_EMAIL configured:
node work/user_study/test_endpoint.mjs
node work/user_study/browser_qa.mjs
```

Endpoint/browser QA records are explicitly flagged as tests and are not real-person ratings. The tests cover plan balance, attention-check count, incomplete-freeze refusal, exclusions, storage, retries/conflicts, private exports, CORS, language switching, required questions, resume, mobile layout and actual QA receipts.

## Initial source release

The complete current pilot images are deployed on the private preview Site. Prepared JPG assets are not included in this initial GitHub commit; regenerate them from the public v2 inputs and baseline outputs with `work/user_study/build_trials.py`, then run `node scripts/sync-study.mjs` before local use. Formal materials remain unfrozen.
