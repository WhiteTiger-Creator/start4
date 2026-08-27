"""Verifier tests for the package-registry resolver reconciler task."""

from __future__ import annotations

import ast
import collections
import hashlib
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

WORKFLOW_PATH = Path("/app/workflow/resolver.py")
ORIGINAL_WORKFLOW_PATH = Path("/app/workflow/.resolver.original")
DEFAULT_INPUT = Path("/app/data/requests.json")
REGISTRY_PATH = Path("/app/data/registry_index.json")
SNAPSHOT_PATH = Path("/app/data/registry_snapshot_pre_migration.json")
JOURNAL_PATH = Path("/app/data/registry_replay_journal.json")
POLICY_PATH = Path("/app/data/resolution_policy.json")
SPEC_PATH = Path("/app/docs/report_spec.json")
# The contract is golden metadata: the verifier reads it from its own image,
# never from the agent-writable copy under /app.
GOLDEN_CONTRACT_PATH = Path("/tests/fixtures/contract_golden.json")
LOG_PATH = Path("/app/incident/registry_governance_log.md")
EXPECTED_FIXTURE = Path("/tests/fixtures/expected_report.json")
ALT_INPUT = Path("/tests/fixtures/alt_requests.json")

FIXTURE = json.loads(EXPECTED_FIXTURE.read_text())
SPEC = json.loads(GOLDEN_CONTRACT_PATH.read_text())

RESOLUTION_KEYS = set(SPEC["resolution_json"]["required_fields"])
PLAN_KEYS = set(SPEC["install_plan"]["required_fields"])
SUMMARY_KEYS = set(SPEC["summary_json"]["required_fields"])
STATUSES = {"resolved", "pinned", "conflict"}

# Documented wall-clock budget for one full resolver run on the graded request
# set. instruction.md and report_spec.json state the same number. The reference
# builds each package's reachable set once and reuses it, finishing in about a
# tenth of the budget; recomputing a reachable set per package is quadratic in
# the resolved set and cannot finish. Kept as a literal here (never read from the
# mutable /app spec) so the budget cannot be relaxed by editing the environment.
RUNTIME_BUDGET_SEC = 120.0
# Cheap request sets: low-layer roots resolve a small subgraph, so the
# behavioural probes stay fast. The graded runs are the expensive ones.
def _requests(pkgs, channel="stable", constraint=">=1.0.0"):
    return [{"request_id": f"probe-{i:03d}", "package": p, "source": "app",
             "channel": channel, "constraint": constraint, "note": ""}
            for i, p in enumerate(pkgs)]


SMALL_ROOTS = ["pkg-03-0000", "pkg-03-0001", "pkg-02-0002"]


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _digest(value: object) -> str:
    """Content digest, insensitive to the whitespace the contract leaves free."""
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


# --- verifier execution isolation -------------------------------------------------
# The submitted /app/workflow/resolver.py is untrusted once the separate verifier runs it.
# It executes under an unprivileged UID (65534 / nobody) via setpriv, so it cannot write the
# reward path, read the held-out fixtures under /tests, or interfere with the verifier.
_CWORK = Path("/candidate-work")
_run_ctr = itertools.count()
_SETPRIV = ["setpriv", "--reuid=65534", "--regid=65534", "--clear-groups", "--no-new-privs"]
_CANDIDATE_ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/candidate-work", "LANG": "C.UTF-8"}


def _candidate_dir() -> Path:
    d = _CWORK / f"run-{next(_run_ctr)}"
    d.mkdir(parents=True, exist_ok=True)
    os.chmod(d, 0o777)
    return d


def _run_agent(argv, cwd: Path):
    # No subprocess timeout: nothing here should pass or fail on how long the
    # grading machine took. A submission that never returns is stopped by the
    # verifier's own budget, not by a stopwatch inside an assertion.
    return subprocess.run(
        _SETPRIV + argv, check=True, capture_output=True, text=True, cwd=str(cwd),
        env=dict(_CANDIDATE_ENV),
    )


def _run_pipeline(script_path: Path = WORKFLOW_PATH, input_path: Path = DEFAULT_INPUT):
    """Run the submitted resolver once and hand back the three artifacts it wrote."""
    work = _candidate_dir()
    out_dir = work / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o777)
    staged = work / "requests.json"
    shutil.copy(str(input_path), str(staged))
    os.chmod(staged, 0o644)
    result = _run_agent(
        [sys.executable, str(script_path), "--input", str(staged), "--output-dir", str(out_dir)],
        cwd=work,
    )
    assert result.returncode == 0
    summary = _load_json(out_dir / "summary.json")
    resolution = _load_json(out_dir / "resolution.json")
    plan = _load_jsonl(out_dir / "install_plan.jsonl")
    return out_dir, summary, resolution, plan


def _run_requests(rows, script_path: Path = WORKFLOW_PATH):
    path = _candidate_dir() / "probe.json"
    _write_json(path, rows)
    os.chmod(path, 0o644)
    return _run_pipeline(script_path=script_path, input_path=path)


# The graded request sets are resolved once for the whole session and reused:
# the 24k-package resolution is the expensive part of the suite.
@pytest.fixture(scope="session")
def primary_outputs():
    return _run_pipeline()


@pytest.fixture(scope="session")
def alternate_outputs():
    return _run_pipeline(input_path=ALT_INPUT)


@pytest.fixture(scope="session")
def small_outputs():
    return _run_requests(_requests(SMALL_ROOTS))


# --------------------------------------------------------------------------
# Step 1: the authoritative registry index must be rebuilt before resolving
# --------------------------------------------------------------------------
def test_recovery_sources_are_intact():
    assert _digest(_load_json(SNAPSHOT_PATH)) == FIXTURE["snapshot_digest"]
    assert _digest(_load_json(JOURNAL_PATH)) == FIXTURE["journal_digest"]


def test_registry_index_recovered():
    index = _load_json(REGISTRY_PATH)
    assert len(index) == FIXTURE["recovered_package_count"]
    assert sum(len(v) for v in index.values()) == FIXTURE["recovered_release_count"]
    assert _digest(index) == FIXTURE["recovered_index_digest"]


def test_recovered_records_carry_no_journal_bookkeeping():
    index = _load_json(REGISTRY_PATH)
    for rows in list(index.values())[:400]:
        for record in rows:
            assert set(record) == {"version", "yanked", "deps"}


def test_shipped_truncated_index_was_not_left_in_place():
    assert _digest(_load_json(REGISTRY_PATH)) != FIXTURE["shipped_truncated_digest"]


def test_resolver_output_depends_on_the_recovered_index(small_outputs):
    """Resolving against the shipped truncated index cannot give the graded answer."""
    assert small_outputs[1]["resolved_package_count"] > 0


