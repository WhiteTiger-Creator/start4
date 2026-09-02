#!/usr/bin/env python3
"""Package-registry dependency-resolution reconciler (INCIDENT SNAPSHOT — DO NOT SHIP).

This is the reconciler as it stood after the failed registry-migration rollout.
It still evaluates several stages against the February draft proposals and the
March interim decisions that the registry governance board later reversed, so
the install plan it produces is wrong. Restore it to the board's final decisions
recorded in /app/incident/registry_governance_log.md.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

DEFAULT_INPUT = "/app/data/requests.json"
DEFAULT_OUTPUT_DIR = "/app/output"
REGISTRY_PATH = "/app/data/registry_index.json"
POLICY_PATH = "/app/data/resolution_policy.json"

SCHEMA_VERSION = "reg-resolve-v1"
STATUS_ORDER = ["resolved", "pinned", "conflict"]

MATURITY = {"dev": 0, "alpha": 1, "beta": 2, "rc": 3, "ga": 4}
GA_RANK = 4
MAX_PASSES = 64

POLICY_BASELINE = {
    "reselect_cap": 2,
    "prerelease_rank_floor": 3,
    "plan_capacity_cap": 3,
    "conflict_weight": 5,
    "alt_report_cap": 4,
}


def canon_name(value: object) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[._]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text if text else "unknown"


def collapse_ws(value: object) -> str:
    return " ".join(str(value).split())


def coerce_flag(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return bool(value)


def parse_version(text: object) -> tuple[int, int, int, int, int]:
    # Splits a version string into the tuple it is ordered on.
    raw = str(text).strip()
    if "+" in raw:
        raw = raw.split("+", 1)[0]
    pre_rank = GA_RANK
    pre_num = 0
    if "-" in raw:
        core, pre = raw.split("-", 1)
        label = "".join(ch for ch in pre if ch.isalpha()).lower()
        num = "".join(ch for ch in pre if ch.isdigit())
        pre_rank = MATURITY.get(label, 0)
        pre_num = int(num) if num else 0
    else:
        core = raw
    parts = (core.split(".") + ["0", "0", "0"])[:3]
    nums = []
    for part in parts:
        digits = "".join(ch for ch in part if ch.isdigit())
        nums.append(int(digits) if digits else 0)
    major, minor, patch = nums
    return (major, minor, patch, pre_rank, pre_num)


def is_prerelease(key) -> bool:
    return key[3] < GA_RANK


_OP_RE = re.compile(r"^(==|>=|<=|~=|>|<)\s*(.+)$")


def parse_constraint(text: object) -> list[tuple[str, tuple]]:
    raw = str(text).strip()
    if raw in {"", "*", "any"}:
        return []
    clauses: list[tuple[str, tuple]] = []
    for piece in raw.split(","):
        piece = piece.strip()
        if not piece or piece in {"*", "any"}:
            continue
        match = _OP_RE.match(piece)
        if not match:
            clauses.append(("==", parse_version(piece)))
            continue
        op, ver = match.group(1), match.group(2).strip()
        if op == "~=":
            comps = [c for c in ver.split("+")[0].split("-")[0].split(".") if c != ""]
            lower = parse_version(ver)
            if len(comps) >= 3:
                upper = (lower[0], lower[1] + 1, 0, GA_RANK, 0)
            else:
                upper = (lower[0] + 1, 0, 0, GA_RANK, 0)
            clauses.append((">=", lower))
            clauses.append(("<", upper))
        else:
            clauses.append((op, parse_version(ver)))
    return clauses


def satisfies(cand: tuple, clauses) -> bool:
    for op, bound in clauses:
        if op == "==" and cand != bound:
            return False
        if op == ">=" and not cand >= bound:
            return False
        if op == ">" and not cand > bound:
            return False
        if op == "<=" and not cand <= bound:
            return False
        if op == "<" and not cand < bound:
            return False
    return True


def canonicalize_registry(raw_index: dict) -> dict[str, list[dict]]:
    reg: dict[str, list[dict]] = {}
    for raw_pkg, entries in raw_index.items():
        pkg = canon_name(raw_pkg)
        bucket = reg.setdefault(pkg, [])
        for entry in entries:
            version = str(entry.get("version", "0.0.0")).strip()
            deps = []
            for dep in entry.get("deps", []) or []:
                deps.append({"package": canon_name(dep.get("package", "")),
                             "constraint": collapse_ws(dep.get("constraint", ""))})
            deps.sort(key=lambda d: (d["package"], d["constraint"]))
            bucket.append({"package": pkg, "version": version, "key": parse_version(version),
                           "yanked": coerce_flag(entry.get("yanked", False)), "deps": deps})
    for bucket in reg.values():
        bucket.sort(key=lambda e: e["key"])
    return reg


def canonicalize_requests(raw_rows: list[dict]) -> list[dict]:
    canon = []
    for row in raw_rows:
        canon.append({
            "request_id": collapse_ws(row.get("request_id", "")),
            "package": canon_name(row.get("package", "")),
            "source": canon_name(row.get("source", "")),
            "channel": canon_name(row.get("channel", "stable")),
            "constraint": collapse_ws(row.get("constraint", "*")) or "*",
            "note": collapse_ws(row.get("note", "")),
        })
    return canon


_SPECIFICITY = {"==": 5, "~=": 4, ">=": 3, "<=": 3, ">": 2, "<": 2}


def _constraint_specificity(constraint: str) -> int:
    best = 1
    for piece in str(constraint).split(","):
        match = _OP_RE.match(piece.strip())
        if match:
            best = max(best, _SPECIFICITY.get(match.group(1), 1))
    return best


def deduplicate(canon_rows: list[dict]) -> list[dict]:
    # Collapses rows addressing the same package and channel to one.
    best: dict[tuple, tuple] = {}
    order: dict[tuple, int] = {}
    for idx, row in enumerate(canon_rows):
        dkey = (row["channel"], row["package"], row["source"])
        spec = _constraint_specificity(row["constraint"])
        sort_key = (spec, row["constraint"], len(row["note"]), -idx)
        if dkey not in best or sort_key > best[dkey]:
            best[dkey] = sort_key
            order[dkey] = idx
    keep = set(order.values())
    return [row for idx, row in enumerate(canon_rows) if idx in keep]


def _coerce_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value).strip())
    except ValueError:
        return default


def resolve_policy(package: str, policy_data: dict) -> dict:
    resolved = dict(POLICY_BASELINE)
    for field, val in policy_data.get("default", {}).items():
        if field in resolved:
            resolved[field] = _coerce_int(val)
    override = policy_data.get("package_overrides", {}).get(package)
    if isinstance(override, dict):
        for field, val in override.items():
            if field in resolved:
                resolved[field] = _coerce_int(val)
    return resolved


def candidate_versions(package, clauses, channel, registry, policy_data) -> list[dict]:
    # The registry entries admissible for this request.
    out = []
    for entry in registry.get(package, []):
        if not satisfies(entry["key"], clauses):
            continue
        if entry["yanked"]:
            continue
        if is_prerelease(entry["key"]):
            continue
        out.append(entry)
    return out


def select_entry(package, clauses, channel, registry, policy_data) -> dict:
    # Picks the entry this request resolves to.
    cands = candidate_versions(package, clauses, channel, registry, policy_data)
    if not cands:
        return {"version": None, "key": None, "status": "conflict", "provenance": "unsatisfiable",
                "reason": "no version satisfies the combined constraints", "deps": [],
                "candidates": [], "used_yanked": False, "is_prerelease": False}
    chosen = max(cands, key=lambda e: e["key"])
    return {"version": chosen["version"], "key": chosen["key"], "status": "resolved",
            "provenance": "highest-satisfying", "reason": "highest satisfying (standard resolution)",
            "deps": chosen["deps"], "candidates": [e["version"] for e in cands],
            "used_yanked": False, "is_prerelease": False}


def resolve_channel(channel, seed_constraints, seed_clause_text, registry, policy_data) -> dict[str, dict]:
    constraints = {pkg: list(clauses) for pkg, clauses in seed_constraints.items()}
    clause_text = {pkg: set(texts) for pkg, texts in seed_clause_text.items()}
    known = set(seed_constraints)
    ledger: dict[str, dict] = {}
    passes = 0
    changed = True
    while changed and passes < MAX_PASSES:
        changed = False
        passes += 1
        for pkg in sorted(known):
            res = select_entry(pkg, constraints.get(pkg, []), channel, registry, policy_data)
            res["reselect_count"] = 0
            prev = ledger.get(pkg)
            if prev is None or prev.get("version") != res["version"]:
                ledger[pkg] = res
                changed = True
            else:
                res = prev
            if res.get("version") is not None:
                for dep in res["deps"]:
                    dpkg = dep["package"]
                    if dpkg not in known:
                        known.add(dpkg)
                        constraints.setdefault(dpkg, [])
                        clause_text.setdefault(dpkg, set())
                        changed = True
                    ctext = dep["constraint"] or "*"
                    if ctext not in clause_text.setdefault(dpkg, set()):
                        clause_text[dpkg].add(ctext)
                        constraints.setdefault(dpkg, []).extend(parse_constraint(ctext))
                        changed = True
    for pkg, entry in ledger.items():
        entry["satisfied_constraints"] = sorted(clause_text.get(pkg, set()))
    return ledger


def topological_order(ledger) -> list[tuple[str, bool]]:
    # Orders the install plan over the resolved ledger.
    nodes = {p for p, r in ledger.items() if r.get("version") is not None and r["status"] in {"resolved", "pinned"}}
    deps = {}
    for pkg in nodes:
        deps[pkg] = sorted({d["package"] for d in ledger[pkg]["deps"] if d["package"] in nodes and d["package"] != pkg})
    placed: list[tuple[str, bool]] = []
    placed_set: set[str] = set()
    remaining = set(nodes)
    while remaining:
        ready = sorted(p for p in remaining if all(d in placed_set for d in deps[p]))
        if not ready:
            break
        for p in ready:
            placed.append((p, False))
            placed_set.add(p)
            remaining.discard(p)
    return placed


RESOLUTION_FIELDS = ("channel", "chosen_version", "status", "provenance", "reselect_count", "is_prerelease",
                     "used_yanked", "dep_edges", "dep_count", "satisfied_constraints", "alternatives_considered",
                     "alternatives_count", "reason")
PLAN_FIELDS = ("order_index", "channel", "package", "version", "status", "provenance", "cyclic", "dep_count",
               "dep_edges", "reselect_count", "alternatives_count", "reason")


def run(input_path: str, output_dir: str) -> None:
    raw_requests = json.loads(Path(input_path).read_text(encoding="utf-8"))
    raw_index = json.loads(Path(REGISTRY_PATH).read_text(encoding="utf-8"))
    policy_data = json.loads(Path(POLICY_PATH).read_text(encoding="utf-8"))

    registry = canonicalize_registry(raw_index)
    canon_requests = deduplicate(canonicalize_requests(raw_requests))

    channels: dict[str, dict] = {}
    for row in canon_requests:
        chan = channels.setdefault(row["channel"], {"clauses": {}, "text": {}})
        chan["clauses"].setdefault(row["package"], [])
        chan["text"].setdefault(row["package"], set())
        ctext = row["constraint"] or "*"
        if ctext not in chan["text"][row["package"]]:
            chan["text"][row["package"]].add(ctext)
            chan["clauses"][row["package"]].extend(parse_constraint(ctext))

    all_entries: list[dict] = []
    per_channel_ledger: dict[str, dict] = {}
    for channel in sorted(channels):
        ledger = resolve_channel(channel, channels[channel]["clauses"], channels[channel]["text"], registry, policy_data)
        per_channel_ledger[channel] = ledger
        for pkg, res in ledger.items():
            dep_edges = sorted({d["package"] for d in res["deps"]})
            cap = resolve_policy(pkg, policy_data)["alt_report_cap"]
            alts = sorted({v for v in res.get("candidates", []) if v != res["version"]}, key=lambda v: parse_version(v))[:cap]
            entry = {"package": pkg, "channel": channel, "chosen_version": res["version"], "status": res["status"],
                     "provenance": res["provenance"], "reselect_count": res.get("reselect_count", 0),
                     "is_prerelease": bool(res.get("is_prerelease", False)), "used_yanked": bool(res.get("used_yanked", False)),
                     "dep_edges": dep_edges, "dep_count": len(dep_edges),
                     "satisfied_constraints": res.get("satisfied_constraints", []),
                     "alternatives_considered": alts, "alternatives_count": len(alts), "reason": res["reason"]}
            all_entries.append(entry)

    plan_cap = resolve_policy("__default__", policy_data)["plan_capacity_cap"]
    ordered_rows: list[dict] = []
    cyclic_packages: list[str] = []
    for channel in sorted(per_channel_ledger):
        ledger = per_channel_ledger[channel]
        for local_idx, (pkg, cyclic) in enumerate(topological_order(ledger)):
            res = ledger[pkg]
            dep_edges = sorted({d["package"] for d in res["deps"]})
            alt_entry = next(e for e in all_entries if e["channel"] == channel and e["package"] == pkg)
            if cyclic:
                cyclic_packages.append(f"{channel}/{pkg}")
            ordered_rows.append({"channel": channel, "package": pkg, "version": res["version"], "status": res["status"],
                                 "provenance": res["provenance"], "cyclic": cyclic, "dep_count": len(dep_edges),
                                 "dep_edges": dep_edges, "reselect_count": res.get("reselect_count", 0),
                                 "alternatives_count": alt_entry["alternatives_count"],
                                 "reason": "cycle-break install" if cyclic else res["reason"], "_topo": local_idx})

    kept: dict[str, int] = {}
    plan_rows: list[dict] = []
    for row in sorted(ordered_rows, key=lambda r: (r["channel"], r["_topo"])):
        c = kept.get(row["channel"], 0)
        if c < plan_cap:
            plan_rows.append(row)
            kept[row["channel"]] = c + 1
    for idx, row in enumerate(plan_rows):
        row["order_index"] = idx
        row.pop("_topo", None)

    status_counts = {status: 0 for status in STATUS_ORDER}
    for entry in all_entries:
        status_counts[entry["status"]] += 1
    conflict_weight = resolve_policy("__default__", policy_data)["conflict_weight"]

    def pmax(field: str) -> int:
        return max((r[field] for r in plan_rows), default=0)

    summary = {
        "schema_version": SCHEMA_VERSION,
        "raw_request_count": len(raw_requests),
        "unique_request_ids": len({collapse_ws(r.get("request_id", "")) for r in raw_requests}),
        "canonical_request_count": len(canon_requests),
        "resolved_package_count": len(all_entries),
        "channel_count": len(per_channel_ledger),
        "status_counts": status_counts,
        "conflict_count": status_counts["conflict"],
        "cyclic_package_count": len(cyclic_packages),
        "cyclic_packages": sorted(cyclic_packages),
        "total_reselects": sum(e["reselect_count"] for e in all_entries),
        "total_alternatives_considered": sum(e["alternatives_count"] for e in all_entries),
        "total_conflict_weight": status_counts["conflict"] * conflict_weight,
        "planned_install_count": len(plan_rows),
        "max_reselect_count": pmax("reselect_count"),
        "max_dep_count": pmax("dep_count"),
        "max_alternatives_count": pmax("alternatives_count"),
    }

    by_package: dict[str, list[dict]] = {}
    for entry in all_entries:
        by_package.setdefault(entry["package"], []).append(entry)
    resolution = {}
    for pkg in sorted(by_package):
        rows = sorted(by_package[pkg], key=lambda e: e["channel"])
        resolution[pkg] = [{f: e[f] for f in RESOLUTION_FIELDS} for e in rows]

    out_plan = [{f: r[f] for f in PLAN_FIELDS} for r in plan_rows]

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out / "resolution.json").write_text(json.dumps(resolution, indent=2) + "\n", encoding="utf-8")
    with (out / "install_plan.jsonl").open("w", encoding="utf-8") as fh:
        for row in out_plan:
            fh.write(json.dumps(row, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Package-registry dependency-resolution reconciler")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    run(args.input, args.output_dir)


if __name__ == "__main__":
    main()
