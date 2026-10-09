# Portfolio Learning Infrastructure — operational lab

Infrastructure proof for seven future ID, OCM and L&D portfolio samples. This is
not a production LMS, a finished course, or an Oracle product clone. Existing
portfolio repositories are not used or modified.

## Components

| Component | Source | Local role |
|---|---|---|
| Adapt Framework 5.56.3 | adaptlearning/adapt_framework | Working course build pipeline |
| Adapt Authoring 0.11.5 | adaptlearning/adapt_authoring | Cloned, visual editor evaluation pending |
| Moodle 4.5 stable revision | moodle/moodle | Cloned, draft Docker deployment pending execution |
| SQL LRS 0.9.9 | yetanalytics/lrsql | Real local xAPI store with persisted SQLite data |
| Portfolio bridge | extensions/adapt-portfolio-xapi | Course initialized/page experienced/completed events |
| Local gateway | gateway/server.mjs | Assigns synthetic actor and forwards validated events |

Exact source commits are in `upstreams.lock.json`. Plugin versions, framework
npm dependency lock and LRS release checksum are committed separately. The checksum
records the archive obtained in this build, not an independent publisher signature.

## Separation and reuse

- `course-source/`: editable JSON content and course assets, separate from engine.
- `extensions/`: reusable tracking behavior.
- `gateway/`: backend code; LRS credentials are never embedded in course files.
- `deployment/`: server configuration.
- `scripts/`: setup and package generation.
- `tests/` and `reports/`: operational evidence.
- `dist/web/` and `dist/scorm/`: generated outputs; not hand-edited.
- `vendor/`: isolated upstream clones, fetched by bootstrap and ignored by parent git.

Adapt uses its native generated `index.html`, `adapt.css`, JavaScript directories,
and course asset folders. Do not flatten its internal structure merely to rename
folders. Future branding belongs in an Adapt theme; a theme-switching UI is not
implemented in this proof. Current course activities are Adapt's upstream samples.

## Reproduce tested local path (Linux x86_64)

Requires Git, Python 3, Node 22+, npm, outbound access and Chromium dependencies.
No Docker is required for the tested LRS/player path.

```sh
python3 scripts/bootstrap.py
python3 scripts/setup-framework.py
python3 scripts/setup-lrs.py
npm ci
npx playwright install chromium --only-shell
python3 scripts/build-course.py --format scorm
python3 scripts/build-course.py --format web
python3 tests/operational.py
```

The test starts/stops a real LRS using its bundled Java runtime and local gateway,
uses only synthetic identities, launches a headless browser, and verifies stored
records by ID. Secrets, logs, databases, downloaded runtimes and installed packages
are ignored. Report files contain no credentials. Run one test process at a time.

`dist/infrastructure-scorm12.zip` is the generated SCORM candidate. A successful
build is not proof of Moodle import, resume behavior, or SCORM conformance.

## Draft Moodle/LRS Docker lab — not yet operationally tested

```sh
python3 scripts/bootstrap.py
python3 scripts/create-env.py
docker compose up --build
```

Moodle: http://localhost:8080 ; LRS: http://localhost:8090.
Credentials are generated into `.env` with restrictive permissions. Database and
course data use named volumes. Do not expose these ports publicly. Docker image
tags still need pull/start verification and digest pinning on the deployment host.
This lab does not install a Moodle-to-LRS reporting plugin. Web builds send xAPI
through the local gateway; SCORM builds use the LMS's SCORM API instead.

Moodle needs cron, HTTPS, backup/restore, email, approved public identity/auth,
updates and course import/resume tests before public operation. SQL LRS seed admin
credentials must be replaced through its admin workflow before deployment.

## Visual authoring decision remains open

The released Adapt editor supports Node 16/18, while this framework requires
Node 22+. The editor has been cloned but not installed or represented as working.
Do not put it on the public internet. Evaluate a maintained editor release or
eXeLearning rather than silently forcing incompatible versions. Editing course JSON
and building Adapt is the authoring route demonstrated in this lab.

## Publication

Published infrastructure: [elearning-infrastructure](https://github.com/LorneH12/elearning-infrastructure).

Upstream forks (original licenses and history preserved):

- [Adapt player](https://github.com/LorneH12/learning-player-adapt)
- [Adapt authoring](https://github.com/LorneH12/learning-authoring-adapt)
- [Moodle LMS](https://github.com/LorneH12/learning-lms-moodle)
- [SQL LRS](https://github.com/LorneH12/learning-lrs-sql)

`upstreams.lock.json` now fetches these forks at the tested commit IDs and records
the original upstream URLs. Runtime databases, credentials and reference photographs
are excluded. Each future course will have its own repository.

## Acceptance gates still outstanding

- Visual editor create/edit/export test.
- Moodle installation and real course upload/launch/resume/score/completion test.
- LMS-authenticated actor mapping and end-to-end LMS/LRS integration.
- Offline retry queue, delivery receipts UI and cross-device resume policy.
- Keyboard/screen-reader/manual accessibility and WCAG 2.2 AA review.
- Company branding, permissions for assets, and all seven original course samples.
- Public hosting, operations, security review and backup restoration.

## Licenses

Infrastructure and custom Adapt extension: GPL-3.0 (see LICENSE). Copied sample
course material is from Adapt Framework under its upstream GPL-3.0 license.
Adapt and Moodle retain GPL-3.0; SQL LRS retains Apache-2.0. Clones retain original
license and notice files. Third-party packages retain their own licenses.