# --------------------------------------------------------------------------
# Graded outputs
# --------------------------------------------------------------------------
def test_cli_exists():
    assert WORKFLOW_PATH.is_file()
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "--input" in text and "--output-dir" in text


def test_output_dir_contains_exactly_three_files(primary_outputs):
    assert sorted(p.name for p in primary_outputs[0].iterdir()) == [
        "install_plan.jsonl", "resolution.json", "summary.json",
    ]


def test_primary_summary_matches_fixture(primary_outputs):
    assert primary_outputs[1] == FIXTURE["primary"]["summary"]


def test_primary_resolution_matches_fixture(primary_outputs):
    assert _digest(primary_outputs[2]) == FIXTURE["primary"]["resolution_digest"]


def test_primary_plan_matches_fixture(primary_outputs):
    assert _digest(primary_outputs[3]) == FIXTURE["primary"]["plan_digest"]


def test_alternate_request_set_matches_fixture(alternate_outputs):
    _, summary, resolution, plan = alternate_outputs
    assert summary == FIXTURE["alternate"]["summary"]
    assert _digest(resolution) == FIXTURE["alternate"]["resolution_digest"]
    assert _digest(plan) == FIXTURE["alternate"]["plan_digest"]


def test_runtime_budget_is_stated_in_the_contract():
    assert float(SPEC["runtime_budget_seconds"]) == RUNTIME_BUDGET_SEC


# --------------------------------------------------------------------------
# Reach reporting (#REG-7172)
# --------------------------------------------------------------------------
def test_reach_counts_are_reported_and_vary(primary_outputs):
    resolution = primary_outputs[2]
    counts = [e["reach_count"] for rows in resolution.values() for e in rows]
    assert counts
    assert min(counts) == 0, "leaf packages reach nothing"
    assert max(counts) == primary_outputs[1]["max_reach_count"]
    assert len(set(counts)) > 50, "reach must vary across the resolved set"


def test_reach_is_bounded_by_the_resolved_set(primary_outputs):
    _, summary, resolution, _ = primary_outputs
    per_channel = {}
    for rows in resolution.values():
        for e in rows:
            per_channel[e["channel"]] = per_channel.get(e["channel"], 0) + 1
    for rows in resolution.values():
        for e in rows:
            assert 0 <= e["reach_count"] < per_channel[e["channel"]]


def test_reach_covers_the_dependencies_the_order_places_earlier(primary_outputs):
    """#REG-7172 counts edges into packages the install order places EARLIER.

    The bound asserted here is the one the rule implies. A blanket
    reach_count >= dep_count is not: an edge into a package the order places
    later (a cycle-broken edge) or into one the channel never resolved
    contributes nothing, so a correct run can report a reach below its own dep
    count. The install plan is a subsequence of the order, so every package it
    places before an entry is genuinely earlier in the order, and each such
    dependency edge is a distinct reachable package.
    """
    resolution = primary_outputs[2]
    plan = primary_outputs[3]
    placed_before: dict[tuple, set] = {}
    seen: dict[str, set] = {}
    for row in plan:
        earlier = seen.setdefault(row["channel"], set())
        placed_before[(row["channel"], row["package"])] = set(earlier)
        earlier.add(row["package"])

    checked = binding = 0
    for package, rows in resolution.items():
        for e in rows:
            earlier = placed_before.get((e["channel"], package))
            if earlier is None:
                continue
            floor = len([d for d in e["dep_edges"] if d in earlier])
            assert e["reach_count"] >= floor, (e, floor)
            checked += 1
            binding += floor > 0
    assert checked, "no planned entry to measure reach against"
    assert binding, "no planned entry depends on a package placed earlier, so the bound is vacuous"

    counts = [e["reach_count"] for rows in resolution.values() for e in rows]
    deps = [e["dep_count"] for rows in resolution.values() for e in rows]
    assert max(counts) > max(deps), \
        "reach never exceeds a direct dep count, so it is not transitive"


# --------------------------------------------------------------------------
# Schema / ordering invariants
# --------------------------------------------------------------------------
def test_summary_schema(primary_outputs):
    summary = primary_outputs[1]
    assert set(summary) == SUMMARY_KEYS
    assert summary["schema_version"] == SPEC["summary_json"]["schema_version"]


def test_resolution_schema_and_sorting(primary_outputs):
    resolution = primary_outputs[2]
    assert isinstance(resolution, dict)
    assert list(resolution) == sorted(resolution)
    for rows in resolution.values():
        assert [r["channel"] for r in rows] == sorted(r["channel"] for r in rows)
        for entry in rows:
            assert set(entry) == RESOLUTION_KEYS
            assert entry["status"] in STATUSES
            assert entry["dep_edges"] == sorted(entry["dep_edges"])
            assert entry["dep_count"] == len(entry["dep_edges"])


def test_plan_required_fields(primary_outputs):
    plan = primary_outputs[3]
    for idx, row in enumerate(plan):
        assert set(row) == PLAN_KEYS
        assert row["order_index"] == idx
        # #REG-7174: the plan installs resolved and pinned entries only, so a
        # conflict row here is a membership error, not merely an odd status.
        assert row["status"] in {"resolved", "pinned"}, (row["package"], row["status"])


def test_a_version_holding_conflict_is_not_installed(primary_outputs):
    """#REG-7174: plan membership is decided by status, never by having a version.

    corelib freezes under the #REG-7160 re-selection cap and still reports the
    version it was holding, so "has a chosen_version" and "is installed" come
    apart exactly here. Without this the rule lived only in the sealed digests.
    """
    _, _, resolution, plan = primary_outputs
    frozen = [e for e in resolution["corelib"] if e["channel"] == "stable"]
    assert len(frozen) == 1, frozen
    entry = frozen[0]
    assert entry["status"] == "conflict"
    assert entry["provenance"] == "reselect-cap-exceeded"
    assert entry["chosen_version"] is not None, "the freeze holds the version it had"
    assert entry["reach_count"] == 0, "an entry the plan never places reaches nothing"

    installed = {(row["channel"], row["package"]) for row in plan}
    assert ("stable", "corelib") not in installed, (
        "a frozen entry took an install row; #REG-7174 excludes it")

    # The rule stated over the whole run, so this cannot pass by luck on one
    # package: nothing outside the ordered set ever reaches a plan row. The
    # converse does not hold, because #REG-7146 defers ordered rows past the cap.
    for package, entries in resolution.items():
        for e in entries:
            if (e["channel"], package) in installed:
                assert e["status"] in {"resolved", "pinned"}, (
                    package, e["channel"], e["status"])
            if e["status"] not in {"resolved", "pinned"}:
                assert e["reach_count"] == 0, (package, e["channel"], e["reach_count"])

    # And the absences are the cap's doing, not silent dropping: each channel
    # carries as many rows as it has orderable entries, up to the cap.
    cap = _load_json(POLICY_PATH)["default"]["plan_capacity_cap"]
    orderable = collections.Counter(
        e["channel"] for entries in resolution.values() for e in entries
        if e["status"] in {"resolved", "pinned"})
    rows = collections.Counter(row["channel"] for row in plan)
    for channel, available in orderable.items():
        assert rows[channel] == min(available, cap), (channel, rows[channel], available, cap)


