"""Verifier tests for the package-registry dependency-resolution reconciler."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import os
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
LOG_PATH = Path("/app/incident/registry_governance_log.md")
EXPECTED_FIXTURE = Path("/tests/fixtures/expected_report.json")
ALT_INPUT = Path("/tests/fixtures/alt_requests.json")

STATUS_ORDER = ["resolved", "pinned", "conflict"]
RELEASE_FIELDS = ("version", "yanked", "deps")

FIXTURE = json.loads(EXPECTED_FIXTURE.read_text())
SPEC = json.loads(SPEC_PATH.read_text())

POLICY_FIELDS = (
    "reselect_cap", "prerelease_rank_floor", "plan_capacity_cap", "conflict_weight", "alt_report_cap",
)
BASELINE = {
    "reselect_cap": 2, "prerelease_rank_floor": 3, "plan_capacity_cap": 3,
    "conflict_weight": 5, "alt_report_cap": 4,
}

RESOLUTION_KEYS = set(SPEC["resolution_json"]["required_fields"])
PLAN_KEYS = set(SPEC["install_plan"]["required_fields"])
SUMMARY_KEYS = set(SPEC["summary_json"]["required_fields"])
PROVENANCE_ENUM = set(SPEC["field_types"]["provenance"]["enum"])
REASON_ENUM = set(SPEC["field_types"]["reason"]["enum"])


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


# --- verifier execution isolation -------------------------------------------------
# The submitted /app/workflow/resolver.py is untrusted once the separate verifier runs it.
# We execute it under an unprivileged UID (65534 / nobody) via setpriv, so it cannot write the
# reward path, read the held-out fixtures under /tests, or interfere with the verifier. Inputs are
# staged into a candidate-writable work area; registry/policy files under /app keep their fixed paths.
_CWORK = Path("/candidate-work")
_run_ctr = itertools.count()
_SETPRIV = ["setpriv", "--reuid=65534", "--regid=65534", "--clear-groups", "--no-new-privs"]
_RUN_TIMEOUT_SEC = 300

# The submitted program gets a minimal explicit environment rather than inheriting the verifier's
# (PATH/PYTHONPATH/CI variables and any other grader context).
_CANDIDATE_ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/candidate-work", "LANG": "C.UTF-8"}


def _candidate_dir() -> Path:
    d = _CWORK / f"run-{next(_run_ctr)}"
    d.mkdir(parents=True, exist_ok=True)
    os.chmod(d, 0o777)
    return d


def _run_agent(argv, cwd: Path):
    """Run the submitted program under the unprivileged candidate UID with a scrubbed environment."""
    return subprocess.run(
        _SETPRIV + argv, check=True, capture_output=True, text=True, cwd=str(cwd),
        env=dict(_CANDIDATE_ENV), timeout=_RUN_TIMEOUT_SEC,
    )


def _run_pipeline(tmp_path: Path, script_path: Path = WORKFLOW_PATH, input_path: Path = DEFAULT_INPUT):
    work = _candidate_dir()
    out_dir = work / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o777)
    staged_input = work / "input.json"
    shutil.copy(str(input_path), str(staged_input))
    os.chmod(staged_input, 0o644)
    result = _run_agent(
        [sys.executable, str(script_path), "--input", str(staged_input), "--output-dir", str(out_dir)],
        cwd=work,
    )
    assert result.returncode == 0
    summary = _load_json(out_dir / "summary.json")
    resolution = _load_json(out_dir / "resolution.json")
    plan = _load_jsonl(out_dir / "install_plan.jsonl")
    return out_dir, summary, resolution, plan


@pytest.fixture(scope="session")
def primary_outputs(tmp_path_factory):
    return _run_pipeline(tmp_path_factory.mktemp("primary"))


# --------------------------------------------------------------------------
# Step 1: the truncated registry index must be recovered in place
# --------------------------------------------------------------------------
def _naive_concatenation() -> dict:
    """The superseded draft merge: snapshot plus every journal entry appended to the end of its
    package's release list, bookkeeping fields left on and retractions ignored."""
    index = {pkg: [dict(r) for r in rows] for pkg, rows in _load_json(SNAPSHOT_PATH).items()}
    for entry in sorted(_load_json(JOURNAL_PATH), key=lambda e: e["journal_seq"]):
        index.setdefault(entry["package"], []).append(dict(entry))
    return index


