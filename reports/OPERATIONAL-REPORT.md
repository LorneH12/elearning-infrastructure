# Operational test report — 9 October 2026

Status: PARTIAL INFRASTRUCTURE PROOF. Not a complete deployed LMS.

Four upstream repositories cloned at recorded commits. Publication update: infrastructure repository and four upstream forks created in LorneH12. Existing builds untouched.

## Passed locally

- LRS rejects unauthenticated statement reads
- LRS stores valid completion
- LRS retrieves exact statement ID
- Identical retry is idempotent
- Conflicting duplicate rejected
- Malformed statement rejected
- Statement persists after LRS restart
- Gateway rejects unauthenticated writes
- Gateway rejects foreign origin
- Browser launches Adapt and opens lesson
- Browser event retrievable: initialized
- Browser event retrievable: experienced

Adapt web and SCORM 1.2 builds completed successfully. SCORM ZIP structure checked: root manifest, launch resource, standard version, enabled Spoor and excluded local xAPI bridge. This is not a SCORM conformance result.

## Not yet demonstrated

- Moodle installation, package import, enrollment, resume, grading and completion.
- Visual authoring editor create/edit/export. The pinned editor requires Node 16/18; the framework requires Node 22+.
- Production LMS identity binding to xAPI actors, offline retry, production hosting or accessibility conformance.
- Browser-driven course completion; completion persistence was tested using a synthetic API statement. Browser tests cover initialization and lesson entry.

## Environment limitations

No Docker or PHP in this runner; the package-manager installation attempt could not perform required system operations. The SQL LRS system Java 17 was too old; the official bundled runtime worked. Browser installation succeeded using the pinned Playwright release and its fallback download host.

## Publication update

The GitHub browser was authorized by the user and used to create the five public
repositories. Source publication uses a one-time, checksum-verified import workflow
because the GitHub connector rejects code writes. No existing portfolio repository
was changed. This does not change the operational test scope above.

## Next operational gate

Publish the new repositories, run the draft Docker lab on a suitable host, and import the SCORM package into Moodle. Resolve visual authoring runtime compatibility before exposing any editor.