def test_a_frozen_entry_contributes_no_reach_to_its_dependents(primary_outputs):
    """An edge into a package the plan never places adds nothing to reach_count.

    #REG-7174 says a dependency satisfied only by a frozen entry is an edge into
    something the channel does not install, so it cannot be counted. Recomputed
    here from the plan itself rather than trusted from the digest.
    """
    _, _, resolution, plan = primary_outputs
    position = {(row["channel"], row["package"]): row["order_index"] for row in plan}
    reachable: dict[tuple, set] = {}
    for row in sorted(plan, key=lambda r: r["order_index"]):
        key = (row["channel"], row["package"])
        seen: set = set()
        for dep in row["dep_edges"]:
            dkey = (row["channel"], dep)
            if dkey in position and position[dkey] < row["order_index"]:
                seen.add(dkey)
                seen |= reachable[dkey]
        reachable[key] = seen
        assert row["reach_count"] == len(seen), (key, row["reach_count"], len(seen))


def test_install_plan_jsonl_compact(primary_outputs):
    raw = (primary_outputs[0] / "install_plan.jsonl").read_text(encoding="utf-8")
    first = raw.splitlines()[0]
    assert ", " not in first and '": ' not in first


def test_summary_math_consistency(primary_outputs):
    _, summary, resolution, plan = primary_outputs
    entries = [e for rows in resolution.values() for e in rows]
    assert summary["resolved_package_count"] == len(entries)
    assert summary["planned_install_count"] == len(plan)
    assert sum(summary["status_counts"].values()) == len(entries)
    assert summary["total_reselects"] == sum(e["reselect_count"] for e in entries)
    assert summary["max_reach_count"] == max(e["reach_count"] for e in entries)


def test_summary_request_counts_track_the_input(primary_outputs):
    requests = _load_json(DEFAULT_INPUT)
    assert primary_outputs[1]["raw_request_count"] == len(requests)


def test_status_counts_enumerate_all_three(primary_outputs):
    counts = primary_outputs[1]["status_counts"]
    assert set(counts) == STATUSES


# --------------------------------------------------------------------------
# Integrity, generalisation and anti-shortcut
# --------------------------------------------------------------------------
def test_original_snapshot_preserved():
    assert ORIGINAL_WORKFLOW_PATH.exists()
    digest = hashlib.sha256(ORIGINAL_WORKFLOW_PATH.read_bytes()).hexdigest()
    assert digest == FIXTURE["broken_pipeline_sha256"]


def test_broken_snapshot_is_wrong(small_outputs):
    """The shipped draft must not reproduce the governed result."""
    rows = _requests(SMALL_ROOTS)
    _, broken_summary, broken_resolution, _ = _run_requests(
        rows, script_path=ORIGINAL_WORKFLOW_PATH)
    assert (broken_summary != small_outputs[1]
            or _digest(broken_resolution) != _digest(small_outputs[2]))


def test_pipeline_rerun_idempotent():
    rows = _requests(SMALL_ROOTS)
    first = _run_requests(rows)
    second = _run_requests(rows)
    assert first[1] == second[1]
    assert _digest(first[2]) == _digest(second[2])
    assert _digest(first[3]) == _digest(second[3])


def test_pipeline_supports_alternate_input(alternate_outputs):
    assert alternate_outputs[1]["resolved_package_count"] > 0


def test_cli_defaults_work_and_match_explicit_run(primary_outputs):
    default_dir = Path("/app/output")
    if default_dir.exists():
        shutil.rmtree(default_dir)
    default_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(default_dir, 0o777)
    _run_agent([sys.executable, str(WORKFLOW_PATH)], cwd=_candidate_dir())
    # all three artifacts, not just the summary: a resolver that special-cases the
    # default invocation must not be able to leave the plan or the resolution behind
    assert sorted(q.name for q in default_dir.iterdir()) == [
        "install_plan.jsonl", "resolution.json", "summary.json"]
    assert _load_json(default_dir / "summary.json") == primary_outputs[1]
    assert _digest(_load_json(default_dir / "resolution.json")) == _digest(primary_outputs[2])
    assert _digest(_load_jsonl(default_dir / "install_plan.jsonl")) == _digest(primary_outputs[3])


def test_submitted_program_runs_unprivileged_and_cannot_write_reward():
    work = _candidate_dir()
    probe = work / "probe.py"
    probe.write_text(
        "import os\n"
        "print(os.getuid())\n"
        "try:\n"
        "    open('/logs/verifier/reward.txt').read()\n"
        "    print('readable')\n"
        "except OSError:\n"
        "    print('unreadable')\n"
        "try:\n"
        "    open('/logs/verifier/reward.txt', 'w').write('1')\n"
        "    print('writable')\n"
        "except OSError:\n"
        "    print('unwritable')\n",
        encoding="utf-8")
    os.chmod(probe, 0o644)
    result = subprocess.run(
        _SETPRIV + [sys.executable, str(probe)], capture_output=True, text=True,
        cwd=str(work), env=dict(_CANDIDATE_ENV), check=False)
    assert result.returncode == 0, result.stderr[-2000:]
    assert result.stdout.splitlines() == ["65534", "unreadable", "unwritable"], result.stdout


def test_policy_source_path_decides_the_plan_it_produces():
    """The capacity cap is resolved from the policy file, and its new value binds.

    Requiring only that the run come out different would pass a resolver that
    reads the file and then plans by some constant of its own, so the mutated run
    is checked against the plan the amended cap implies: #REG-7146 applies the cap
    after the ordering, so a cap of one keeps each channel's first row and nothing
    else.
    """
    rows = _requests(SMALL_ROOTS)
    _, base_summary, _, base_plan = _run_requests(rows)
    assert len(base_plan) > 1, "the probe plans too little to tell a cap from a constant"
    expected = []
    seen = set()
    for row in base_plan:
        if row["channel"] not in seen:
            seen.add(row["channel"])
            expected.append((row["channel"], row["package"], row["version"]))

    original = POLICY_PATH.read_text(encoding="utf-8")
    try:
        policy = json.loads(original)
        policy.setdefault("default", {})["plan_capacity_cap"] = 1
        POLICY_PATH.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        _, summary, _, plan = _run_requests(rows)
    finally:
        POLICY_PATH.write_text(original, encoding="utf-8")
    assert [(r["channel"], r["package"], r["version"]) for r in plan] == expected
    assert summary["planned_install_count"] == len(expected)
    assert summary != base_summary