def test_recovery_sources_are_intact():
    assert _load_json(SNAPSHOT_PATH) == FIXTURE["snapshot"]
    assert _load_json(JOURNAL_PATH) == FIXTURE["journal"]


def test_registry_index_recovered():
    """/app/data/registry_index.json shipped truncated; it must hold the recovered index."""
    recovered = _load_json(REGISTRY_PATH)
    assert isinstance(recovered, dict)
    assert recovered == FIXTURE["recovered_index"]


def test_recovered_records_carry_no_journal_bookkeeping():
    for rows in _load_json(REGISTRY_PATH).values():
        for record in rows:
            assert set(record) == set(RELEASE_FIELDS)


def test_shipped_and_naive_indexes_differ_from_the_recovered_one():
    """The recovery is real work: neither the truncated file nor the draft merge match."""
    expected = FIXTURE["recovered_index"]
    assert FIXTURE["shipped_truncated_index"] != expected
    assert _load_json(SNAPSHOT_PATH) != expected
    assert _naive_concatenation() != expected


def test_resolver_output_depends_on_the_recovered_index(tmp_path: Path):
    """Even a correctly repaired resolver emits wrong artifacts on a wrongly merged index."""
    expected = (
        FIXTURE["primary"]["summary"],
        FIXTURE["primary"]["resolution"],
        FIXTURE["primary"]["plan_rows"],
    )
    original = REGISTRY_PATH.read_text(encoding="utf-8")
    try:
        for label, index in (
            ("truncated", FIXTURE["shipped_truncated_index"]),
            ("snapshot_only", _load_json(SNAPSHOT_PATH)),
            ("naive_concatenation", _naive_concatenation()),
        ):
            _write_json(REGISTRY_PATH, index)
            _, summary, resolution, plan = _run_pipeline(tmp_path / label)
            assert (summary, resolution, plan) != expected, label
            assert resolution != FIXTURE["primary"]["resolution"], label
    finally:
        REGISTRY_PATH.write_text(original, encoding="utf-8")


# --------------------------------------------------------------------------
# Step 2: the resolver output contract
# --------------------------------------------------------------------------
def test_cli_exists():
    assert WORKFLOW_PATH.exists()


def test_output_dir_contains_exactly_three_files(primary_outputs):
    out_dir, _, _, _ = primary_outputs
    names = sorted(p.name for p in out_dir.iterdir() if p.is_file())
    assert names == ["install_plan.jsonl", "resolution.json", "summary.json"]


def test_primary_summary_matches_fixture(primary_outputs):
    _, summary, _, _ = primary_outputs
    assert summary == FIXTURE["primary"]["summary"]


def test_primary_resolution_matches_fixture(primary_outputs):
    _, _, resolution, _ = primary_outputs
    assert resolution == FIXTURE["primary"]["resolution"]


def test_primary_plan_matches_fixture(primary_outputs):
    _, _, _, plan = primary_outputs
    assert plan == FIXTURE["primary"]["plan_rows"]


def test_summary_schema(primary_outputs):
    _, summary, _, _ = primary_outputs
    assert set(summary) == SUMMARY_KEYS
    assert summary["schema_version"] == "reg-resolve-v1"
    assert list(summary["status_counts"]) == STATUS_ORDER
    for name in summary["cyclic_packages"]:
        assert name.count("/") == 1
    assert summary["cyclic_packages"] == sorted(summary["cyclic_packages"])


def test_resolution_schema_and_sorting(primary_outputs):
    _, _, resolution, _ = primary_outputs
    assert list(resolution) == sorted(resolution)
    for pkg_entries in resolution.values():
        channels = [row["channel"] for row in pkg_entries]
        assert channels == sorted(channels)
        for row in pkg_entries:
            assert set(row) == RESOLUTION_KEYS
            assert row["status"] in STATUS_ORDER
            assert row["provenance"] in PROVENANCE_ENUM
            assert row["reason"] in REASON_ENUM
            assert row["dep_edges"] == sorted(set(row["dep_edges"]))
            assert row["dep_count"] == len(row["dep_edges"])
            assert row["satisfied_constraints"] == sorted(row["satisfied_constraints"])
            assert row["alternatives_count"] == len(row["alternatives_considered"])
            if row["status"] == "conflict":
                assert row["chosen_version"] is None or isinstance(row["chosen_version"], str)


