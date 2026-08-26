# Package Registry Resolution Reconciler — Governance Review Log
Registry governance archive for the failed registry-migration rollout (2026-Q1 through 2026-Q2).

## Executive Summary
How the resolution reconciler is *meant* to behave — the recovery of a truncated registry index, canonicalization, request deduplication, the version precedence, constraint satisfaction, the conflict/selection strategy, pin overrides, the yanked and pre-release admission rules, the per-channel resolution ledger, cycle handling, install ordering and the capacity cap — was settled incrementally by the registry governance board, and those decisions live in the review entries below, not in any single summary. Several stages deliberately DEVIATE from standard semver / pip resolution: version precedence treats build metadata as significant, the default conflict strategy picks the LOWEST satisfying version, yanked and pre-release builds are gated by governance exemptions, and dependency cycles are non-fatal — so importing a semver/pip resolver and delegating to it produces wrong answers. The February draft proposals were revisited during the 2026-05 governance review and several were reversed, and the index-recovery entries were revisited again in 2026-06; where a draft or interim conflicts with a later decision, the later dated decision governs. `/app/docs/report_spec.json` is the output contract only.

## Governance Review Archive
Routine entries are context only. #REG-ticketed proposal and decision quotes are the authoritative record for reconciler behaviour.

### Review entry 1000 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1000. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1001 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1001. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1002 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1002. Synthetic package injection verified alert delivery to the on-call rotation for this region.
> **Recovery draft proposal (2026-02-06 - #REG-7004)** Anders: version precedence is standard semver: compare (major, minor, patch) then the pre-release identifiers, and build metadata (the +N suffix) is IGNORED for ordering, exactly like semver *(Superseded — reversed in the 2026-05 governance review.)*
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1003 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1003. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1004 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1004. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1005 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1005. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1006 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1006. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
> **Recovery draft proposal (2026-02-08 - #REG-7008)** Rosa: conflict resolution selects the HIGHEST satisfying version of each package, matching pip's default resolver *(Superseded — reversed in the 2026-05 governance review.)*
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1007 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1007. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
> **Recovery draft proposal (2026-02-05 - #REG-7002)** Anders: should the migration ever truncate the registry index, rebuild it by concatenating the pre-migration snapshot and the replay journal package by package and let the #REG-7104 precedence sort settle whatever overlaps; journal bookkeeping fields are inert and may stay on the release records *(Superseded — reversed in the 2026-06 governance review.)*
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1008 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1008. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1009 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1009. Vendor ticket on mirror retries closed; delivery within contractual budget.
> **Governance decision (2026-03-05 - #REG-7109)** Rosa: deduplicate requests by (channel, package, source); on a specificity tie keep the lexicographically LARGER constraint string *(Revised — see the 2026-05 governance review.)*
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1010 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1010. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1011 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1011. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1012 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1012. Synthetic package injection verified alert delivery to the on-call rotation for this region.
> **Recovery draft proposal (2026-02-12 - #REG-7020)** Anders: yanked versions are NEVER selected by the resolver under any circumstance *(Superseded — reversed in the 2026-05 governance review.)*
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1013 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1013. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1014 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1014. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1015 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1015. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
> **Recovery draft proposal (2026-02-13 - #REG-7022)** Rosa: pre-release versions (anything carrying a -rc/-beta/-alpha/-dev suffix) are never selected on any channel *(Superseded — reversed in the 2026-05 governance review.)*
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1016 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1016. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1017 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1017. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1018 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1018. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
> **Governance decision (2026-03-06 - #REG-7115)** Priya: resolution is per-package and independent: each package resolves ONCE to its highest satisfying version and there is no cross-dependency consistency ledger and no re-selection *(Revised — see the 2026-05 governance review.)*
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1019 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1019. Vendor ticket on mirror retries closed; delivery within contractual budget.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1020 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1020. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1021 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1021. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
> **Recovery draft proposal (2026-02-14 - #REG-7046)** Anders: the responder capacity cap is applied per package during admission, before any ordering *(Superseded — reversed in the 2026-05 governance review.)*
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1022 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1022. Synthetic package injection verified alert delivery to the on-call rotation for this region.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1023 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1023. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1024 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1024. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
> **Governance decision (2026-03-08 - #REG-7048)** Yusuf: the max_* summary fields are maxima over EVERY resolved package, admitted to the plan or not *(Revised — see the 2026-05 governance review.)*
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1025 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1025. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1026 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1026. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1027 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1027. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1028 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1028. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
> **Governance decision (2026-03-09 - #REG-7009)** Priya: registry-index recovery interim: the replay journal outranks the pre-migration snapshot wherever the two carry the same release, but a replayed release is appended to the END of its package's release list rather than taking the snapshot record's position, and a retraction applies only to versions the snapshot never held *(Revised — see the 2026-06 governance review.)*
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1029 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1029. Vendor ticket on mirror retries closed; delivery within contractual budget.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1030 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1030. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1031 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1031. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1032 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1032. Synthetic package injection verified alert delivery to the on-call rotation for this region.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1033 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1033. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1034 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1034. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1035 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1035. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1036 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1036. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1037 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1037. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1038 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1038. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1039 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1039. Vendor ticket on mirror retries closed; delivery within contractual budget.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1040 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1040. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1041 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1041. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1042 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1042. Synthetic package injection verified alert delivery to the on-call rotation for this region.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1043 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1043. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1044 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1044. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1045 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1045. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1046 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1046. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1047 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1047. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1048 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1048. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1049 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1049. Vendor ticket on mirror retries closed; delivery within contractual budget.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1050 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1050. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
> **Governance decision (2026-05-02 - #REG-7101)** Yusuf: canonicalization: package, source and channel names via str(...).strip().lower() then separator normalization — underscores and dots collapse to single hyphens and repeated hyphens collapse (empty -> 'unknown'); note collapses internal whitespace; a constraint is whitespace-collapsed and an empty constraint or '*' means ANY; the yanked flag — booleans unchanged, strings true/1/yes => true, everything else => false; registry versions are parsed under #REG-7104; rows are KEPT even when a field looks odd
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1051 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1051. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1052 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1052. Synthetic package injection verified alert delivery to the on-call rotation for this region.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1053 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1053. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1054 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1054. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
> **Governance decision (2026-05-03 - #REG-7102)** Yusuf: deduplicate requests by (channel, package, source): keep the MOST SPECIFIC constraint, where specificity ranks == above ~= above >=/<= above >/< above any; the direction of the specificity tie-break is set by #REG-7142; then prefer the longer note; then first-seen input order. This supersedes #REG-7109 on structure
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1055 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1055. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1056 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1056. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1057 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1057. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
> **Governance decision (2026-05-14 - #REG-7142)** Yusuf: duplicate tie-break direction is REVERSED: where two requests share (channel, package, source) and tie on constraint specificity, keep the LEXICOGRAPHICALLY SMALLER constraint string (reversed from the #REG-7109 draft). Only this comparison changes; the rest of the #REG-7102 chain runs unchanged after it
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1058 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1058. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1059 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1059. Vendor ticket on mirror retries closed; delivery within contractual budget.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1060 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1060. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1061 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1061. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1062 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1062. Synthetic package injection verified alert delivery to the on-call rotation for this region.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1063 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1063. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1064 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1064. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
> **Governance decision (2026-05-04 - #REG-7104)** Lena: version precedence (deviates from semver): order by (major, minor, patch), then pre-release maturity rank where dev < alpha < beta < rc < ga and ga denotes a final release (no pre-release suffix), then the pre-release number, then BUILD METADATA (the integer in a +N suffix) as the FINAL tiebreaker — build metadata IS precedence-significant here, unlike semver which ignores it entirely, so 1.0.0+build7 outranks 1.0.0+build3 outranks 1.0.0. This supersedes #REG-7004
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1065 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1065. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1066 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1066. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1067 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1067. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1068 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1068. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1069 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1069. Vendor ticket on mirror retries closed; delivery within contractual budget.
> **Governance decision (2026-05-05 - #REG-7106)** Marek: constraint satisfaction: operators ==, >=, >, <=, < compare full governance version keys; '~=X.Y' is the compatible-release band >=X.Y.0,<(X+1).0.0 and '~=X.Y.Z' is >=X.Y.Z,<X.(Y+1).0; a comma joins clauses with AND; '' or '*' is ANY; a bare version is an exact ==. A candidate's FULL key (pre-release rank and build included) is compared against the boundary parsed the same way, so 1.2.0-rc1 does NOT satisfy >=1.2.0
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1070 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1070. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1071 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1071. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1072 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1072. Synthetic package injection verified alert delivery to the on-call rotation for this region.
> **Governance decision (2026-05-06 - #REG-7108)** Lena: selection direction (deviates from pip/semver): the default conflict-resolution strategy chooses the LOWEST satisfying version (conservative minimum-viable resolution), NOT the highest; only packages named in the policy's selection_overrides list take the HIGHEST satisfying version instead. This supersedes #REG-7008
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1073 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1073. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1074 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1074. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1075 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1075. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1076 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1076. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
> **Governance decision (2026-05-06 - #REG-7110)** Priya: pin override: a version named in the policy's pins for the request's channel (or under the '*' global scope) is chosen ABSOLUTELY — regardless of constraints, yanked state or pre-release state — with status 'pinned'; a pin whose version is absent from the registry is a 'conflict' (pin-missing). Pins take precedence over #REG-7108, #REG-7120 and #REG-7122
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1077 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1077. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1078 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1078. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1079 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1079. Vendor ticket on mirror retries closed; delivery within contractual budget.
> **Governance decision (2026-05-07 - #REG-7120)** Lena: yanked exemption: a yanked version is excluded from the candidate set UNLESS its package is named in the policy's yanked_exemptions list, in which case yanked builds are eligible like any other version. This supersedes #REG-7020
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1080 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1080. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1081 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1081. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1082 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1082. Synthetic package injection verified alert delivery to the on-call rotation for this region.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1083 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1083. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
> **Governance decision (2026-05-08 - #REG-7122)** Priya: pre-release admission: a pre-release candidate (maturity rank below ga) is admitted only when BOTH the channel's channel_priorities.allow_prerelease is true AND the candidate's maturity rank is >= the resolved prerelease_rank_floor for that package; otherwise it is excluded from candidates (a pin naming a pre-release still wins per #REG-7110). This supersedes #REG-7022
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1084 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1084. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1085 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1085. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1086 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1086. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
> **Governance decision (2026-05-10 - #REG-7116)** Yusuf: resolution ledger: resolution is a per-channel MONOTONE fixpoint. Constraints only ACCUMULATE as chosen versions pull in their dependencies (a re-selected version's earlier dependency constraints persist). The per-channel ledger keeps a package's FIRST chosen version for consistency across repeated sub-dependencies and only RE-SELECTS — incrementing reselect_count — when the held version stops satisfying the tightened constraint set. This supersedes #REG-7115 on structure; the re-selection cap is set by #REG-7160
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1087 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1087. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1088 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1088. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1089 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1089. Vendor ticket on mirror retries closed; delivery within contractual budget.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1090 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1090. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
> **Governance decision (2026-05-28 - #REG-7160)** Yusuf: re-selection cap, final: when a package would have to re-select beyond its resolved reselect_cap it FREEZES into a 'conflict' (provenance reselect-cap-exceeded) instead of re-resolving further; a re-selection at or below the cap is accepted and its new dependencies enqueued. Freezing refuses the re-selection rather than taking it: the package KEEPS the version it was holding, and unlike the pin-missing and unsatisfiable conflicts — which never chose anything and so report no version — a frozen entry reports that held version as its chosen_version. Only the version is held: every other field the entry carries is still read off #REG-7156 against the constraints as they finally stand, so its dep_edges are the held release's, its satisfied_constraints are everything that accumulated against the package in that channel, and its alternatives_considered are the candidates admissible at the end other than the version it held. Its reselect_count is the re-selection that was refused, so it reads one beyond the cap
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1091 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1091. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1092 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1092. Synthetic package injection verified alert delivery to the on-call rotation for this region.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1093 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1093. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1094 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1094. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1095 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1095. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1096 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1096. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
> **Governance decision (2026-05-12 - #REG-7156)** Marek: resolution entry reporting, final. Status is `resolved` for a normal selection, `pinned` for a #REG-7110 pin, and `conflict` for every failure. Each entry also records the provenance label that settled it: a selection taken in the #REG-7108 default direction is `default-selection`; one taken because the package is named in the policy's selection_overrides list is `override-selection`; a pin is `pin-override` and a pin whose version is absent from the index is `pin-missing`; a package with no admissible candidate is `unsatisfiable`; a package frozen by #REG-7160 is `reselect-cap-exceeded`. The entry's reason repeats its provenance label verbatim, prefixed with `yanked-admitted;` (no space) when a default- or override-selection settled on a yanked build; the pin and failure labels are never prefixed. A plan row repeats its entry's reason, except that a row placed by the #REG-7148 cycle rule carries `cycle-break` instead. dep_edges are the normalized dependency package names of the chosen release, de-duplicated and sorted ascending, and dep_count is their number; satisfied_constraints are the distinct constraint texts that accumulated against that package in that channel, sorted ascending; alternatives_considered are the admissible candidate versions other than the chosen one, sorted ascending by the #REG-7104 precedence key and then truncated to that package's resolved alt_report_cap, with alternatives_count their number -- where an entry chose nothing there is nothing to exclude and every admissible candidate is reported, so a pin-missing conflict carries the candidates its constraints admitted while an unsatisfiable one, having none, carries no alternative at all; is_prerelease and used_yanked describe the chosen release; and cyclic_packages names each cycle-broken install in the #REG-7145/#REG-7148 ordering — including any row the #REG-7146 cap later defers — as `channel/package`, sorted ascending, with cyclic_package_count their number
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1097 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1097. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
> **Governance decision (2026-05-08 - #REG-7145)** Priya: install order: build the dependency graph among the resolved packages of a channel and order DEPENDENCIES BEFORE DEPENDENTS; among packages whose dependencies are all already placed, the tie-break is the lexicographically smallest package name; channels are ordered ascending
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1098 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1098. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1099 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1099. Vendor ticket on mirror retries closed; delivery within contractual budget.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1100 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1100. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
> **Governance decision (2026-05-16 - #REG-7148)** Marek: cycle handling: dependency cycles are NON-FATAL — when no remaining package is installable, install the lexicographically smallest remaining package, FLAG it cyclic, and continue; cyclic packages are reported in the summary but still installed
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1101 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1101. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1102 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1102. Synthetic package injection verified alert delivery to the on-call rotation for this region.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1103 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1103. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1104 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1104. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
> **Governance decision (2026-05-24 - #REG-7146)** Marek: capacity cap: at most plan_capacity_cap install rows per channel. The cap is a FINAL pass over the fully ordered plan — not applied during resolution and not per package before ordering: order everything per #REG-7145 and #REG-7148, then walk each channel keeping only its first plan_capacity_cap rows; deferred rows contribute to no plan-derived summary field. This supersedes #REG-7046
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1105 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1105. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1106 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1106. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1107 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1107. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
> **Governance decision (2026-05-10 - #REG-7154)** Yusuf: summary aggregation (final, revising #REG-7048): max_reselect_count, max_dep_count and max_alternatives_count are maxima over the FINAL capped install_plan rows only (0 when the plan is empty); total_reselects and total_alternatives_considered sum over EVERY resolution entry; total_conflict_weight = conflict_count times the resolved default conflict_weight
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1108 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1108. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1109 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1109. Vendor ticket on mirror retries closed; delivery within contractual budget.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1110 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1110. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1111 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1111. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1112 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1112. Synthetic package injection verified alert delivery to the on-call rotation for this region.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1113 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1113. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1114 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1114. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1115 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1115. Capacity review noted rising publish volume; resolution thresholds unchanged outside the governance process.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1116 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1116. Replica checksum sync drill completed; index acknowledgment stayed within the governance SLO.
> **Governance decision (2026-06-02 - #REG-7170)** Lena: authoritative registry-index recovery, final — this supersedes the #REG-7002 draft and revises the #REG-7009 interim, and it runs BEFORE any resolve. The migration truncated `/app/data/registry_index.json`, so that file is no longer authoritative and must be rebuilt in place from the two surviving sources beside it. Begin with every package of `/app/data/registry_snapshot_pre_migration.json`, keeping the snapshot's package order and each package's release order. Then apply `/app/data/registry_replay_journal.json` in ascending journal_seq order, one entry at a time. An entry whose journal_op is `append` carries a release published after the snapshot: if that package's list already holds a record with the same version string the entry OVERWRITES the FIRST such record IN PLACE, keeping that record's existing position (it is NOT moved to the end, revising #REG-7009); otherwise the release is appended to the END of that package's list, and a package the snapshot never held is added as a new key at the end of the index. An entry whose journal_op is `retract` removes EVERY record of that package carrying that version string, whether it came from the snapshot or from an earlier journal entry (also revising #REG-7009), and contributes no record of its own. The journal always wins on overlap; the snapshot never overrides it. journal_seq, journal_op, package and reason are journal bookkeeping, not release fields: a recovered release record carries exactly version, yanked and deps, with the journal's values for a replayed release. Write the result back to `/app/data/registry_index.json` as a JSON object of package to release list in exactly the order described. A stale record left uncorrected or a retracted release left in place changes which version #REG-7108 selects, so an index rebuilt any other way yields a wrong install plan
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1117 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1117. Change-board reviewed stale exemption approvals; owners pinged before the next resolve cycle.
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1118 — quarantine (north) lane
Shift lead logged a routine observation for quarantine (north) during review window 1118. Rule-set rollback rehearsal ran clean; no changes to reconciler parameters were approved.
> **Governance decision (2026-05-18 - #REG-7150)** Priya: policy baseline (read from /app/data/resolution_policy.json at that fixed absolute path; --input never relocates it). Any field the policy file omits keeps its baseline: reselect_cap = 2; prerelease_rank_floor = 3; plan_capacity_cap = 3; conflict_weight = 5; alt_report_cap = 4
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1119 — channel-canary lane lane
Shift lead logged a routine observation for channel-canary lane during review window 1119. Vendor ticket on mirror retries closed; delivery within contractual budget.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1120 — registry-core (primary index) lane
Shift lead logged a routine observation for registry-core (primary index) during review window 1120. Dashboard tiles for resolver throughput lagged during index refresh; attributed to mirror staleness, not the reconciler.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

### Review entry 1121 — publish (edge worker) lane
Shift lead logged a routine observation for publish (edge worker) during review window 1121. Registry index audit sampled cross-account publish roles; no reconciler-relevant findings for this lane.
> **Governance decision (2026-05-18 - #REG-7152)** Priya: policy resolution, per package in three layers: start from the #REG-7150 baseline; overlay every field the policy file's `default` object supplies (it need not be complete); then overlay every field that package's entry in `package_overrides` supplies (an override names only the fields it changes). Coerce every value to int. plan_capacity_cap and conflict_weight are taken from the resolved default
Historical CSV exports remain archived and non-authoritative for the JSON reconciler acceptance.

### Review entry 1122 — resolver (control plane) lane
Shift lead logged a routine observation for resolver (control plane) during review window 1122. Synthetic package injection verified alert delivery to the on-call rotation for this region.
No reconciler semantics changed in this entry; parameters remain as approved by the governance board.

### Review entry 1123 — mirror (west) lane
Shift lead logged a routine observation for mirror (west) during review window 1123. Noise review: repeated publish webhooks traced to a flapping mirror, suppressed at the source.
Thread archived; see the #REG decision entries for anything affecting reconciler behaviour.

### Review entry 1124 — quarantine (north) lane
> **Governance decision (2026-06-06 - #REG-7174)** Yusuf: install-plan membership, final. What a channel ORDERS is exactly the entries whose status is `resolved` or `pinned`. Membership in that set is decided by STATUS alone and never by whether an entry reports a chosen_version. A #REG-7160 frozen entry is the case this settles: the cap refused its re-selection, so although it still reports the version it was holding, the channel does not install it. It never enters the #REG-7145/#REG-7148 ordering, so it takes no install row and no place in the #REG-7172 reach graph, and a dependency satisfied only by it is an edge into a package the ordering never places and adds nothing to any other package's reach_count. Its own reach_count is 0, as it is for every entry outside the ordering, including the pin-missing and unsatisfiable conflicts that never chose a version at all. Order membership and the install plan are separate questions: the #REG-7146 capacity cap runs afterwards over the ordered rows, so a `resolved` entry that did enter the ordering can still be deferred and take no plan row

> **Governance decision (2026-06-04 - #REG-7172)** Lena: dependency reach reporting, final. Every resolution entry and every install row also carries `reach_count`: the number of DISTINCT packages reachable from that package by following dependency edges among the channel's own resolved packages, counting only edges into a package the #REG-7145/#REG-7148 install order places EARLIER than it, and excluding the package itself. The install order is a total order, so a cycle-broken edge never contributes. The summary carries `max_reach_count` over all resolution entries. Reach is a property of the resolved set, not of a single release: the same package resolved in two channels may report different counts. This settles the #REG-7112 draft, which counted only direct dependencies

Shift lead logged a routine observation for quarantine (north) during review window 1124. Quarterly access recertification touched this lane; no reconciler-relevant configuration changed.
Reviewers should reconcile behaviour questions against #REG governance decisions rather than chat excerpts.