def test_registry_source_path_affects_output():
    """The registry index is read from its fixed path, not inlined.

    The victim is drawn from the packages the probe actually resolves; yanking one
    outside that closure would leave the output identical and prove nothing.
    """
    rows = _requests(SMALL_ROOTS)
    original = REGISTRY_PATH.read_text(encoding="utf-8")
    _, baseline, base_resolution, _ = _run_requests(rows)
    exempt = set(_load_json(POLICY_PATH).get("yanked_exemptions", []))
    try:
        data = json.loads(original)
        victim = sorted((set(base_resolution) & set(data)) - exempt)[0]
        data[victim] = [dict(r, yanked=True) for r in data[victim]]
        REGISTRY_PATH.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
        _, summary, resolution, _ = _run_requests(rows)
    finally:
        REGISTRY_PATH.write_text(original, encoding="utf-8")
    # every release of the victim is now yanked and it is not exempt, so #REG-7120
    # leaves it with no admissible candidate at all
    assert base_resolution[victim][0]["status"] == "resolved"
    for entry in resolution[victim]:
        assert entry["status"] == "conflict", victim
        assert entry["provenance"] == "unsatisfiable", victim
        assert entry["chosen_version"] is None, victim
    weight = _load_json(POLICY_PATH)["default"]["conflict_weight"]
    added = len(resolution[victim])
    assert summary["conflict_count"] == baseline["conflict_count"] + added
    assert summary["total_conflict_weight"] == baseline["total_conflict_weight"] + weight * added


# Each entry is a branch the policy and the log define, and each is reached by the
# graded request set: a resolver that skips one cannot match these.
GOVERNED_BRANCHES = (
    ("legacypin", "stable", "0.6.0", "pinned", "pin-override"),
    ("legacypin", "canary", "1.0.0", "resolved", "default-selection"),
    ("ghostpin", "stable", None, "conflict", "pin-missing"),
    ("hotfix", "stable", "1.0.0", "resolved", "yanked-admitted;default-selection"),
    ("netcore", "stable", "1.4.0", "resolved", "default-selection"),
    ("cryptobox", "stable", "1.4.0", "resolved", "override-selection"),
    ("edgekit", "canary", "1.0.0-rc.1", "resolved", "default-selection"),
    ("edgekit", "stable", "1.2.0", "resolved", "default-selection"),
    ("corelib", "stable", "2.0.0", "conflict", "reselect-cap-exceeded"),
)


@pytest.mark.parametrize("package,channel,version,status,reason", GOVERNED_BRANCHES)
def test_each_governed_branch_is_reached_and_settled(
        primary_outputs, package, channel, version, status, reason):
    """Every documented branch is exercised by the graded run and settles as ruled.

    The pin binds against the constraint and only on its own channel; a pin naming
    an absent version is a conflict; a yanked build stays eligible where the policy
    exempts its package and is excluded where it does not; the override takes the
    highest rather than the lowest; a pre-release clears the rank floor only on a
    channel that allows one; and the per-package re-selection cap freezes a package
    the default cap would have resolved.
    """
    resolution = primary_outputs[2]
    assert package in resolution, package
    entries = [e for e in resolution[package] if e["channel"] == channel]
    assert len(entries) == 1, (package, channel)
    entry = entries[0]
    assert entry["chosen_version"] == version, (package, channel)
    assert entry["status"] == status, (package, channel)
    assert entry["reason"] == reason, (package, channel)


def test_the_yanked_exemption_is_what_separates_hotfix_from_netcore(primary_outputs):
    """The two packages differ only in the exemption list, and only there."""
    resolution = primary_outputs[2]
    exempt = set(_load_json(POLICY_PATH)["yanked_exemptions"])
    assert "hotfix" in exempt and "netcore" not in exempt
    hotfix = resolution["hotfix"][0]
    netcore = resolution["netcore"][0]
    assert hotfix["used_yanked"] is True and hotfix["chosen_version"] == "1.0.0"
    assert netcore["used_yanked"] is False and netcore["chosen_version"] == "1.4.0"
    index = _load_json(REGISTRY_PATH)
    assert {r["version"] for r in index["hotfix"] if r["yanked"]} == {"1.0.0"}
    assert {r["version"] for r in index["netcore"] if r["yanked"]} == {"1.0.0"}


def test_the_package_alternative_cap_overrides_the_baseline(primary_outputs):
    """cryptobox reports two alternatives where the baseline would report four."""
    resolution = primary_outputs[2]
    policy = _load_json(POLICY_PATH)
    cap = policy["package_overrides"]["cryptobox"]["alt_report_cap"]
    entry = resolution["cryptobox"][0]
    index = _load_json(REGISTRY_PATH)
    assert len(index["cryptobox"]) - 1 > cap, "too few releases to tell the cap from the baseline"
    assert entry["alternatives_count"] == cap == len(entry["alternatives_considered"])
    assert entry["chosen_version"] not in entry["alternatives_considered"]


def test_capacity_cap_applied_after_ordering(small_outputs):
    plan = small_outputs[3]
    policy = _load_json(POLICY_PATH)
    cap = policy["default"]["plan_capacity_cap"]
    per_channel: dict[str, int] = {}
    for row in plan:
        per_channel[row["channel"]] = per_channel.get(row["channel"], 0) + 1
    for count in per_channel.values():
        assert count <= cap


def test_cycles_are_non_fatal(primary_outputs):
    """The registry really does contain cycles, and the run resolves them anyway.

    A cycle must not abort the resolution and must not drop the packages caught in
    it: every named cyclic package still carries a resolved entry.
    """
    summary, resolution = primary_outputs[1], primary_outputs[2]
    named = summary["cyclic_packages"]
    assert isinstance(named, list)
    assert summary["cyclic_package_count"] == len(named)
    assert named, "the graded registry contains no cycle, so the rule is untested"
    resolved = set(resolution)
    for entry in named:
        # the summary names a cycle member as channel/package
        pkg = entry.split("/", 1)[1] if "/" in entry else entry
        assert pkg in resolved, f"cyclic package {entry} was dropped from the resolution"


def _imported_modules(source: str) -> set[str]:
    mods = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module.split(".")[0])
    return mods


