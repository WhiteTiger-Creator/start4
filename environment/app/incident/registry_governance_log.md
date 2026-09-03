# Package Registry Resolution Reconciler — Governance Review Log
Registry governance archive for the failed registry-migration rollout (2026-Q1 through 2026-Q2).

## Executive Summary
How the resolution reconciler is *meant* to behave — the recovery of a truncated registry index, canonicalization, request deduplication, the version precedence, constraint satisfaction, the conflict/selection strategy, pin overrides, the yanked and pre-release admission rules, the per-channel resolution ledger, cycle handling, install ordering and the capacity cap — was settled incrementally by the registry governance board, and those decisions live in the review entries below, not in any single summary. Several stages deliberately depart from standard semver and pip resolution, and which ones they are is settled in the entries below rather than here. The February draft proposals were revisited during the 2026-05 governance review and several were reversed, and the index-recovery entries were revisited again in 2026-06; where a draft or interim conflicts with a later decision, the later dated decision governs. `/app/docs/report_spec.json` is the output contract only.

## Governance Review Archive
A shift handover carried forward a routine observation. A duplicate order was cancelled at source and never reached the run. Logged for trend purposes only.

### Review entry 1000 — registry-core (primary index) lane
A shift handover recorded a routine observation. The downstream vendor confirmed receipt inside the agreed window. Raised, discussed briefly, and dropped.
The reconciliation desk noted a routine observation. Late inputs arrived from one feed and were loaded before the cut. Filed alongside the cycle's other notes.

### Review entry 1001 — publish (edge worker) lane
The duty analyst raised and closed a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. No action was carried forward.
An on-call engineer filed a routine observation. A batch retried once after a transient timeout and completed on the second pass. Nothing here bears on engine behaviour.