def test_plan_required_fields(primary_outputs):
    _, _, _, plan = primary_outputs
    for idx, row in enumerate(plan):
        assert set(row) == PLAN_KEYS
        assert row["status"] in STATUS_ORDER
        assert row["provenance"] in PROVENANCE_ENUM
        assert row["reason"] in REASON_ENUM
        assert row["order_index"] == idx
        assert isinstance(row["cyclic"], bool)
        if row["cyclic"]:
            assert row["reason"] == "cycle-break"


def test_install_plan_jsonl_compact(primary_outputs):
    out_dir, _, _, _ = primary_outputs
    for line in (out_dir / "install_plan.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        assert ": " not in line
        assert json.dumps(json.loads(line), separators=(",", ":")) == line


def test_summary_math_consistency(primary_outputs):
    _, summary, resolution, plan = primary_outputs
    entries = [e for rows in resolution.values() for e in rows]
    assert summary["resolved_package_count"] == len(entries)
    assert summary["total_reselects"] == sum(e["reselect_count"] for e in entries)
    assert summary["total_alternatives_considered"] == sum(e["alternatives_count"] for e in entries)
    assert summary["conflict_count"] == sum(1 for e in entries if e["status"] == "conflict")
    assert summary["planned_install_count"] == len(plan)
    assert summary["cyclic_package_count"] == len(summary["cyclic_packages"])
    for row in plan:
        if row["cyclic"]:
            assert f"{row['channel']}/{row['package']}" in summary["cyclic_packages"]
    for field in ("reselect_count", "dep_count", "alternatives_count"):
        assert summary["max_" + field] == max((r[field] for r in plan), default=0)


def test_summary_request_counts_track_the_input(primary_outputs):
    _, summary, _, _ = primary_outputs
    requests = _load_json(DEFAULT_INPUT)
    assert summary["raw_request_count"] == len(requests)
    assert summary["unique_request_ids"] == len({r["request_id"] for r in requests})


def test_status_counts_enumerate_all_three(primary_outputs):
    _, summary, resolution, _ = primary_outputs
    counts = {s: 0 for s in STATUS_ORDER}
    for rows in resolution.values():
        for e in rows:
            counts[e["status"]] += 1
    assert summary["status_counts"] == counts
    assert set(summary["status_counts"]) == set(STATUS_ORDER)


# --------------------------------------------------------------------------
# Original / broken snapshot
# --------------------------------------------------------------------------
def test_original_snapshot_preserved():
    assert ORIGINAL_WORKFLOW_PATH.exists()
    digest = hashlib.sha256(ORIGINAL_WORKFLOW_PATH.read_bytes()).hexdigest()
    assert digest == FIXTURE["broken_pipeline_sha256"]


def test_broken_snapshot_is_wrong(tmp_path: Path):
    # The frozen broken snapshot must produce results that differ from the correct reference.
    # Its exact output is intentionally not pinned: the shipped broken resolver is not order-stable,
    # and this check only needs to confirm the shipped state is wrong, not reproduce its wrongness.
    _, broken_summary, _, broken_plan = _run_pipeline(tmp_path, script_path=ORIGINAL_WORKFLOW_PATH)
    assert broken_plan != FIXTURE["primary"]["plan_rows"]
    assert broken_summary != FIXTURE["primary"]["summary"]


# --------------------------------------------------------------------------
# Generalization / idempotency / CLI
# --------------------------------------------------------------------------
def test_pipeline_rerun_idempotent(tmp_path: Path):
    _, sa, ra, pa = _run_pipeline(tmp_path / "a")
    _, sb, rb, pb = _run_pipeline(tmp_path / "b")
    assert (sa, ra, pa) == (sb, rb, pb)


def test_pipeline_supports_alternate_input(tmp_path: Path):
    _, summary, resolution, plan = _run_pipeline(tmp_path, input_path=ALT_INPUT)
    assert summary == FIXTURE["alternate"]["summary"]
    assert resolution == FIXTURE["alternate"]["resolution"]
    assert plan == FIXTURE["alternate"]["plan_rows"]


def test_cli_defaults_work_and_match_explicit_run(tmp_path: Path):
    _, explicit_summary, _, _ = _run_pipeline(tmp_path)
    # The no-argument run writes to the default /app/output; clear any root-owned artifacts from
    # solve.sh and make the dir candidate-writable so the unprivileged program can populate it.
    default_out = Path("/app/output")
    shutil.rmtree(default_out, ignore_errors=True)
    default_out.mkdir(parents=True, exist_ok=True)
    os.chmod(default_out, 0o777)
    _run_agent([sys.executable, str(WORKFLOW_PATH)], cwd=_candidate_dir())
    assert _load_json(default_out / "summary.json") == explicit_summary


def test_submitted_program_runs_unprivileged_and_cannot_write_reward(tmp_path: Path):
    """The isolation itself works: code run the way the verifier runs the agent is unprivileged
    (uid 65534) and cannot write the reward path."""
    # Ensure the reward path exists and is root-owned (as it is under test.sh) before probing.
    os.makedirs("/logs/verifier", exist_ok=True)
    reward = Path("/logs/verifier/reward.txt")
    if not reward.exists():
        reward.write_text("0")
    os.chmod("/logs/verifier", 0o755)
    os.chmod(reward, 0o644)
    probe = _candidate_dir() / "probe.py"
    probe.write_text(
        "import os\n"
        "print(os.getuid())\n"
        "open('/logs/verifier/reward.txt', 'w').write('1')\n",
        encoding="utf-8",
    )
    os.chmod(probe, 0o644)
    res = subprocess.run(
        _SETPRIV + [sys.executable, str(probe)],
        capture_output=True, text=True, cwd=str(_CWORK), check=False,
    )
    assert res.stdout.strip().splitlines()[0] == "65534", "submitted program must run as uid 65534"
    assert res.returncode != 0 and "Permission denied" in res.stderr, (
        "unprivileged submitted program must not be able to write the reward path"
    )


# --------------------------------------------------------------------------
# Source-path influence
# --------------------------------------------------------------------------
def test_registry_source_path_affects_output(tmp_path: Path):
    original = REGISTRY_PATH.read_text(encoding="utf-8")
    try:
        _, summary_a, _, plan_a = _run_pipeline(tmp_path / "a")
        REGISTRY_PATH.write_text("{}\n", encoding="utf-8")
        _, summary_b, _, plan_b = _run_pipeline(tmp_path / "b")
        assert summary_a["conflict_count"] < summary_b["conflict_count"]
        assert summary_b["planned_install_count"] == 0
        assert plan_a != plan_b
    finally:
        REGISTRY_PATH.write_text(original, encoding="utf-8")


def test_policy_source_path_affects_output(tmp_path: Path):
    original = POLICY_PATH.read_text()
    try:
        data = json.loads(original)
        data["default"]["plan_capacity_cap"] = 0
        POLICY_PATH.write_text(json.dumps(data, indent=2) + "\n")
        _, summary, _, plan = _run_pipeline(tmp_path / "shifted")
        assert summary != FIXTURE["primary"]["summary"]
        assert len(plan) == 0
    finally:
        POLICY_PATH.write_text(original)


# --------------------------------------------------------------------------
# Policy resolution
# --------------------------------------------------------------------------
def _resolve(package: str, data: dict) -> dict:
    base = dict(BASELINE)
    base.update({k: int(v) for k, v in data.get("default", {}).items() if k in BASELINE})
    override = data.get("package_overrides", {}).get(package)
    if isinstance(override, dict):
        base.update({k: int(v) for k, v in override.items() if k in BASELINE})
    return base


def test_sparse_override_inherits_remaining_fields():
    data = json.loads(POLICY_PATH.read_text())
    overrides = data.get("package_overrides", {})
    sparse = [p for p, o in overrides.items() if len(o) == 1]
    assert sparse, "the shipped policy must exercise a single-field override"
    default_resolved = _resolve("__absent__", data)
    for package in sparse:
        resolved = _resolve(package, data)
        named = next(iter(overrides[package]))
        assert resolved[named] == int(overrides[package][named])
        for field in POLICY_FIELDS:
            if field != named:
                assert resolved[field] == default_resolved[field]


def test_policy_default_may_omit_fields_and_falls_back_to_baseline():
    data = json.loads(POLICY_PATH.read_text())
    omitted = [f for f in POLICY_FIELDS if f not in data.get("default", {})]
    assert omitted, "the shipped policy must omit at least one field to exercise fallback"
    resolved = _resolve("__absent__", data)
    for field in omitted:
        assert resolved[field] == BASELINE[field]


def test_alt_report_cap_respected(primary_outputs):
    _, _, resolution, _ = primary_outputs
    data = json.loads(POLICY_PATH.read_text())
    for pkg, rows in resolution.items():
        cap = _resolve(pkg, data)["alt_report_cap"]
        for row in rows:
            assert row["alternatives_count"] <= cap


def test_reselect_count_respects_resolved_cap(primary_outputs):
    _, _, resolution, _ = primary_outputs
    data = json.loads(POLICY_PATH.read_text())
    for pkg, rows in resolution.items():
        cap = _resolve(pkg, data)["reselect_cap"]
        for row in rows:
            if row["status"] != "conflict":
                assert row["reselect_count"] <= cap


# --------------------------------------------------------------------------
# Capacity cap
# --------------------------------------------------------------------------
def test_capacity_cap_applied_after_ordering(primary_outputs):
    _, _, resolution, plan = primary_outputs
    data = json.loads(POLICY_PATH.read_text())
    cap = _resolve("__default__", data)["plan_capacity_cap"]
    per_channel: dict[str, int] = {}
    for row in plan:
        per_channel[row["channel"]] = per_channel.get(row["channel"], 0) + 1
    assert per_channel
    assert max(per_channel.values()) <= cap, f"channel exceeded cap: {per_channel}"
    installable = sum(
        1 for rows in resolution.values() for e in rows if e["status"] in {"resolved", "pinned"}
    )
    assert installable > len(plan), "fixture must contain more installable packages than the cap allows"
    seen_order = [r["channel"] for r in plan]
    for channel in per_channel:
        idxs = [i for i, c in enumerate(seen_order) if c == channel]
        assert idxs == sorted(idxs)


# --------------------------------------------------------------------------
# Deviation from standard semver / pip resolution
# --------------------------------------------------------------------------
def _run_with_registry(tmp_path: Path, registry: dict, policy: dict, requests: list):
    reg_orig = REGISTRY_PATH.read_text(encoding="utf-8")
    pol_orig = POLICY_PATH.read_text(encoding="utf-8")
    try:
        _write_json(REGISTRY_PATH, registry)
        _write_json(POLICY_PATH, policy)
        input_path = tmp_path / "req.json"
        _write_json(input_path, requests)
        return _run_pipeline(tmp_path / "run", input_path=input_path)
    finally:
        REGISTRY_PATH.write_text(reg_orig, encoding="utf-8")
        POLICY_PATH.write_text(pol_orig, encoding="utf-8")


def test_standard_semver_resolution_produces_wrong_answers(tmp_path: Path):
    """Governance selects the version standard semver/pip would not: the two disagree, so a semver
    delegate is wrong."""
    registry = {
        "leftpad": [
            {"version": "1.0.0", "yanked": False, "deps": []},
            {"version": "1.1.0", "yanked": False, "deps": []},
            {"version": "1.2.0", "yanked": False, "deps": []},
        ],
    }
    policy = {"default": {}, "package_overrides": {}, "pins": {}, "yanked_exemptions": [],
              "selection_overrides": [], "channel_priorities": {}}
    requests = [{"request_id": "d1", "package": "leftpad", "source": "app",
                 "channel": "stable", "constraint": ">=1.0.0", "note": "dev"}]
    _, _, resolution, _ = _run_with_registry(tmp_path, registry, policy, requests)
    chosen = resolution["leftpad"][0]["chosen_version"]

    # The standard semver / pip pick is the largest satisfying version.
    semver_pick = max(["1.0.0", "1.1.0", "1.2.0"], key=lambda v: tuple(int(x) for x in v.split(".")))
    assert semver_pick == "1.2.0"
    assert chosen == "1.0.0"
    assert chosen != semver_pick


def test_build_metadata_is_precedence_significant(tmp_path: Path):
    """Governance treats +buildN as significant; semver ignores it entirely. Under a policy selection
    override the build7 release outranks both the build3 release and the bare release."""
    registry = {
        "cryptobox": [
            {"version": "2.0.0", "yanked": False, "deps": []},
            {"version": "2.0.0+build3", "yanked": False, "deps": []},
            {"version": "2.0.0+build7", "yanked": False, "deps": []},
        ],
    }
    policy = {"default": {}, "package_overrides": {}, "pins": {}, "yanked_exemptions": [],
              "selection_overrides": ["cryptobox"], "channel_priorities": {}}
    requests = [{"request_id": "d2", "package": "cryptobox", "source": "app",
                 "channel": "stable", "constraint": ">=2.0.0", "note": "crypto"}]
    _, _, resolution, _ = _run_with_registry(tmp_path, registry, policy, requests)
    assert resolution["cryptobox"][0]["chosen_version"] == "2.0.0+build7"


def test_yanked_and_prerelease_gates_deviate(tmp_path: Path):
    """A yanked-only package resolves only via the exemption; a pre-release is admitted only when the
    channel allows it and it clears the maturity floor -- both deviate from a plain semver resolver."""
    registry = {
        "hot": [{"version": "1.0.0", "yanked": True, "deps": []}],
        "beta-lib": [
            {"version": "1.0.0", "yanked": False, "deps": []},
            {"version": "2.0.0-rc1", "yanked": False, "deps": []},
        ],
    }
    policy = {"default": {}, "package_overrides": {}, "pins": {}, "yanked_exemptions": ["hot"],
              "selection_overrides": ["beta-lib"],
              "channel_priorities": {"canary": {"allow_prerelease": True}}}
    requests = [
        {"request_id": "y1", "package": "hot", "source": "app", "channel": "canary", "constraint": "*", "note": "y"},
        {"request_id": "y2", "package": "beta-lib", "source": "app", "channel": "canary", "constraint": ">=1.0.0", "note": "b"},
    ]
    _, _, resolution, _ = _run_with_registry(tmp_path, registry, policy, requests)
    hot = resolution["hot"][0]
    assert hot["chosen_version"] == "1.0.0" and hot["used_yanked"] is True
    assert hot["reason"] == "yanked-admitted;default-selection"
    beta = resolution["beta-lib"][0]
    assert beta["chosen_version"] == "2.0.0-rc1" and beta["is_prerelease"] is True
    assert beta["provenance"] == "override-selection"


def test_cycles_are_non_fatal(tmp_path: Path):
    registry = {
        "svc-a": [{"version": "1.0.0", "yanked": False,
                   "deps": [{"package": "svc-b", "constraint": ">=1.0.0"}]}],
        "svc-b": [{"version": "1.0.0", "yanked": False,
                   "deps": [{"package": "svc-a", "constraint": ">=1.0.0"}]}],
    }
    policy = {"default": {"plan_capacity_cap": 5}, "package_overrides": {}, "pins": {},
              "yanked_exemptions": [], "selection_overrides": [], "channel_priorities": {}}
    requests = [{"request_id": "c1", "package": "svc-a", "source": "app",
                 "channel": "stable", "constraint": "*", "note": "cycle"}]
    _, summary, _, plan = _run_with_registry(tmp_path, registry, policy, requests)
    assert summary["cyclic_package_count"] >= 1
    assert any(r["cyclic"] for r in plan)
    assert all(r["reason"] == "cycle-break" for r in plan if r["cyclic"])


# --------------------------------------------------------------------------
# Anti-delegation: static AST ban + proof the dialect deviates
# --------------------------------------------------------------------------
def test_reconciler_does_not_import_resolver_libraries():
    tree = ast.parse(WORKFLOW_PATH.read_text(encoding="utf-8"))
    banned = set(SPEC["workflow_repair"]["prohibited_imports"])
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    offending = banned & found
    assert not offending, f"reconciler must not delegate to a semver/pip resolver: {offending}"


def test_ast_check_catches_packaging_importing_engine(tmp_path: Path):
    """The AST ban is real: a packaging/semantic_version delegate is detected."""
    shim = tmp_path / "delegating_engine.py"
    shim.write_text(
        "import packaging.version\nimport semantic_version\n\n\n"
        "def run(a, b):\n    return packaging.version.Version('1.0')\n"
    )
    tree = ast.parse(shim.read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    banned = set(SPEC["workflow_repair"]["prohibited_imports"])
    assert banned & imported == {"packaging", "semantic_version"}


# --------------------------------------------------------------------------
# Sources stay operational
# --------------------------------------------------------------------------
def test_governance_log_present():
    assert LOG_PATH.exists() and LOG_PATH.stat().st_size > 0


def test_pipeline_does_not_reference_test_artifacts():
    code = WORKFLOW_PATH.read_text(encoding="utf-8")
    for token in ("/tests", "expected_report.json", "alt_requests.json"):
        assert token not in code