def _workflow_sources() -> list[Path]:
    """Every Python file the submission ships under /app/workflow.

    Scanning resolver.py alone let a helper module beside it import packaging or
    reach eval and pass, so the whole directory is read. The frozen snapshot is
    not a .py file and is checked by its own hash elsewhere.
    """
    sources = sorted(WORKFLOW_PATH.parent.rglob("*.py"))
    assert WORKFLOW_PATH in sources, "the resolver is not where the contract puts it"
    return sources


def test_reconciler_does_not_import_resolver_libraries():
    banned = set(SPEC["workflow_repair"]["prohibited_imports"])
    for source in _workflow_sources():
        found = _imported_modules(source.read_text(encoding="utf-8")) & banned
        assert not found, f"{source.name} imports {sorted(found)}"


def test_ast_check_catches_packaging_importing_engine():
    assert "packaging" in _imported_modules("import packaging.version\n")
    assert "pip" in _imported_modules("from pip import main\n")


BANNED_DYNAMIC = {"eval", "exec", "compile"}


def _dynamic_execution_offences(source: str) -> list[str]:
    """Names in `source` that reach eval, exec or compile, however they are spelled.

    A bare-name call check only catches `eval(...)`. It misses `builtins.eval(...)`
    and it misses a rebinding such as `run = eval` or `from builtins import exec as
    run`, so the ban is followed through attribute access and through aliases.
    """
    tree = ast.parse(source)
    aliases: set[str] = set()
    # Resolve rebindings first, so a call through one is recognised wherever it sits.
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name in BANNED_DYNAMIC:
                    aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.Assign):
            source_name = None
            if isinstance(node.value, ast.Name) and node.value.id in BANNED_DYNAMIC | aliases:
                source_name = node.value.id
            elif (isinstance(node.value, ast.Attribute)
                  and node.value.attr in BANNED_DYNAMIC
                  and isinstance(node.value.value, ast.Name)
                  and node.value.value.id.endswith("builtins")):
                source_name = node.value.attr
            if source_name:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        aliases.add(target.id)

    # Which names refer to the builtins module, so builtins.eval is caught while
    # re.compile -- an ordinary, entirely legitimate call -- is not.
    builtin_mods = {"builtins"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "builtins":
                    builtin_mods.add(alias.asname or alias.name)

    offences = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Attribute) and node.attr in BANNED_DYNAMIC
                and isinstance(node.value, ast.Name) and node.value.id in builtin_mods):
            offences.append(f"{node.value.id}.{node.attr}")
        elif isinstance(node, ast.Name) and node.id in BANNED_DYNAMIC | aliases:
            offences.append(node.id)
    return offences


def test_resolver_has_no_dynamic_execution():
    """Nothing under /app/workflow reaches eval, exec or compile, by any spelling.

    The resolver may import a helper it ships beside itself, so the ban is read
    across the whole directory rather than off the entry point alone.
    """
    for source in _workflow_sources():
        offences = _dynamic_execution_offences(source.read_text(encoding="utf-8"))
        assert not offences, (
            f"{source.name} reaches dynamic execution: {sorted(set(offences))}")


def test_a_helper_beside_the_resolver_is_scanned_too(tmp_path: Path):
    """The widened scan is real: a sibling module is read like the entry point.

    A submission that moved the banned import or the eval call one file sideways
    passed both scans while the resolver itself looked clean.
    """
    helper = WORKFLOW_PATH.parent / "_scan_probe.py"
    helper.write_text("import packaging.version\n\n\ndef pick(a):\n    return eval(a)\n",
                      encoding="utf-8")
    try:
        assert helper in _workflow_sources()
        banned = set(SPEC["workflow_repair"]["prohibited_imports"])
        offended = False
        for source in _workflow_sources():
            text = source.read_text(encoding="utf-8")
            if _imported_modules(text) & banned or _dynamic_execution_offences(text):
                offended = True
        assert offended, "a sibling module carrying both offences was not seen"
    finally:
        helper.unlink()


def test_the_dynamic_execution_ban_catches_an_alias():
    """Negative control: the ban is only worth having if the aliases fail it.

    Each of these passed the previous bare-name check, which is why they are
    written out here rather than assumed.
    """
    for source in (
            "import builtins\nbuiltins.eval('1')\n",
            "run = eval\nrun('1')\n",
            "from builtins import exec as run\nrun('x=1')\n",
            "import builtins\nrun = builtins.compile\nrun('1', '<s>', 'eval')\n"):
        assert _dynamic_execution_offences(source), source
    # and ordinary code still passes, including re.compile, which is not dynamic
    # execution and which the reference itself uses
    assert not _dynamic_execution_offences("import json\njson.loads('{}')\n")
    assert not _dynamic_execution_offences("import re\n_RE = re.compile(r'^a$')\n")


def test_governance_log_present():
    assert LOG_PATH.is_file() and LOG_PATH.stat().st_size > 1000


def test_shipped_contract_matches_the_golden_copy():
    """The output contract in the environment is unmodified.

    Field lists, container shapes and sort orders are golden metadata and are read
    from the verifier's own image; this proves the agent's copy still agrees with
    it, so the contract cannot be trimmed to weaken a schema check.
    """
    shipped = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    assert shipped == json.loads(GOLDEN_CONTRACT_PATH.read_text(encoding="utf-8"))



# --------------------------------------------------------------------------
# The recovery is load-bearing: each plausible wrong index differs, and the
# resolver run against it disagrees with the sealed result
# --------------------------------------------------------------------------
def _wrong_index(kind: str) -> dict:
    """Rebuild the index the way a superseded decision would have.

    "snapshot_only" ignores the replay journal altogether. "concatenated" is the
    #REG-7002 draft: every journal entry is appended to its package rather than
    overwriting the record already carrying that version, and a retraction
    removes nothing.
    """
    snapshot = _load_json(SNAPSHOT_PATH)
    index = {package: [dict(r) for r in rows] for package, rows in snapshot.items()}
    if kind == "snapshot_only":
        return index
    for entry in sorted(_load_json(JOURNAL_PATH), key=lambda e: e["journal_seq"]):
        if entry["journal_op"] != "append":
            continue          # the draft's defect: a retraction removes nothing
        index.setdefault(entry["package"], []).append(
            {f: entry[f] for f in ("version", "yanked", "deps")})
    return index


def test_each_wrong_index_differs_from_the_recovered_one():
    """The shipped truncation, the snapshot alone and the concatenation all differ."""
    recovered = FIXTURE["recovered_index_digest"]
    assert FIXTURE["shipped_truncated_digest"] != recovered
    assert FIXTURE["snapshot_digest"] != recovered
    for kind in ("snapshot_only", "concatenated"):
        assert _digest(_wrong_index(kind)) != recovered, kind