### Review entry 1002 — resolver (control plane) lane
The audit lead filed a routine observation. An operator asked whether a credit had posted; it had, in the preceding period. No change to the approved parameters resulted.
> **Recovery draft proposal (2026-02-06 - #REG-7004)** Anders: version precedence is standard semver: compare (major, minor, patch) then the pre-release identifiers, and build metadata (the +N suffix) is IGNORED for ordering, exactly like semver *(Superseded — reversed in the 2026-05 governance review.)*
A shift handover raised and closed a routine observation. The count sat a little above the running mean, entirely from estimated inputs. The matter was not pursued.

### Review entry 1003 — mirror (west) lane
The duty analyst filed a routine observation. A typo in a reference record was corrected before the run started. Filed for the record.
An on-call engineer filed a routine observation. The variance sat inside tolerance and no adjustment was raised. No follow-up was requested.

### Review entry 1004 — quarantine (north) lane
The exceptions queue owner logged a routine observation. A query about a prior-period entry was answered from the published schedule. Referred to the dated decisions and closed.
A weekly review spot-checked a routine observation. A typo in a reference record was corrected before the run started. The reviewer signed it off the same day.

### Review entry 1005 — channel-canary lane lane
The controls team noted a routine observation. A query about a prior-period entry was answered from the published schedule. No dissent was recorded.
A reviewer on shift filed a routine observation. A batch retried once after a transient timeout and completed on the second pass. The observation stood without amendment.

### Review entry 1006 — registry-core (primary index) lane
The reconciliation desk opened a query on a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. The desk confirmed no downstream impact.
> **Recovery draft proposal (2026-02-08 - #REG-7008)** Rosa: conflict resolution selects the HIGHEST satisfying version of each package, matching pip's default resolver *(Superseded — reversed in the 2026-05 governance review.)*
A weekly review reviewed a routine observation. A batch retried once after a transient timeout and completed on the second pass.

### Review entry 1007 — publish (edge worker) lane
The duty analyst filed a routine observation. One record appeared twice in the export after a mid-cycle correction. A second reviewer concurred.
> **Recovery draft proposal (2026-02-05 - #REG-7002)** Anders: should the migration ever truncate the registry index, rebuild it by concatenating the pre-migration snapshot and the replay journal package by package and let the #REG-7104 precedence sort settle whatever overlaps; journal bookkeeping fields are inert and may stay on the release records *(Superseded — reversed in the 2026-06 governance review.)*
A reviewer on shift spot-checked a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. Noted and closed.

### Review entry 1008 — resolver (control plane) lane
The reconciliation desk filed a routine observation. The downstream vendor confirmed receipt inside the agreed window. Carried to the archive unchanged.
The reconciliation desk spot-checked a routine observation. The overnight window ran long behind an unrelated platform patch. The item was closed at the same meeting.

### Review entry 1009 — mirror (west) lane
The operations desk opened a query on a routine observation. One record appeared twice in the export after a mid-cycle correction. Left open overnight, then closed.
> **Governance decision (2026-03-05 - #REG-7109)** Rosa: deduplicate requests by (channel, package, source); on a specificity tie keep the lexicographically LARGER constraint string *(Revised — see the 2026-05 governance review.)*
The duty analyst spot-checked a routine observation. Late inputs arrived from one feed and were loaded before the cut. Recorded without further action.

### Review entry 1010 — quarantine (north) lane
A reviewer on shift recorded a routine observation. A query about a prior-period entry was answered from the published schedule. Closed against the standing runbook.
The audit lead reviewed a routine observation. The overnight window ran long behind an unrelated platform patch. Nothing was escalated.

### Review entry 1011 — channel-canary lane lane
The reconciliation desk raised and closed a routine observation. A batch retried once after a transient timeout and completed on the second pass. The thread was archived after review.
The audit lead carried forward a routine observation. Nightly reconciliation matched exactly and the file was released without comment. Closed with no parameter change.

### Review entry 1012 — registry-core (primary index) lane
A weekly review raised and closed a routine observation. One record appeared twice in the export after a mid-cycle correction.
> **Recovery draft proposal (2026-02-12 - #REG-7020)** Anders: yanked versions are NEVER selected by the resolver under any circumstance *(Superseded — reversed in the 2026-05 governance review.)*
The platform team signed off a routine observation. Nightly reconciliation matched exactly and the file was released without comment.

### Review entry 1013 — publish (edge worker) lane
An on-call engineer raised and closed a routine observation. The variance sat inside tolerance and no adjustment was raised.
A reviewer on shift opened a query on a routine observation. Nightly reconciliation matched exactly and the file was released without comment.

### Review entry 1014 — resolver (control plane) lane
An on-call engineer noted a routine observation. Nightly reconciliation matched exactly and the file was released without comment.
An on-call engineer logged a routine observation. One record appeared twice in the export after a mid-cycle correction.

### Review entry 1015 — mirror (west) lane
A stand-up note filed a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.
> **Recovery draft proposal (2026-02-13 - #REG-7022)** Rosa: pre-release versions (anything carrying a -rc/-beta/-alpha/-dev suffix) are never selected on any channel *(Superseded — reversed in the 2026-05 governance review.)*
The platform team raised and closed a routine observation. A typo in a reference record was corrected before the run started.

### Review entry 1016 — quarantine (north) lane
A shift handover reviewed a routine observation. A batch retried once after a transient timeout and completed on the second pass.
The audit lead recorded a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine.

### Review entry 1017 — channel-canary lane lane
The operations desk logged a routine observation. A typo in a reference record was corrected before the run started.
A stand-up note opened a query on a routine observation. The variance sat inside tolerance and no adjustment was raised.

### Review entry 1018 — registry-core (primary index) lane
An on-call engineer spot-checked a routine observation. Storage on the staging host was extended after the export outgrew its allocation.
> **Governance decision (2026-03-06 - #REG-7115)** Priya: resolution is per-package and independent: each package resolves ONCE to its highest satisfying version and there is no cross-dependency consistency ledger and no re-selection *(Revised — see the 2026-05 governance review.)*
A weekly review recorded a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.

### Review entry 1019 — publish (edge worker) lane
The duty analyst logged a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.
The reconciliation desk filed a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.

### Review entry 1020 — resolver (control plane) lane
The reconciliation desk carried forward a routine observation. The count sat a little above the running mean, entirely from estimated inputs.
A weekly review opened a query on a routine observation. A duplicate order was cancelled at source and never reached the run.

### Review entry 1021 — mirror (west) lane
A shift handover noted a routine observation. A batch retried once after a transient timeout and completed on the second pass.
> **Recovery draft proposal (2026-02-14 - #REG-7046)** Anders: the responder capacity cap is applied per package during admission, before any ordering *(Superseded — reversed in the 2026-05 governance review.)*
A reviewer on shift recorded a routine observation. One record appeared twice in the export after a mid-cycle correction.

### Review entry 1022 — quarantine (north) lane
The controls team filed a routine observation. A duplicate order was cancelled at source and never reached the run.
A stand-up note signed off a routine observation. The count sat a little above the running mean, entirely from estimated inputs.

### Review entry 1023 — channel-canary lane lane
The duty analyst reviewed a routine observation. The downstream vendor confirmed receipt inside the agreed window.
A weekly review reviewed a routine observation. Late inputs arrived from one feed and were loaded before the cut.

### Review entry 1024 — registry-core (primary index) lane
An on-call engineer raised and closed a routine observation. Storage on the staging host was extended after the export outgrew its allocation.
> **Governance decision (2026-03-08 - #REG-7048)** Yusuf: the max_* summary fields are maxima over EVERY resolved package, admitted to the plan or not *(Revised — see the 2026-05 governance review.)*
An on-call engineer carried forward a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. No change to the approved parameters resulted.

### Review entry 1025 — publish (edge worker) lane
A weekly review reviewed a routine observation. A typo in a reference record was corrected before the run started. Closed with no parameter change.
The controls team carried forward a routine observation. A question raised on the floor was withdrawn once the entry was reread.

### Review entry 1026 — resolver (control plane) lane
The exceptions queue owner carried forward a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. Nothing here bears on engine behaviour.
The audit lead reviewed a routine observation. One record appeared twice in the export after a mid-cycle correction. Logged for trend purposes only.

### Review entry 1027 — mirror (west) lane
The platform team reviewed a routine observation. The downstream vendor confirmed receipt inside the agreed window. Recorded without further action.
An on-call engineer raised and closed a routine observation. A batch retried once after a transient timeout and completed on the second pass. Closed against the standing runbook.

### Review entry 1028 — quarantine (north) lane
The reconciliation desk recorded a routine observation. A typo in a reference record was corrected before the run started. A second reviewer concurred.
> **Governance decision (2026-03-09 - #REG-7009)** Priya: registry-index recovery interim: the replay journal outranks the pre-migration snapshot wherever the two carry the same release, but a replayed release is appended to the END of its package's release list rather than taking the snapshot record's position, and a retraction applies only to versions the snapshot never held *(Revised — see the 2026-06 governance review.)*
A weekly review reviewed a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. Left open overnight, then closed.

### Review entry 1029 — channel-canary lane lane
The reconciliation desk signed off a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. Referred to the dated decisions and closed.
A weekly review opened a query on a routine observation. One record appeared twice in the export after a mid-cycle correction. Carried to the archive unchanged.

### Review entry 1030 — registry-core (primary index) lane
A reviewer on shift carried forward a routine observation. The variance sat inside tolerance and no adjustment was raised. No follow-up was requested.
The platform team signed off a routine observation. Late inputs arrived from one feed and were loaded before the cut. Filed alongside the cycle's other notes.

### Review entry 1031 — publish (edge worker) lane
A weekly review opened a query on a routine observation. A query about a prior-period entry was answered from the published schedule. Raised, discussed briefly, and dropped.
The operations desk noted a routine observation. Storage on the staging host was extended after the export outgrew its allocation. The thread was archived after review.

### Review entry 1032 — resolver (control plane) lane
The operations desk opened a query on a routine observation. One record appeared twice in the export after a mid-cycle correction. The desk confirmed no downstream impact.
The operations desk carried forward a routine observation. Late inputs arrived from one feed and were loaded before the cut. Filed for the record.

### Review entry 1033 — mirror (west) lane
The platform team recorded a routine observation. One record appeared twice in the export after a mid-cycle correction. The reviewer signed it off the same day.
A reviewer on shift signed off a routine observation. One record appeared twice in the export after a mid-cycle correction. Noted and closed.

### Review entry 1034 — quarantine (north) lane
An on-call engineer signed off a routine observation. A duplicate order was cancelled at source and never reached the run. No action was carried forward.
The platform team filed a routine observation. The overnight window ran long behind an unrelated platform patch. Nothing was escalated.

### Review entry 1035 — channel-canary lane lane
A shift handover carried forward a routine observation. A batch retried once after a transient timeout and completed on the second pass. The observation stood without amendment.
An on-call engineer recorded a routine observation. Storage on the staging host was extended after the export outgrew its allocation. The item was closed at the same meeting.

### Review entry 1036 — registry-core (primary index) lane
A weekly review reviewed a routine observation. The variance sat inside tolerance and no adjustment was raised. No dissent was recorded.
The controls team reviewed a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. The matter was not pursued.

### Review entry 1037 — publish (edge worker) lane
A stand-up note noted a routine observation. One record appeared twice in the export after a mid-cycle correction.
An on-call engineer reviewed a routine observation. A query about a prior-period entry was answered from the published schedule.

### Review entry 1038 — resolver (control plane) lane
A reviewer on shift noted a routine observation. A batch retried once after a transient timeout and completed on the second pass.
The exceptions queue owner carried forward a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.

### Review entry 1039 — mirror (west) lane
The exceptions queue owner recorded a routine observation. Storage on the staging host was extended after the export outgrew its allocation.
The audit lead opened a query on a routine observation. Storage on the staging host was extended after the export outgrew its allocation.

### Review entry 1040 — quarantine (north) lane
The audit lead noted a routine observation. The count sat a little above the running mean, entirely from estimated inputs.
A reviewer on shift logged a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.

### Review entry 1041 — channel-canary lane lane
A reviewer on shift reviewed a routine observation. Storage on the staging host was extended after the export outgrew its allocation.
A reviewer on shift noted a routine observation. A query about a prior-period entry was answered from the published schedule.

### Review entry 1042 — registry-core (primary index) lane
The exceptions queue owner opened a query on a routine observation. The downstream vendor confirmed receipt inside the agreed window.
A shift handover opened a query on a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.

### Review entry 1043 — publish (edge worker) lane
The reconciliation desk signed off a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine.
The audit lead recorded a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine.

### Review entry 1044 — resolver (control plane) lane
The operations desk noted a routine observation. A query about a prior-period entry was answered from the published schedule.
A weekly review logged a routine observation. The downstream vendor confirmed receipt inside the agreed window.

### Review entry 1045 — mirror (west) lane
A weekly review filed a routine observation. A question raised on the floor was withdrawn once the entry was reread.
A stand-up note noted a routine observation. A typo in a reference record was corrected before the run started.

### Review entry 1046 — quarantine (north) lane
The duty analyst signed off a routine observation. The variance sat inside tolerance and no adjustment was raised.
The duty analyst raised and closed a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.

### Review entry 1047 — channel-canary lane lane
A stand-up note opened a query on a routine observation. A query about a prior-period entry was answered from the published schedule.
The controls team carried forward a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine.

### Review entry 1048 — registry-core (primary index) lane
A shift handover noted a routine observation. An operator asked whether a credit had posted; it had, in the preceding period.
An on-call engineer noted a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine.

### Review entry 1049 — publish (edge worker) lane
The platform team carried forward a routine observation. Storage on the staging host was extended after the export outgrew its allocation.
The audit lead logged a routine observation. A typo in a reference record was corrected before the run started. Filed alongside the cycle's other notes.

### Review entry 1050 — resolver (control plane) lane
A shift handover noted a routine observation. The variance sat inside tolerance and no adjustment was raised. Left open overnight, then closed.
> **Governance decision (2026-05-02 - #REG-7101)** Yusuf: canonicalization: package, source and channel names via str(...).strip().lower() then separator normalization — underscores and dots collapse to single hyphens and repeated hyphens collapse (empty -> 'unknown'); note collapses internal whitespace; a constraint is whitespace-collapsed and an empty constraint or '*' means ANY; the yanked flag — booleans unchanged, strings true/1/yes => true, everything else => false; registry versions are parsed under #REG-7104; rows are KEPT even when a field looks odd
The platform team raised and closed a routine observation. The downstream vendor confirmed receipt inside the agreed window. The thread was archived after review.

### Review entry 1051 — mirror (west) lane
The exceptions queue owner spot-checked a routine observation. The downstream vendor confirmed receipt inside the agreed window. No action was carried forward.
A shift handover recorded a routine observation. Storage on the staging host was extended after the export outgrew its allocation. Nothing here bears on engine behaviour.

### Review entry 1052 — quarantine (north) lane
The controls team recorded a routine observation. The count sat a little above the running mean, entirely from estimated inputs. The desk confirmed no downstream impact.
The platform team opened a query on a routine observation. The variance sat inside tolerance and no adjustment was raised. Closed against the standing runbook.

### Review entry 1053 — channel-canary lane lane
A reviewer on shift noted a routine observation. One record appeared twice in the export after a mid-cycle correction. The reviewer signed it off the same day.
The exceptions queue owner carried forward a routine observation. Nightly reconciliation matched exactly and the file was released without comment. A second reviewer concurred.

### Review entry 1054 — registry-core (primary index) lane
The reconciliation desk logged a routine observation. The variance sat inside tolerance and no adjustment was raised. Closed with no parameter change.
> **Governance decision (2026-05-03 - #REG-7102)** Yusuf: deduplicate requests by (channel, package, source): keep the MOST SPECIFIC constraint, where specificity ranks == above ~= above >=/<= above >/< above any; the direction of the specificity tie-break is set by #REG-7142; then prefer the longer note; then first-seen input order. This supersedes #REG-7109 on structure
The audit lead opened a query on a routine observation. A typo in a reference record was corrected before the run started. No change to the approved parameters resulted.

### Review entry 1055 — publish (edge worker) lane
An on-call engineer noted a routine observation. Nightly reconciliation matched exactly and the file was released without comment. Noted and closed.
An on-call engineer reviewed a routine observation. The downstream vendor confirmed receipt inside the agreed window.

### Review entry 1056 — resolver (control plane) lane
A weekly review raised and closed a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. The matter was not pursued.
A stand-up note reviewed a routine observation. A query about a prior-period entry was answered from the published schedule. The observation stood without amendment.

### Review entry 1057 — mirror (west) lane
A stand-up note noted a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. Referred to the dated decisions and closed.
> **Governance decision (2026-05-14 - #REG-7142)** Yusuf: duplicate tie-break direction is REVERSED: where two requests share (channel, package, source) and tie on constraint specificity, keep the LEXICOGRAPHICALLY SMALLER constraint string (reversed from the #REG-7109 draft). Only this comparison changes; the rest of the #REG-7102 chain runs unchanged after it
A reviewer on shift filed a routine observation. An operator asked whether a credit had posted; it had, in the preceding period. Nothing was escalated.

### Review entry 1058 — quarantine (north) lane
A stand-up note filed a routine observation. Nightly reconciliation matched exactly and the file was released without comment. The item was closed at the same meeting.
The duty analyst spot-checked a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. Filed for the record.

### Review entry 1059 — channel-canary lane lane
A reviewer on shift opened a query on a routine observation. Late inputs arrived from one feed and were loaded before the cut. Recorded without further action.
The operations desk reviewed a routine observation. Storage on the staging host was extended after the export outgrew its allocation. Logged for trend purposes only.

### Review entry 1060 — registry-core (primary index) lane
A shift handover signed off a routine observation. A typo in a reference record was corrected before the run started. Carried to the archive unchanged.
An on-call engineer raised and closed a routine observation. The count sat a little above the running mean, entirely from estimated inputs. Raised, discussed briefly, and dropped.

### Review entry 1061 — publish (edge worker) lane
A stand-up note noted a routine observation. A duplicate order was cancelled at source and never reached the run. No follow-up was requested.
A stand-up note carried forward a routine observation. A typo in a reference record was corrected before the run started. No dissent was recorded.

### Review entry 1062 — resolver (control plane) lane
The audit lead raised and closed a routine observation. Late inputs arrived from one feed and were loaded before the cut.
A weekly review noted a routine observation. Late inputs arrived from one feed and were loaded before the cut.

### Review entry 1063 — mirror (west) lane
The operations desk filed a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.
A shift handover noted a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine.

### Review entry 1064 — quarantine (north) lane
A shift handover logged a routine observation. The count sat a little above the running mean, entirely from estimated inputs.
> **Governance decision (2026-05-04 - #REG-7104)** Lena: version precedence (deviates from semver): order by (major, minor, patch), then pre-release maturity rank where dev < alpha < beta < rc < ga and ga denotes a final release (no pre-release suffix), then the pre-release number, then BUILD METADATA (the integer in a +N suffix) as the FINAL tiebreaker — build metadata IS precedence-significant here, unlike semver which ignores it entirely, so 1.0.0+build7 outranks 1.0.0+build3 outranks 1.0.0. This supersedes #REG-7004
The operations desk filed a routine observation. Nightly reconciliation matched exactly and the file was released without comment.

### Review entry 1065 — channel-canary lane lane
A shift handover recorded a routine observation. Storage on the staging host was extended after the export outgrew its allocation.
The exceptions queue owner carried forward a routine observation. The downstream vendor confirmed receipt inside the agreed window.

### Review entry 1066 — registry-core (primary index) lane
A reviewer on shift logged a routine observation. A typo in a reference record was corrected before the run started.
The controls team spot-checked a routine observation. One record appeared twice in the export after a mid-cycle correction.

### Review entry 1067 — publish (edge worker) lane
The operations desk signed off a routine observation. An operator asked whether a credit had posted; it had, in the preceding period.
The audit lead noted a routine observation. Late inputs arrived from one feed and were loaded before the cut.

### Review entry 1068 — resolver (control plane) lane
The audit lead spot-checked a routine observation. An operator asked whether a credit had posted; it had, in the preceding period.
The operations desk noted a routine observation. Storage on the staging host was extended after the export outgrew its allocation.

### Review entry 1069 — mirror (west) lane
A weekly review spot-checked a routine observation. A question raised on the floor was withdrawn once the entry was reread.
> **Governance decision (2026-05-05 - #REG-7106)** Marek: constraint satisfaction: operators ==, >=, >, <=, < compare full governance version keys; '~=X.Y' is the compatible-release band >=X.Y.0,<(X+1).0.0 and '~=X.Y.Z' is >=X.Y.Z,<X.(Y+1).0; a comma joins clauses with AND; '' or '*' is ANY; a bare version is an exact ==. A candidate's FULL key (pre-release rank and build included) is compared against the boundary parsed the same way, so 1.2.0-rc1 does NOT satisfy >=1.2.0
The operations desk signed off a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.

### Review entry 1070 — quarantine (north) lane
An on-call engineer carried forward a routine observation. Late inputs arrived from one feed and were loaded before the cut.
A reviewer on shift raised and closed a routine observation. The downstream vendor confirmed receipt inside the agreed window.

### Review entry 1071 — channel-canary lane lane
The duty analyst raised and closed a routine observation. The downstream vendor confirmed receipt inside the agreed window.
The audit lead noted a routine observation. Storage on the staging host was extended after the export outgrew its allocation.

### Review entry 1072 — registry-core (primary index) lane
A weekly review recorded a routine observation. A typo in a reference record was corrected before the run started.
> **Governance decision (2026-05-06 - #REG-7108)** Lena: selection direction (deviates from pip/semver): the default conflict-resolution strategy chooses the LOWEST satisfying version (conservative minimum-viable resolution), NOT the highest; only packages named in the policy's selection_overrides list take the HIGHEST satisfying version instead. This supersedes #REG-7008
The audit lead signed off a routine observation. The variance sat inside tolerance and no adjustment was raised.

### Review entry 1073 — publish (edge worker) lane
The exceptions queue owner raised and closed a routine observation. The count sat a little above the running mean, entirely from estimated inputs.
The controls team reviewed a routine observation. One record appeared twice in the export after a mid-cycle correction.

### Review entry 1074 — resolver (control plane) lane
A stand-up note raised and closed a routine observation. Late inputs arrived from one feed and were loaded before the cut.
A reviewer on shift spot-checked a routine observation. The downstream vendor confirmed receipt inside the agreed window. Referred to the dated decisions and closed.

### Review entry 1075 — mirror (west) lane
A stand-up note filed a routine observation. The overnight window ran long behind an unrelated platform patch. Noted and closed.
A weekly review noted a routine observation. Late inputs arrived from one feed and were loaded before the cut. Filed alongside the cycle's other notes.

### Review entry 1076 — quarantine (north) lane
The reconciliation desk raised and closed a routine observation. The variance sat inside tolerance and no adjustment was raised. No change to the approved parameters resulted.
> **Governance decision (2026-05-06 - #REG-7110)** Priya: pin override: a version named in the policy's pins for the request's channel (or under the '*' global scope) is chosen ABSOLUTELY — regardless of constraints, yanked state or pre-release state — with status 'pinned'; a pin whose version is absent from the registry is a 'conflict' (pin-missing). Pins take precedence over #REG-7108, #REG-7120 and #REG-7122
The platform team carried forward a routine observation. A duplicate order was cancelled at source and never reached the run. No follow-up was requested.

### Review entry 1077 — channel-canary lane lane
The operations desk spot-checked a routine observation. The count sat a little above the running mean, entirely from estimated inputs. Nothing was escalated.
A reviewer on shift noted a routine observation. A batch retried once after a transient timeout and completed on the second pass. Closed against the standing runbook.

### Review entry 1078 — registry-core (primary index) lane
The controls team logged a routine observation. Late inputs arrived from one feed and were loaded before the cut. The thread was archived after review.
The controls team noted a routine observation. The count sat a little above the running mean, entirely from estimated inputs. Closed with no parameter change.

### Review entry 1079 — publish (edge worker) lane
The audit lead filed a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. The observation stood without amendment.
> **Governance decision (2026-05-07 - #REG-7120)** Lena: yanked exemption: a yanked version is excluded from the candidate set UNLESS its package is named in the policy's yanked_exemptions list, in which case yanked builds are eligible like any other version. This supersedes #REG-7020
A weekly review logged a routine observation. A batch retried once after a transient timeout and completed on the second pass. Filed for the record.

### Review entry 1080 — resolver (control plane) lane
The controls team noted a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. No dissent was recorded.
The duty analyst carried forward a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. The reviewer signed it off the same day.

### Review entry 1081 — mirror (west) lane
The exceptions queue owner noted a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. Recorded without further action.
A shift handover raised and closed a routine observation. A question raised on the floor was withdrawn once the entry was reread. A second reviewer concurred.

### Review entry 1082 — quarantine (north) lane
An on-call engineer logged a routine observation. Storage on the staging host was extended after the export outgrew its allocation. Raised, discussed briefly, and dropped.
The duty analyst noted a routine observation. A typo in a reference record was corrected before the run started. Logged for trend purposes only.

### Review entry 1083 — channel-canary lane lane
The platform team filed a routine observation. The overnight window ran long behind an unrelated platform patch. Left open overnight, then closed.
> **Governance decision (2026-05-08 - #REG-7122)** Priya: pre-release admission: a pre-release candidate (maturity rank below ga) is admitted only when BOTH the channel's channel_priorities.allow_prerelease is true AND the candidate's maturity rank is >= the resolved prerelease_rank_floor for that package; otherwise it is excluded from candidates (a pin naming a pre-release still wins per #REG-7110). This supersedes #REG-7022
The controls team reviewed a routine observation. A batch retried once after a transient timeout and completed on the second pass. The matter was not pursued.

### Review entry 1084 — registry-core (primary index) lane
A shift handover logged a routine observation. An operator asked whether a credit had posted; it had, in the preceding period. The desk confirmed no downstream impact.
The reconciliation desk reviewed a routine observation. A query about a prior-period entry was answered from the published schedule. Nothing here bears on engine behaviour.

### Review entry 1085 — publish (edge worker) lane
The duty analyst opened a query on a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.
A shift handover logged a routine observation. A question raised on the floor was withdrawn once the entry was reread. No action was carried forward.

### Review entry 1086 — resolver (control plane) lane
The platform team reviewed a routine observation. A question raised on the floor was withdrawn once the entry was reread. Carried to the archive unchanged.
> **Governance decision (2026-05-10 - #REG-7116)** Yusuf: resolution ledger: resolution is a per-channel MONOTONE fixpoint. Constraints only ACCUMULATE as chosen versions pull in their dependencies (a re-selected version's earlier dependency constraints persist). The per-channel ledger keeps a package's FIRST chosen version for consistency across repeated sub-dependencies and only RE-SELECTS — incrementing reselect_count — when the held version stops satisfying the tightened constraint set. This supersedes #REG-7115 on structure; the re-selection cap is set by #REG-7160
The reconciliation desk signed off a routine observation. A question raised on the floor was withdrawn once the entry was reread. The item was closed at the same meeting.

### Review entry 1087 — mirror (west) lane
The reconciliation desk filed a routine observation. The overnight window ran long behind an unrelated platform patch.
A reviewer on shift logged a routine observation. The variance sat inside tolerance and no adjustment was raised.

### Review entry 1088 — quarantine (north) lane
The platform team spot-checked a routine observation. Storage on the staging host was extended after the export outgrew its allocation.
The reconciliation desk reviewed a routine observation. Nightly reconciliation matched exactly and the file was released without comment.

### Review entry 1089 — channel-canary lane lane
The operations desk filed a routine observation. A batch retried once after a transient timeout and completed on the second pass.
The platform team logged a routine observation. A question raised on the floor was withdrawn once the entry was reread.

### Review entry 1090 — registry-core (primary index) lane
A stand-up note opened a query on a routine observation. The overnight window ran long behind an unrelated platform patch.
> **Governance decision (2026-05-28 - #REG-7160)** Yusuf: re-selection cap, final: when a package would have to re-select beyond its resolved reselect_cap it FREEZES into a 'conflict' (provenance reselect-cap-exceeded) instead of re-resolving further; a re-selection at or below the cap is accepted and its new dependencies enqueued. Freezing refuses the re-selection rather than taking it: the package KEEPS the version it was holding, and unlike the pin-missing and unsatisfiable conflicts — which never chose anything and so report no version — a frozen entry reports that held version as its chosen_version. Only the version is held: every other field the entry carries is still read off #REG-7156 against the constraints as they finally stand, so its dep_edges are the held release's, its satisfied_constraints are everything that accumulated against the package in that channel, and its alternatives_considered are the candidates admissible at the end other than the version it held. Its reselect_count is the re-selection that was refused, so it reads one beyond the cap
A stand-up note noted a routine observation. Nightly reconciliation matched exactly and the file was released without comment.

### Review entry 1091 — publish (edge worker) lane
The controls team spot-checked a routine observation. A duplicate order was cancelled at source and never reached the run.
The platform team recorded a routine observation. A typo in a reference record was corrected before the run started.

### Review entry 1092 — resolver (control plane) lane
The reconciliation desk filed a routine observation. An operator asked whether a credit had posted; it had, in the preceding period.
The reconciliation desk carried forward a routine observation. The variance sat inside tolerance and no adjustment was raised.

### Review entry 1093 — mirror (west) lane
The operations desk carried forward a routine observation. The count sat a little above the running mean, entirely from estimated inputs.
The platform team raised and closed a routine observation. Storage on the staging host was extended after the export outgrew its allocation.

### Review entry 1094 — quarantine (north) lane
A reviewer on shift spot-checked a routine observation. One record appeared twice in the export after a mid-cycle correction.
The platform team carried forward a routine observation. Late inputs arrived from one feed and were loaded before the cut.

### Review entry 1095 — channel-canary lane lane
The controls team logged a routine observation. An operator asked whether a credit had posted; it had, in the preceding period.
A stand-up note raised and closed a routine observation. An operator asked whether a credit had posted; it had, in the preceding period.

### Review entry 1096 — registry-core (primary index) lane
The exceptions queue owner signed off a routine observation. Late inputs arrived from one feed and were loaded before the cut.
> **Governance decision (2026-05-12 - #REG-7156)** Marek: resolution entry reporting, final. Status is `resolved` for a normal selection, `pinned` for a #REG-7110 pin, and `conflict` for every failure. Each entry also records the provenance label that settled it: a selection taken in the #REG-7108 default direction is `default-selection`; one taken because the package is named in the policy's selection_overrides list is `override-selection`; a pin is `pin-override` and a pin whose version is absent from the index is `pin-missing`; a package with no admissible candidate is `unsatisfiable`; a package frozen by #REG-7160 is `reselect-cap-exceeded`. The entry's reason repeats its provenance label verbatim, prefixed with `yanked-admitted;` (no space) when a default- or override-selection settled on a yanked build; the pin and failure labels are never prefixed. A plan row repeats its entry's reason, except that a row placed by the #REG-7148 cycle rule carries `cycle-break` instead. dep_edges are the normalized dependency package names of the chosen release, de-duplicated and sorted ascending, and dep_count is their number; satisfied_constraints are the distinct constraint texts that accumulated against that package in that channel, sorted ascending; alternatives_considered are the admissible candidate versions other than the chosen one, sorted ascending by the #REG-7104 precedence key and then truncated to that package's resolved alt_report_cap, with alternatives_count their number -- where an entry chose nothing there is nothing to exclude and every admissible candidate is reported, so a pin-missing conflict carries the candidates its constraints admitted while an unsatisfiable one, having none, carries no alternative at all; is_prerelease and used_yanked describe the chosen release; and cyclic_packages names each cycle-broken install in the #REG-7145/#REG-7148 ordering — including any row the #REG-7146 cap later defers — as `channel/package`, sorted ascending, with cyclic_package_count their number
The platform team noted a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine.

### Review entry 1097 — publish (edge worker) lane
The controls team reviewed a routine observation. The count sat a little above the running mean, entirely from estimated inputs.
> **Governance decision (2026-05-08 - #REG-7145)** Priya: install order: build the dependency graph among the resolved packages of a channel and order DEPENDENCIES BEFORE DEPENDENTS; among packages whose dependencies are all already placed, the tie-break is the lexicographically smallest package name; channels are ordered ascending
An on-call engineer noted a routine observation. Storage on the staging host was extended after the export outgrew its allocation.

### Review entry 1098 — resolver (control plane) lane
The duty analyst filed a routine observation. The count sat a little above the running mean, entirely from estimated inputs.
The controls team noted a routine observation. A duplicate order was cancelled at source and never reached the run.

### Review entry 1099 — mirror (west) lane
A reviewer on shift logged a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine.
The duty analyst logged a routine observation. Nightly reconciliation matched exactly and the file was released without comment. Filed for the record.

### Review entry 1100 — quarantine (north) lane
The reconciliation desk reviewed a routine observation. The count sat a little above the running mean, entirely from estimated inputs. Left open overnight, then closed.
> **Governance decision (2026-05-16 - #REG-7148)** Marek: cycle handling: dependency cycles are NON-FATAL — when no remaining package is installable, install the lexicographically smallest remaining package, FLAG it cyclic, and continue; cyclic packages are reported in the summary but still installed
The operations desk spot-checked a routine observation. The variance sat inside tolerance and no adjustment was raised. The reviewer signed it off the same day.

### Review entry 1101 — channel-canary lane lane
An on-call engineer signed off a routine observation. The variance sat inside tolerance and no adjustment was raised. Carried to the archive unchanged.
A weekly review raised and closed a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. No change to the approved parameters resulted.

### Review entry 1102 — registry-core (primary index) lane
The platform team carried forward a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. The matter was not pursued.
The controls team filed a routine observation. An operator asked whether a credit had posted; it had, in the preceding period. Referred to the dated decisions and closed.

### Review entry 1103 — publish (edge worker) lane
The platform team carried forward a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. No dissent was recorded.
The platform team noted a routine observation. One record appeared twice in the export after a mid-cycle correction. Noted and closed.

### Review entry 1104 — resolver (control plane) lane
The audit lead reviewed a routine observation. A typo in a reference record was corrected before the run started. No follow-up was requested.
> **Governance decision (2026-05-24 - #REG-7146)** Marek: capacity cap: at most plan_capacity_cap install rows per channel. The cap is a FINAL pass over the fully ordered plan — not applied during resolution and not per package before ordering: order everything per #REG-7145 and #REG-7148, then walk each channel keeping only its first plan_capacity_cap rows; deferred rows contribute to no plan-derived summary field. This supersedes #REG-7046
The controls team raised and closed a routine observation. Storage on the staging host was extended after the export outgrew its allocation. The item was closed at the same meeting.

### Review entry 1105 — mirror (west) lane
A reviewer on shift opened a query on a routine observation. Late inputs arrived from one feed and were loaded before the cut. The desk confirmed no downstream impact.
The platform team filed a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. Recorded without further action.

### Review entry 1106 — quarantine (north) lane
The operations desk raised and closed a routine observation. A batch retried once after a transient timeout and completed on the second pass.
A reviewer on shift logged a routine observation. Nightly reconciliation matched exactly and the file was released without comment. Closed with no parameter change.

### Review entry 1107 — channel-canary lane lane
The exceptions queue owner reviewed a routine observation. Storage on the staging host was extended after the export outgrew its allocation. The observation stood without amendment.
> **Governance decision (2026-05-10 - #REG-7154)** Yusuf: summary aggregation (final, revising #REG-7048): max_reselect_count, max_dep_count and max_alternatives_count are maxima over the FINAL capped install_plan rows only (0 when the plan is empty); total_reselects and total_alternatives_considered sum over EVERY resolution entry; total_conflict_weight = conflict_count times the resolved default conflict_weight
> **Governance decision (2026-05-10 - #REG-7155)** Yusuf: summary request and channel counters, final. `raw_request_count` is the number of rows the selected request file holds, counted before any coercion. `unique_request_ids` is the number of DISTINCT request_id values across those same raw rows, the id collapsed under the #REG-7101 note coercion. `canonical_request_count` is the number of requests left AFTER the #REG-7102/#REG-7142 duplicate keep, so a request set holding no duplicate (channel, package, source) reports it equal to raw_request_count. `channel_count` is the number of DISTINCT canonical channels those surviving requests name, not the number of channels the policy configures.
A weekly review signed off a routine observation. The downstream vendor confirmed receipt inside the agreed window. Nothing was escalated.

### Review entry 1108 — registry-core (primary index) lane
A weekly review raised and closed a routine observation. One record appeared twice in the export after a mid-cycle correction. Nothing here bears on engine behaviour.
The exceptions queue owner reviewed a routine observation. Late inputs arrived from one feed and were loaded before the cut. No action was carried forward.

### Review entry 1109 — publish (edge worker) lane
The duty analyst reviewed a routine observation. An operator asked whether a credit had posted; it had, in the preceding period. The thread was archived after review.
The controls team logged a routine observation. Storage on the staging host was extended after the export outgrew its allocation. Raised, discussed briefly, and dropped.

### Review entry 1110 — resolver (control plane) lane
The audit lead logged a routine observation. Storage on the staging host was extended after the export outgrew its allocation. Filed alongside the cycle's other notes.
The duty analyst signed off a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. Closed against the standing runbook.

### Review entry 1111 — mirror (west) lane
The platform team opened a query on a routine observation. A query about a prior-period entry was answered from the published schedule. A second reviewer concurred.
A reviewer on shift filed a routine observation. The count sat a little above the running mean, entirely from estimated inputs. Logged for trend purposes only.

### Review entry 1112 — quarantine (north) lane
The operations desk signed off a routine observation. A typo in a reference record was corrected before the run started.
The operations desk raised and closed a routine observation. A question raised on the floor was withdrawn once the entry was reread.

### Review entry 1113 — channel-canary lane lane
The controls team signed off a routine observation. Late inputs arrived from one feed and were loaded before the cut.
The reconciliation desk filed a routine observation. A question raised on the floor was withdrawn once the entry was reread.

### Review entry 1114 — registry-core (primary index) lane
The reconciliation desk signed off a routine observation. The downstream vendor confirmed receipt inside the agreed window.
A stand-up note noted a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.

### Review entry 1115 — publish (edge worker) lane
The exceptions queue owner raised and closed a routine observation. The overnight window ran long behind an unrelated platform patch.
The controls team filed a routine observation. A query about a prior-period entry was answered from the published schedule.

### Review entry 1116 — resolver (control plane) lane
A shift handover opened a query on a routine observation. The overnight window ran long behind an unrelated platform patch.
> **Governance decision (2026-06-02 - #REG-7170)** Lena: authoritative registry-index recovery, final — this supersedes the #REG-7002 draft and revises the #REG-7009 interim, and it runs BEFORE any resolve. The migration truncated `/app/data/registry_index.json`, so that file is no longer authoritative and must be rebuilt in place from the two surviving sources beside it. Begin with every package of `/app/data/registry_snapshot_pre_migration.json`, keeping the snapshot's package order and each package's release order. Then apply `/app/data/registry_replay_journal.json` in ascending journal_seq order, one entry at a time. An entry whose journal_op is `append` carries a release published after the snapshot: if that package's list already holds a record with the same version string the entry OVERWRITES the FIRST such record IN PLACE, keeping that record's existing position (it is NOT moved to the end, revising #REG-7009); otherwise the release is appended to the END of that package's list, and a package the snapshot never held is added as a new key at the end of the index. An entry whose journal_op is `retract` removes EVERY record of that package carrying that version string, whether it came from the snapshot or from an earlier journal entry (also revising #REG-7009), and contributes no record of its own. The journal always wins on overlap; the snapshot never overrides it. journal_seq, journal_op, package and reason are journal bookkeeping, not release fields: a recovered release record carries exactly version, yanked and deps, with the journal's values for a replayed release. Write the result back to `/app/data/registry_index.json` as a JSON object of package to release list in exactly the order described. A stale record left uncorrected or a retracted release left in place changes which version #REG-7108 selects, so an index rebuilt any other way yields a wrong install plan
An on-call engineer spot-checked a routine observation. A question raised on the floor was withdrawn once the entry was reread.

### Review entry 1117 — mirror (west) lane
The duty analyst spot-checked a routine observation. The overnight window ran long behind an unrelated platform patch.
The audit lead noted a routine observation. A duplicate order was cancelled at source and never reached the run.

### Review entry 1118 — quarantine (north) lane
A weekly review spot-checked a routine observation. One record appeared twice in the export after a mid-cycle correction.
> **Governance decision (2026-05-18 - #REG-7150)** Priya: policy baseline (read from /app/data/resolution_policy.json at that fixed absolute path; --input never relocates it). Any field the policy file omits keeps its baseline: reselect_cap = 2; prerelease_rank_floor = 3; plan_capacity_cap = 3; conflict_weight = 5; alt_report_cap = 4
The audit lead signed off a routine observation. Late inputs arrived from one feed and were loaded before the cut.

### Review entry 1119 — channel-canary lane lane
An on-call engineer reviewed a routine observation. One record appeared twice in the export after a mid-cycle correction.
The reconciliation desk opened a query on a routine observation. A question raised on the floor was withdrawn once the entry was reread.

### Review entry 1120 — registry-core (primary index) lane
A stand-up note raised and closed a routine observation. A typo in a reference record was corrected before the run started.
A shift handover logged a routine observation. A duplicate order was cancelled at source and never reached the run.

### Review entry 1121 — publish (edge worker) lane
The controls team reviewed a routine observation. A question raised on the floor was withdrawn once the entry was reread.
> **Governance decision (2026-05-18 - #REG-7152)** Priya: policy resolution, per package in three layers: start from the #REG-7150 baseline; overlay every field the policy file's `default` object supplies (it need not be complete); then overlay every field that package's entry in `package_overrides` supplies (an override names only the fields it changes). Coerce every value to int. plan_capacity_cap and conflict_weight are taken from the resolved default
The duty analyst signed off a routine observation. A duplicate order was cancelled at source and never reached the run.

### Review entry 1122 — resolver (control plane) lane
The exceptions queue owner spot-checked a routine observation. The downstream vendor confirmed receipt inside the agreed window.
The audit lead signed off a routine observation. A query about a prior-period entry was answered from the published schedule.

### Review entry 1123 — mirror (west) lane
A reviewer on shift carried forward a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine.
The duty analyst noted a routine observation. An operator asked whether a credit had posted; it had, in the preceding period.

### Review entry 1124 — quarantine (north) lane
> **Governance decision (2026-06-06 - #REG-7174)** Yusuf: install-plan membership, final. What a channel ORDERS is exactly the entries whose status is `resolved` or `pinned`. Membership in that set is decided by STATUS alone and never by whether an entry reports a chosen_version. A #REG-7160 frozen entry is the case this settles: the cap refused its re-selection, so although it still reports the version it was holding, the channel does not install it. It never enters the #REG-7145/#REG-7148 ordering, so it takes no install row and no place in the #REG-7172 reach graph, and a dependency satisfied only by it is an edge into a package the ordering never places and adds nothing to any other package's reach_count. Its own reach_count is 0, as it is for every entry outside the ordering, including the pin-missing and unsatisfiable conflicts that never chose a version at all. Order membership and the install plan are separate questions: the #REG-7146 capacity cap runs afterwards over the ordered rows, so a `resolved` entry that did enter the ordering can still be deferred and take no plan row

> **Governance decision (2026-06-04 - #REG-7172)** Lena: dependency reach reporting, final. Every resolution entry and every install row also carries `reach_count`: the number of DISTINCT packages reachable from that package by following dependency edges among the channel's own resolved packages, counting only edges into a package the #REG-7145/#REG-7148 install order places EARLIER than it, and excluding the package itself. The install order is a total order, so a cycle-broken edge never contributes. The summary carries `max_reach_count` over all resolution entries. Reach is a property of the resolved set, not of a single release: the same package resolved in two channels may report different counts. This settles the #REG-7112 draft, which counted only direct dependencies

A shift handover noted a routine observation. Nightly reconciliation matched exactly and the file was released without comment.
A shift handover noted a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. The item was closed at the same meeting.