def test_resolver_output_depends_on_which_index_it_reads():
    """Re-running the agent's own resolver on each wrong index disagrees with the seal.

    This is what makes the two stages provably dependent: a resolver that is
    perfectly repaired still cannot reach the sealed outputs from a wrongly
    rebuilt index.
    """
    # probe the packages the journal actually touches: elsewhere a wrong merge
    # and the governed one agree, so a probe that misses them proves nothing
    journal = _load_json(JOURNAL_PATH)
    retracted = sorted({e["package"] for e in journal if e["journal_op"] == "retract"})
    assert retracted, "the journal retracts nothing, so the merge rule is untested"
    rows = _requests(retracted[:3])
    original = REGISTRY_PATH.read_text(encoding="utf-8")
    baseline = _run_requests(rows)[1]
    try:
        for kind in ("snapshot_only", "concatenated"):
            REGISTRY_PATH.write_text(
                json.dumps(_wrong_index(kind), separators=(",", ":")) + "\n", encoding="utf-8")
            assert _run_requests(rows)[1] != baseline, kind
    finally:
        REGISTRY_PATH.write_text(original, encoding="utf-8")


def test_install_order_takes_the_smallest_package_ready_at_that_moment():
    """#REG-7145 re-picks after every placement, rather than draining a ready batch.

    A package that becomes installable partway through has to be able to win
    against one that was installable from the start. With `alpha` free, `beta`
    depending on `alpha`, and `omega` free, placing `alpha` makes `beta` ready, and
    `beta` sorts below `omega`, so the order is alpha, beta, omega. Ordering that
    drains the initially-ready set first emits alpha, omega, beta -- a legal
    topological order, and the wrong one. The two readings only diverge on a shape
    like this, which is why the graded registry alone never separated them.
    """
    original = REGISTRY_PATH.read_text(encoding="utf-8")
    try:
        staged = {
            "alpha": [{"version": "1.0.0", "yanked": False, "deps": []}],
            "beta": [{"version": "1.0.0", "yanked": False,
                      "deps": [{"package": "alpha", "constraint": ">=1.0.0"}]}],
            "omega": [{"version": "1.0.0", "yanked": False, "deps": []}],
        }
        REGISTRY_PATH.write_text(
            json.dumps(staged, separators=(",", ":")) + "\n", encoding="utf-8")
        _, _, resolution, plan = _run_requests(_requests(["beta", "omega"]))
    finally:
        REGISTRY_PATH.write_text(original, encoding="utf-8")

    assert set(resolution) == {"alpha", "beta", "omega"}, sorted(resolution)
    order = [row["package"] for row in plan]
    assert order == ["alpha", "beta", "omega"], order
    # Name the batch reading explicitly so a regression says what it regressed to.
    assert order != ["alpha", "omega", "beta"], (
        "install order drained the initially-ready set before re-picking; #REG-7145 "
        "chooses the smallest package among those ready at that moment")


def test_install_plan_lines_are_all_compact():
    """Every plan line is compact JSON, not just the first one."""
    out_dir = _run_pipeline()[0]
    text = (out_dir / "install_plan.jsonl").read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.strip()]
    assert lines
    for number, line in enumerate(lines, start=1):
        assert ": " not in line, f"line {number} is not compact"
        assert json.dumps(json.loads(line), separators=(",", ":")) == line, (
            f"line {number} is not the compact serialisation of its own content")


def test_recovered_index_and_summary_preserve_the_contracted_key_orders(primary_outputs):
    """Key order is governed, and a digest over sorted keys cannot see it.

    The sealed digests canonicalise with sort_keys, so they pin content and say
    nothing about the order the keys were written in. #REG-7170 fixes the index
    order and the contract fixes status_counts, so both are read off the raw text.
    """
    index_keys = list(json.loads(
        REGISTRY_PATH.read_text(encoding="utf-8")).keys())
    # #REG-7170 fixes this order as the snapshot's package order, with a package
    # the snapshot never held added as a new key AT THE END. Asserting ascending
    # order instead would only be testing that the shipped snapshot happens to be
    # sorted, and would fail a correct rebuild the moment the journal introduces a
    # package that sorts earlier than one already there.
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    journal = json.loads(JOURNAL_PATH.read_text(encoding="utf-8"))
    expected_keys = list(snapshot)
    seen = set(expected_keys)
    for entry in sorted(journal, key=lambda e: e["journal_seq"]):
        if entry.get("journal_op") == "append" and entry["package"] not in seen:
            seen.add(entry["package"])
            expected_keys.append(entry["package"])
    assert index_keys == expected_keys, (
        "the rebuilt index does not carry the snapshot's package order with "
        "journal-added packages appended")

    _, summary, _, _ = primary_outputs
    wanted = SPEC["summary_json"]["status_counts_key_order"]
    assert list(summary["status_counts"].keys()) == wanted, list(summary["status_counts"].keys())


# --------------------------------------------------------------------------
# The documented input coercions and the constraint grammar
# --------------------------------------------------------------------------
_COERCION_REGISTRY = {
    "crypto-box": [
        {"version": "1.0.0", "yanked": False, "deps": []},
        {"version": "1.5.0", "yanked": False, "deps": []},
        {"version": "2.0.0", "yanked": False, "deps": []},
    ],
    "unknown": [{"version": "1.0.0", "yanked": False, "deps": []}],
}


def _staged_registry_run(rows):
    """Resolve `rows` against a small staged registry, restoring it afterwards."""
    original = REGISTRY_PATH.read_text(encoding="utf-8")
    try:
        REGISTRY_PATH.write_text(
            json.dumps(_COERCION_REGISTRY, separators=(",", ":")) + "\n", encoding="utf-8")
        return _run_requests(rows)
    finally:
        REGISTRY_PATH.write_text(original, encoding="utf-8")


def _staged_run(rows, registry, policy_patch=None):
    """Resolve `rows` against a staged registry and an optionally patched policy.

    Both files are restored whatever happens, so a probe cannot leave the graded
    inputs altered for the fixtures that follow it.
    """
    reg_original = REGISTRY_PATH.read_text(encoding="utf-8")
    pol_original = POLICY_PATH.read_text(encoding="utf-8")
    try:
        REGISTRY_PATH.write_text(
            json.dumps(registry, separators=(",", ":")) + "\n", encoding="utf-8")
        if policy_patch is not None:
            policy = json.loads(pol_original)
            policy_patch(policy)
            POLICY_PATH.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        return _run_requests(rows)
    finally:
        REGISTRY_PATH.write_text(reg_original, encoding="utf-8")
        POLICY_PATH.write_text(pol_original, encoding="utf-8")


def test_stale_files_are_cleared_from_the_output_directory(tmp_path: Path):
    """A run presents its own artifacts, not whatever an earlier run left behind.

    The contract says a run leaves exactly the three artifacts. Every other check
    here resolves into a fresh directory, so a resolver that simply wrote its
    three files over whatever was already there would satisfy all of them while
    leaving a stale companion visible.
    """
    work = _candidate_dir()
    out_dir = work / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o777)
    stale = out_dir / "stale.tmp"
    stale.write_text("left over from an earlier run\n", encoding="utf-8")
    os.chmod(stale, 0o666)
    shadow = out_dir / "summary.json"
    shadow.write_text("{}\n", encoding="utf-8")
    os.chmod(shadow, 0o666)
    leftover_dir = out_dir / "leftover"
    leftover_dir.mkdir()
    (leftover_dir / "inner.json").write_text("{}\n", encoding="utf-8")
    os.chmod(leftover_dir / "inner.json", 0o666)
    os.chmod(leftover_dir, 0o777)

    _run_agent([sys.executable, str(WORKFLOW_PATH), "--output-dir", str(out_dir)], cwd=work)
    names = sorted(q.name for q in out_dir.iterdir())
    assert names == ["install_plan.jsonl", "resolution.json", "summary.json"], names
    assert _load_json(out_dir / "summary.json") != {}, "the stale summary was left in place"


def test_request_names_are_canonicalised_before_they_are_matched():
    """report_spec.json's coercion is applied to package, source and channel.

    The graded request set is already canonical, so nothing else here exercises
    this: a resolver that matched raw names would agree with every sealed fixture
    while violating the coercion the contract states.
    """
    spellings = ["  Crypto_Box  ", "CRYPTO.BOX", "crypto--box", "Crypto._.Box"]
    rows = [{"request_id": f"c-{i}", "package": name, "source": " App ",
             "channel": " STABLE ", "constraint": ">=1.0.0", "note": ""}
            for i, name in enumerate(spellings)]
    _, _, resolution, _ = _staged_registry_run(rows)
    assert set(resolution) == {"crypto-box"}, sorted(resolution)
    entry = resolution["crypto-box"][0]
    assert entry["channel"] == "stable", entry["channel"]
    assert entry["status"] == "resolved"


def test_a_name_that_coerces_to_nothing_becomes_unknown():
    """An empty result becomes 'unknown', which the contract names explicitly."""
    rows = [{"request_id": "c-empty", "package": "  --__--  ", "source": "app",
             "channel": "stable", "constraint": ">=1.0.0", "note": ""}]
    _, _, resolution, _ = _staged_registry_run(rows)
    assert set(resolution) == {"unknown"}, sorted(resolution)


@pytest.mark.parametrize("constraint,expected", [
    (">=1.0.0", "1.0.0"),
    (">1.0.0", "1.5.0"),
    ("==2.0.0", "2.0.0"),
    ("2.0.0", "2.0.0"),          # #REG-7106: a bare version is an exact ==
    ("<=1.5.0", "1.0.0"),
    ("<2.0.0", "1.0.0"),
    ("", "1.0.0"),               # '' is ANY
    ("*", "1.0.0"),              # '*' is ANY
    (">1.0.0,<2.0.0", "1.5.0"),  # a comma joins clauses with AND
    ("~=1.5", "1.5.0"),          # >=1.5.0,<2.0.0
    ("  >=  1.5.0  ", "1.5.0"),  # internal whitespace collapses
])
def test_every_documented_constraint_operator_selects_as_ruled(constraint, expected):
    """#REG-7106 names six operators, two any-tokens and a clause separator.

    The graded requests only ever use '>=', so without this a resolver that
    understood nothing else would still match both sealed fixtures.
    """
    rows = [{"request_id": "op-1", "package": "crypto-box", "source": "app",
             "channel": "stable", "constraint": constraint, "note": ""}]
    _, _, resolution, _ = _staged_registry_run(rows)
    entry = resolution["crypto-box"][0]
    assert entry["status"] == "resolved", (constraint, entry)
    assert entry["chosen_version"] == expected, (constraint, entry["chosen_version"])


def test_the_default_selection_takes_the_lowest_satisfying_version():
    """Selection direction deviates from pip and semver: lowest wins by default.

    A package offering several satisfying versions resolves to the lowest of them,
    which the "highest satisfying version" reading gets exactly backwards.
    """
    index = _load_json(REGISTRY_PATH)
    target = next(
        (pkg for pkg, rows in sorted(index.items())
         if len([r for r in rows if not r.get("yanked")]) >= 2), None)
    assert target, "the registry offers no package with two live versions"
    live = [r["version"] for r in index[target] if not r.get("yanked")]

    def core(version: str) -> tuple[int, int, int]:
        head = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
        return tuple(int(g) for g in head.groups()) if head else (0, 0, 0)

    highest = max(live, key=core)
    lowest = min(live, key=core)
    assert core(highest) != core(lowest), "the candidates do not differ in version order"
    resolution = _run_requests(_requests([target], constraint=">=0.0.0"))[2]
    chosen = resolution[target][0]["chosen_version"]
    assert chosen in live, chosen
    assert core(chosen) == core(lowest), (
        f"selection took {chosen}; the governed direction is the lowest satisfying "
        f"version, not the highest ({highest})")


# --------------------------------------------------------------------------
# The duplicate-request keep (#REG-7102/#REG-7142) and the policy boundary
# --------------------------------------------------------------------------
_DUPE_REGISTRY = {
    "crypto-box": [
        {"version": "1.0.0", "yanked": False, "deps": []},
        {"version": "1.5.0", "yanked": False, "deps": []},
        {"version": "2.0.0", "yanked": False, "deps": []},
    ],
}


def _dupe_row(rid, constraint, source="app", note=""):
    return {"request_id": rid, "package": "crypto-box", "source": source,
            "channel": "stable", "constraint": constraint, "note": note}


def test_a_duplicate_request_keeps_the_most_specific_constraint():
    """#REG-7102, with the bare version #REG-7106 calls an exact ==.

    Neither graded request set holds a duplicate (channel, package, source), so
    nothing else exercises the keep at all: a resolver that skipped the whole
    stage matches both sealed fixtures. A bare version outranks a range here, so
    a specificity table that only recognises written operators keeps the wrong
    row and resolves a version lower than the one the board's rule selects.
    """
    rows = [_dupe_row("d-1", ">=1.0.0"), _dupe_row("d-2", "1.5.0")]
    _, summary, resolution, _ = _staged_run(rows, _DUPE_REGISTRY)
    assert summary["raw_request_count"] == 2
    assert summary["canonical_request_count"] == 1, "the duplicate pair was not reduced to one request"
    assert resolution["crypto-box"][0]["chosen_version"] == "1.5.0"


def test_a_specificity_tie_keeps_the_lexicographically_smaller_constraint():
    """#REG-7142 reverses the #REG-7109 draft, and only for this comparison.

    Both constraints rank the same, so the tie-break decides which survives and
    with it which version the run selects. The reversed draft keeps `>=1.5.0`
    and resolves 1.5.0.
    """
    rows = [_dupe_row("t-1", ">=1.5.0"), _dupe_row("t-2", ">=1.0.0")]
    _, summary, resolution, _ = _staged_run(rows, _DUPE_REGISTRY)
    assert summary["canonical_request_count"] == 1
    assert resolution["crypto-box"][0]["chosen_version"] == "1.0.0", (
        "the specificity tie kept the lexicographically larger constraint")


def test_the_source_coercion_decides_which_requests_are_duplicates():
    """`source` is coerced like a package name, and the duplicate key uses it.

    Nothing else here can see the source coercion: the field never reaches an
    output. It is visible only through the duplicate key, where two spellings of
    one source collapse into a single request.
    """
    rows = [_dupe_row("s-1", ">=1.0.0", source="  App.  "),
            _dupe_row("s-2", ">=1.0.0", source="app")]
    _, summary, _resolution, _ = _staged_run(rows, _DUPE_REGISTRY)
    assert summary["raw_request_count"] == 2
    assert summary["canonical_request_count"] == 1, (
        "two spellings of one source were treated as separate requests")
    assert summary["unique_request_ids"] == 2


_YANKED_STRING_REGISTRY = {
    "crypto-box": [
        {"version": "1.0.0", "yanked": "no", "deps": []},
        {"version": "1.5.0", "yanked": "true", "deps": []},
        {"version": "2.0.0", "yanked": False, "deps": []},
    ],
}


def test_a_string_yanked_flag_is_coerced_as_the_contract_states():
    """report_spec.json rules on `yanked` strings; plain truthiness gets both wrong.

    A registry record carrying "no" is live and one carrying "true" is yanked.
    Read as raw truthiness both are yanked, which moves the selection in the
    stable lane; read as raw strings neither is, which moves it in the canary
    lane. The two lanes pin the coercion from both sides.
    """
    rows = [_dupe_row("y-1", ">=1.0.0"),
            {"request_id": "y-2", "package": "crypto-box", "source": "app",
             "channel": "canary", "constraint": ">=1.5.0", "note": ""}]
    _, _summary, resolution, _ = _staged_run(rows, _YANKED_STRING_REGISTRY)
    by_channel = {e["channel"]: e for e in resolution["crypto-box"]}
    assert by_channel["stable"]["chosen_version"] == "1.0.0", '"no" is not a yanked release'
    assert by_channel["stable"]["used_yanked"] is False
    assert by_channel["canary"]["chosen_version"] == "2.0.0", '"true" is a yanked release'
    assert by_channel["canary"]["used_yanked"] is False


_EXEMPTION_REGISTRY = {
    "hot-fix": [
        {"version": "1.0.0", "yanked": True, "deps": []},
        {"version": "2.0.0", "yanked": False, "deps": []},
    ],
}


def test_policy_channel_names_are_canonicalised_before_they_are_matched():
    """A channel name in the policy is coerced like the one on a request.

    The shipped policy spells every channel canonically, so the graded run cannot
    tell a coerced lookup from a raw one. Matching the key raw drops the entry for
    any spelling an operator wrote differently, and with it the channel's
    pre-release admission, which quietly changes the selection instead of failing.
    """
    registry = {"edgekit": [
        {"version": "1.0.0-rc.1", "yanked": False, "deps": []},
        {"version": "2.0.0", "yanked": False, "deps": []},
    ]}
    rows = [{"request_id": "ch-1", "package": "edgekit", "source": "app",
             "channel": "  CANARY  ", "constraint": ">=1.0.0-rc.1", "note": ""}]

    def patch(policy):
        policy["channel_priorities"] = {"  Canary ": {"allow_prerelease": True, "priority": 2}}

    _, _, resolution, _ = _staged_run(rows, registry, patch)
    entry = resolution["edgekit"][0]
    assert entry["chosen_version"] == "1.0.0-rc.1", (
        "the channel's pre-release admission was lost to a raw key match", entry)
    assert entry["is_prerelease"] is True


def test_a_reselect_reports_the_alternatives_that_are_still_admissible():
    """#REG-7156 reports the candidates admissible as the constraints finally stand.

    A package resolved once under a loose constraint and met again under a tighter
    one keeps its version where that version still satisfies both. The alternatives
    it reports must be recomputed against the tightened set: the reference built
    that list into a copy and threw it away, so the entry went out naming versions
    the final constraints no longer admit.
    """
    registry = {"netcore": [
        {"version": "1.0.0", "yanked": False, "deps": []},
        {"version": "1.4.0", "yanked": False, "deps": []},
        {"version": "2.0.0", "yanked": False, "deps": []},
        {"version": "3.0.0", "yanked": False, "deps": []},
    ]}
    # the same package asked for twice in one channel from two sources: the second
    # request tightens the set after the first has already resolved it
    rows = [
        {"request_id": "r-1", "package": "netcore", "source": "app",
         "channel": "stable", "constraint": ">=1.0.0", "note": ""},
        {"request_id": "r-2", "package": "netcore", "source": "svc",
         "channel": "stable", "constraint": "<2.0.0", "note": ""},
    ]
    _, _, resolution, _ = _staged_run(rows, registry)
    entry = resolution["netcore"][0]
    assert entry["chosen_version"] == "1.0.0", entry
    admissible = {"1.0.0", "1.4.0"}
    reported = set(entry["alternatives_considered"])
    assert reported <= admissible - {entry["chosen_version"]}, (
        "the entry reports alternatives the tightened constraints no longer admit",
        sorted(reported),
    )


def test_policy_package_names_are_canonicalised_before_they_are_matched():
    """A package name in the policy is a package name, and is coerced as one.

    The shipped policy spells every name canonically, so the graded run cannot
    tell a canonicalised lookup from a raw one. Matching the exemption list raw
    silently drops the exemption for any name the operator wrote differently,
    which quietly changes the selection instead of failing.
    """
    rows = [{"request_id": "x-1", "package": "  Hot.Fix  ", "source": "app",
             "channel": "stable", "constraint": ">=1.0.0", "note": ""}]

    def patch(policy):
        policy["yanked_exemptions"] = ["Hot_Fix"]

    _, _summary, resolution, _ = _staged_run(rows, _EXEMPTION_REGISTRY, patch)
    entry = resolution["hot-fix"][0]
    assert entry["used_yanked"] is True and entry["chosen_version"] == "1.0.0", (
        "the exemption was not matched against the canonical package name", entry)
