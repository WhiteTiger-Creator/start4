#!/usr/bin/env python3
"""Package-registry dependency-resolution reconciler (governance dialect).

Computes a deterministic install plan from a dependency graph and a set of
version constraints under the registry governance board's resolution dialect.
Every resolution rule here -- the version precedence, the conflict/selection
strategy, how yanked and pre-release versions may be used, cycle handling and
the per-channel selection ledger -- is the board's own dialect and deliberately
DEVIATES from standard semver / pip resolution. It is reconstructed from
/app/incident/registry_governance_log.md, the operational data and
/app/docs/report_spec.json (output contract only).

Standard-library only. Delegating resolution to ``packaging`` /
``pip`` / ``setuptools`` / ``semantic_version`` would produce wrong answers
because the dialect deviates from semver, and is rejected by the verifier.
"""

from __future__ import annotations

import argparse
import heapq
import json
import re
from pathlib import Path

# Fixed absolute operational-input paths. --input selects the request stream
# only; the scoped policy and registry-index files never become relative to it.
DEFAULT_INPUT = "/app/data/requests.json"
DEFAULT_OUTPUT_DIR = "/app/output"
REGISTRY_PATH = "/app/data/registry_index.json"
POLICY_PATH = "/app/data/resolution_policy.json"

SCHEMA_VERSION = "reg-resolve-v1"
STATUS_ORDER = ["resolved", "pinned", "conflict"]

# --- Governance constants (final decisions; see log entries in comments) ---
# #REG-7104: governance maturity rank for pre-release labels (ga = release).
MATURITY = {"dev": 0, "alpha": 1, "beta": 2, "rc": 3, "ga": 4}
GA_RANK = 4


# Baseline resolution policy (#REG-7150). Any field the policy file omits keeps
# these values; the policy file may override per default and per package.
POLICY_BASELINE = {
    "reselect_cap": 2,
    "prerelease_rank_floor": 3,
    "plan_capacity_cap": 3,
    "conflict_weight": 5,
    "alt_report_cap": 4,
}


# --------------------------------------------------------------------------
# Canonicalization helpers (#REG-7101)
# --------------------------------------------------------------------------
def canon_name(value: object) -> str:
    text = str(value).strip().lower()
    # governance separator normalization: '_' and '.' collapse to '-'.
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


def parse_version(text: object) -> tuple[int, int, int, int, int, int]:
    """Governance version key (#REG-7104). Higher tuple sorts as the greater
    version. DEVIATES from semver: build metadata is precedence-SIGNIFICANT
    (the final tiebreaker), and pre-release labels use a fixed maturity rank."""
    raw = str(text).strip()
    build = 0
    if "+" in raw:
        raw, bmeta = raw.split("+", 1)
        digits = "".join(ch for ch in bmeta if ch.isdigit())
        build = int(digits) if digits else 0
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
    return (major, minor, patch, pre_rank, pre_num, build)


def is_prerelease(key: tuple[int, int, int, int, int, int]) -> bool:
    return key[3] < GA_RANK


# --------------------------------------------------------------------------
# Constraint parsing / satisfaction (#REG-7106)
# --------------------------------------------------------------------------
_OP_RE = re.compile(r"^(==|>=|<=|~=|>|<)\s*(.+)$")


def parse_constraint(text: object) -> list[tuple[str, tuple]]:
    """Return a list of (op, version_key) clauses ANDed together. '*'/'' -> []
    (any). '~=' expands to a governance compatible-release band."""
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
            # bare version means exact-match under the governance dialect.
            clauses.append(("==", parse_version(piece)))
            continue
        op, ver = match.group(1), match.group(2).strip()
        if op == "~=":
            comps = [c for c in ver.split("+")[0].split("-")[0].split(".") if c != ""]
            lower = parse_version(ver)
            if len(comps) >= 3:
                upper = (lower[0], lower[1] + 1, 0, GA_RANK, 0, 0)
            else:
                upper = (lower[0] + 1, 0, 0, GA_RANK, 0, 0)
            clauses.append((">=", lower))
            clauses.append(("<", upper))
        else:
            clauses.append((op, parse_version(ver)))
    return clauses


def satisfies(cand: tuple, clauses: list[tuple[str, tuple]]) -> bool:
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


# --------------------------------------------------------------------------
# Stage 1: canonicalize registry + requests (#REG-7101)
# --------------------------------------------------------------------------
def canonicalize_registry(raw_index: dict) -> dict[str, list[dict]]:
    reg: dict[str, list[dict]] = {}
    for raw_pkg, entries in raw_index.items():
        pkg = canon_name(raw_pkg)
        bucket = reg.setdefault(pkg, [])
        for entry in entries:
            version = str(entry.get("version", "0.0.0")).strip()
            deps = []
            for dep in entry.get("deps", []) or []:
                deps.append(
                    {
                        "package": canon_name(dep.get("package", "")),
                        "constraint": collapse_ws(dep.get("constraint", "")),
                    }
                )
            deps.sort(key=lambda d: (d["package"], d["constraint"]))
            bucket.append(
                {
                    "package": pkg,
                    "version": version,
                    "key": parse_version(version),
                    "yanked": coerce_flag(entry.get("yanked", False)),
                    "deps": deps,
                }
            )
    for bucket in reg.values():
        bucket.sort(key=lambda e: e["key"])
    return reg


def canonicalize_requests(raw_rows: list[dict]) -> list[dict]:
    canon = []
    for row in raw_rows:
        canon.append(
            {
                "request_id": collapse_ws(row.get("request_id", "")),
                "package": canon_name(row.get("package", "")),
                "source": canon_name(row.get("source", "")),
                "channel": canon_name(row.get("channel", "stable")),
                "constraint": collapse_ws(row.get("constraint", "*")) or "*",
                "note": collapse_ws(row.get("note", "")),
            }
        )
    return canon


# --------------------------------------------------------------------------
# Stage 2: deduplicate requests by (channel, package, source) (#REG-7102/#REG-7142)
# --------------------------------------------------------------------------
_SPECIFICITY = {"==": 5, "~=": 4, ">=": 3, "<=": 3, ">": 2, "<": 2}


def _constraint_specificity(constraint: str) -> int:
    best = 1
    for piece in str(constraint).split(","):
        piece = piece.strip()
        match = _OP_RE.match(piece)
        if match:
            best = max(best, _SPECIFICITY.get(match.group(1), 1))
    return best


def deduplicate(canon_rows: list[dict]) -> list[dict]:
    # #REG-7102 chain with the #REG-7142 reversal on the constraint tie-break:
    # keep the MOST SPECIFIC constraint; on tie keep the LEXICOGRAPHICALLY
    # SMALLER constraint string (reversed from the #REG-7109 draft); then the
    # longer note; then first-seen input order.
    best: dict[tuple, tuple] = {}
    order: dict[tuple, int] = {}
    for idx, row in enumerate(canon_rows):
        dkey = (row["channel"], row["package"], row["source"])
        spec = _constraint_specificity(row["constraint"])
        # larger tuple wins: high specificity, smaller constraint (negated via a
        # reverse comparator), longer note, earliest index (negated).
        sort_key = (spec, _NegStr(row["constraint"]), len(row["note"]), -idx)
        if dkey not in best or sort_key > best[dkey]:
            best[dkey] = sort_key
            order[dkey] = idx
    keep = set(order.values())
    return [row for idx, row in enumerate(canon_rows) if idx in keep]


class _NegStr:
    """Comparator wrapper so that the LEXICOGRAPHICALLY SMALLER string sorts as
    the greater key (used for the reversed #REG-7142 constraint tie-break)."""

    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value = value

    def __lt__(self, other: _NegStr) -> bool:
        return self.value > other.value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _NegStr) and self.value == other.value


# --------------------------------------------------------------------------
# Policy resolution (#REG-7150, #REG-7152)
# --------------------------------------------------------------------------
def _coerce_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value).strip())
    except ValueError:
        try:
            return int(float(str(value).strip()))
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


# --------------------------------------------------------------------------
# Stage 3: resolution -- candidate selection under the governance dialect
# (#REG-7104, #REG-7106, #REG-7108, #REG-7110, #REG-7120, #REG-7122)
# --------------------------------------------------------------------------
def _pin_for(channel: str, package: str, policy_data: dict) -> str | None:
    pins = policy_data.get("pins", {})
    scoped = pins.get(channel, {})
    if isinstance(scoped, dict) and package in scoped:
        return str(scoped[package]).strip()
    glob = pins.get("*", {})
    if isinstance(glob, dict) and package in glob:
        return str(glob[package]).strip()
    return None


def _channel_allows_prerelease(channel: str, policy_data: dict) -> bool:
    chan = policy_data.get("channel_priorities", {}).get(channel, {})
    return coerce_flag(chan.get("allow_prerelease", False)) if isinstance(chan, dict) else False


def candidate_versions(
    package: str,
    clauses: list[tuple[str, tuple]],
    channel: str,
    registry: dict,
    policy_data: dict,
) -> list[dict]:
    """Entries satisfying every clause under the governance admission rules
    (#REG-7120 yanked exemption, #REG-7122 pre-release channel/floor gate)."""
    yanked_ok = set(policy_data.get("yanked_exemptions", []))
    floor = resolve_policy(package, policy_data)["prerelease_rank_floor"]
    allow_pre = _channel_allows_prerelease(channel, policy_data)
    out = []
    for entry in registry.get(package, []):
        if not satisfies(entry["key"], clauses):
            continue
        if entry["yanked"] and package not in yanked_ok:
            continue
        if is_prerelease(entry["key"]) and (not allow_pre or entry["key"][3] < floor):
            continue
        out.append(entry)
    return out


def select_entry(
    package: str,
    clauses: list[tuple[str, tuple]],
    channel: str,
    registry: dict,
    policy_data: dict,
) -> dict:
    """Resolve one (channel, package) to a single entry under the dialect.

    Returns a resolution dict. Pins (#REG-7110) win absolutely. Otherwise the
    default direction is the LOWEST satisfying version (#REG-7108, conservative
    -- DEVIATES from pip/semver which take the highest); packages named in the
    governance selection_overrides list instead take the HIGHEST.
    """
    overrides = set(policy_data.get("selection_overrides", []))
    pin = _pin_for(channel, package, policy_data)
    if pin is not None:
        pin_key = parse_version(pin)
        match = next((e for e in registry.get(package, []) if e["version"] == pin), None)
        if match is None:
            # #REG-7156: alternatives are the admissible candidates other than
            # the chosen one. A pin-missing conflict chose nothing, so there is
            # nothing to exclude and every admissible candidate is reported.
            return {
                "version": None, "key": None, "status": "conflict",
                "provenance": "pin-missing", "reason": "pin-missing",
                "deps": [],
                "candidates": [e["version"] for e in candidate_versions(
                    package, clauses, channel, registry, policy_data)],
                "used_yanked": False, "is_prerelease": False,
            }
        return {
            "version": match["version"], "key": pin_key, "status": "pinned",
            "provenance": "pin-override", "reason": "pin-override",
            "deps": match["deps"],
            "candidates": [e["version"] for e in registry.get(package, [])
                           if satisfies(e["key"], clauses)],
            "used_yanked": match["yanked"], "is_prerelease": is_prerelease(pin_key),
        }

    cands = candidate_versions(package, clauses, channel, registry, policy_data)
    if not cands:
        return {
            "version": None, "key": None, "status": "conflict",
            "provenance": "unsatisfiable", "reason": "unsatisfiable",
            "deps": [], "candidates": [], "used_yanked": False, "is_prerelease": False,
        }
    take_highest = package in overrides
    chosen = max(cands, key=lambda e: e["key"]) if take_highest else min(cands, key=lambda e: e["key"])
    provenance = "override-selection" if take_highest else "default-selection"
    reason = provenance
    if chosen["yanked"]:
        reason = "yanked-admitted;" + reason
    return {
        "version": chosen["version"], "key": chosen["key"], "status": "resolved",
        "provenance": provenance, "reason": reason, "deps": chosen["deps"],
        "candidates": [e["version"] for e in cands],
        "used_yanked": chosen["yanked"], "is_prerelease": is_prerelease(chosen["key"]),
    }


# --------------------------------------------------------------------------
# Stage 5: per-channel stateful selection ledger + reselect cap
# (#REG-7116, #REG-7160)
# --------------------------------------------------------------------------
def resolve_channel(
    channel: str,
    seed_constraints: dict[str, list[tuple[str, tuple]]],
    seed_clause_text: dict[str, set[str]],
    registry: dict,
    policy_data: dict,
) -> dict[str, dict]:
    """Monotone fixpoint over one channel. Constraints only ACCUMULATE, so the
    ledger keeps a package's first chosen version for consistency and only
    RE-SELECTS (bumping reselect_count) when the held version stops satisfying
    the tightened constraint set; beyond the resolved reselect_cap the package
    freezes into a conflict (#REG-7116, #REG-7160)."""
    constraints: dict[str, list[tuple[str, tuple]]] = {
        pkg: list(clauses) for pkg, clauses in seed_constraints.items()
    }
    clause_text: dict[str, set[str]] = {
        pkg: set(texts) for pkg, texts in seed_clause_text.items()
    }
    known = set(seed_constraints)
    ledger: dict[str, dict] = {}

    # The governed resolution is a monotone fixpoint that runs until it is stable.
    # The bound below is only there so a pathological registry cannot spin forever;
    # it scales with the registry rather than sitting at a fixed 64, and running
    # into it raises instead of returning a half-propagated ledger, because a
    # silently truncated chain would be reported as a confident wrong answer.
    max_passes = len(registry) + 64
    passes = 0
    changed = True
    while changed and passes < max_passes:
        changed = False
        passes += 1
        for pkg in sorted(known):
            clauses = constraints.get(pkg, [])
            cur = ledger.get(pkg)
            if cur is not None and cur.get("frozen"):
                res = cur
            else:
                fresh = select_entry(pkg, clauses, channel, registry, policy_data)
                cap = resolve_policy(pkg, policy_data)["reselect_cap"]
                if cur is None:
                    fresh["reselect_count"] = 0
                    fresh["frozen"] = fresh["status"] == "conflict"
                    ledger[pkg] = fresh
                    res = fresh
                    changed = True
                else:
                    held_ok = (
                        cur["version"] is not None
                        and cur["key"] is not None
                        and satisfies(cur["key"], clauses)
                        and any(e["version"] == cur["version"]
                                for e in candidate_versions(pkg, clauses, channel, registry, policy_data))
                    )
                    if cur["status"] == "pinned" and cur["version"] is not None:
                        held_ok = True  # pins never re-select
                    if held_ok:
                        # The version stands, but #REG-7156 reports the alternatives
                        # admissible under the constraints as they now stand, so the
                        # candidate list is recomputed rather than carried over from
                        # when they were looser.
                        res = dict(cur)
                        res["candidates"] = [
                            e["version"] for e in candidate_versions(
                                pkg, clauses, channel, registry, policy_data)]
                    else:
                        count = cur.get("reselect_count", 0) + 1
                        if count > cap:
                            # #REG-7160: beyond the cap the package FREEZES rather
                            # than re-resolving, so the re-selection is refused and
                            # the version it was holding stands. The count records
                            # the re-selection that was refused.
                            frozen = dict(cur)
                            frozen["reselect_count"] = count
                            # Only the VERSION is held. Every field the entry
                            # reports still follows #REG-7156 against the
                            # constraints as they finally stand, so the
                            # alternatives are the admissible candidates other
                            # than the held version, not the set that was
                            # admissible when it was chosen.
                            frozen["candidates"] = [
                                e["version"] for e in candidate_versions(
                                    pkg, clauses, channel, registry, policy_data)
                            ]
                            frozen["status"] = "conflict"
                            frozen["provenance"] = "reselect-cap-exceeded"
                            frozen["reason"] = "reselect-cap-exceeded"
                            frozen["frozen"] = True
                            ledger[pkg] = frozen
                            res = frozen
                        else:
                            fresh["reselect_count"] = count
                            fresh["frozen"] = fresh["status"] == "conflict"
                            ledger[pkg] = fresh
                            res = fresh
                        changed = True
            # enqueue deps of the currently chosen version (monotone).
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
    if changed:
        raise RuntimeError(
            f"dependency ledger for channel {channel!r} did not reach a fixpoint "
            f"in {max_passes} passes")
    for pkg, entry in ledger.items():
        entry["satisfied_constraints"] = sorted(clause_text.get(pkg, set()))
    return ledger


# --------------------------------------------------------------------------
# Stage 4: install plan -- topological order + cycle handling + capacity cap
# (#REG-7145, #REG-7146, #REG-7148)
# --------------------------------------------------------------------------
def topological_order(ledger: dict[str, dict]) -> list[tuple[str, bool]]:
    """Governance install order: dependencies before dependents. Among nodes
    whose deps are all placed, the tie-break is the lexicographically smallest
    package (#REG-7145). Cycles are NON-FATAL (#REG-7148): when no node is
    installable, break the cycle by installing the lexicographically smallest
    remaining package and flag it cyclic.

    Kahn's algorithm with an unplaced-dependency counter and a heap of ready
    nodes, so the whole order costs O((V+E) log V). Rescanning every remaining
    node each round is quadratic in the resolved set and will not meet the
    runtime budget at registry scale.
    """
    nodes = {p for p, r in ledger.items() if r.get("version") is not None
             and r["status"] in {"resolved", "pinned"}}
    deps = {}
    for pkg in nodes:
        deps[pkg] = sorted({d["package"] for d in ledger[pkg]["deps"]
                            if d["package"] in nodes and d["package"] != pkg})
    dependents: dict[str, list[str]] = {p: [] for p in nodes}
    indegree = {p: len(deps[p]) for p in nodes}
    for pkg in nodes:
        for dep in deps[pkg]:
            dependents[dep].append(pkg)

    placed: list[tuple[str, bool]] = []
    remaining = set(nodes)
    # A heap, not a sorted batch. #REG-7145 picks the smallest package among those
    # whose dependencies are placed *at that moment*, so a package that becomes
    # ready partway through must be able to win against one that was ready earlier:
    # with a -> b and an independent z, the order is a, b, z and not a, z, b.
    ready = [p for p in nodes if indegree[p] == 0]
    heapq.heapify(ready)
    while remaining:
        if ready:
            pkg = heapq.heappop(ready)
            placed.append((pkg, False))
            remaining.discard(pkg)
            for child in dependents[pkg]:
                indegree[child] -= 1
                if indegree[child] == 0 and child in remaining:
                    heapq.heappush(ready, child)
        else:
            victim = min(remaining)
            placed.append((victim, True))
            remaining.discard(victim)
            for child in dependents[victim]:
                indegree[child] -= 1
                if indegree[child] == 0 and child in remaining:
                    heapq.heappush(ready, child)
    return placed


def reach_counts(ledger: dict[str, dict], order: list[tuple[str, bool]]) -> dict[str, int]:
    """#REG-7172 reach_count per package: distinct packages reachable through
    dependency edges that run to a package installed EARLIER.

    Each package's reachable set is carried as a bitmask and built once, in
    install order, by OR-ing the masks its earlier dependencies already have.
    Recomputing the reachable set per package instead is O(V*(V+E)) over the
    resolved set and cannot finish inside the runtime budget.
    """
    position = {pkg: i for i, (pkg, _) in enumerate(order)}
    bit = {pkg: 1 << i for i, (pkg, _) in enumerate(order)}
    masks: dict[str, int] = {}
    counts: dict[str, int] = {}
    for pkg, _cyclic in order:
        mask = 0
        for dep in {d["package"] for d in ledger[pkg]["deps"]}:
            if dep in position and position[dep] < position[pkg]:
                mask |= bit[dep] | masks[dep]
        masks[pkg] = mask
        counts[pkg] = mask.bit_count()
    return counts


RESOLUTION_FIELDS = (
    "channel",
    "chosen_version",
    "status",
    "provenance",
    "reselect_count",
    "is_prerelease",
    "used_yanked",
    "dep_edges",
    "dep_count",
    "satisfied_constraints",
    "alternatives_considered",
    "alternatives_count",
    "reach_count",
    "reason",
)
PLAN_FIELDS = (
    "order_index",
    "channel",
    "package",
    "version",
    "status",
    "provenance",
    "cyclic",
    "dep_count",
    "dep_edges",
    "reselect_count",
    "alternatives_count",
    "reach_count",
    "reason",
)


def run(input_path: str, output_dir: str) -> None:
    raw_requests = json.loads(Path(input_path).read_text(encoding="utf-8"))
    raw_index = json.loads(Path(REGISTRY_PATH).read_text(encoding="utf-8"))
    policy_data = json.loads(Path(POLICY_PATH).read_text(encoding="utf-8"))

    registry = canonicalize_registry(raw_index)
    canon_requests = canonicalize_requests(raw_requests)
    canon_requests = deduplicate(canon_requests)

    # Seed per-channel constraint sets from the surviving requests.
    channels: dict[str, dict] = {}
    for row in canon_requests:
        chan = channels.setdefault(row["channel"], {"clauses": {}, "text": {}})
        chan["clauses"].setdefault(row["package"], [])
        chan["text"].setdefault(row["package"], set())
        ctext = row["constraint"] or "*"
        if ctext not in chan["text"][row["package"]]:
            chan["text"][row["package"]].add(ctext)
            chan["clauses"][row["package"]].extend(parse_constraint(ctext))

    # Resolve every channel independently under its own ledger.
    all_entries: list[dict] = []
    per_channel_ledger: dict[str, dict] = {}
    for channel in sorted(channels):
        ledger = resolve_channel(
            channel, channels[channel]["clauses"], channels[channel]["text"], registry, policy_data
        )
        per_channel_ledger[channel] = ledger
        for pkg, res in ledger.items():
            dep_edges = sorted({d["package"] for d in res["deps"]})
            cap = resolve_policy(pkg, policy_data)["alt_report_cap"]
            alts = [v for v in res.get("candidates", []) if v != res["version"]]
            alts = sorted(set(alts), key=lambda v: parse_version(v))[:cap]
            entry = {
                "package": pkg,
                "channel": channel,
                "chosen_version": res["version"],
                "status": res["status"],
                "provenance": res["provenance"],
                "reselect_count": res.get("reselect_count", 0),
                "is_prerelease": bool(res.get("is_prerelease", False)),
                "used_yanked": bool(res.get("used_yanked", False)),
                "dep_edges": dep_edges,
                "dep_count": len(dep_edges),
                "satisfied_constraints": res.get("satisfied_constraints", []),
                "alternatives_considered": alts,
                "alternatives_count": len(alts),
                "reach_count": 0,
                "reason": res["reason"],
            }
            all_entries.append(entry)

    # --- install plan: topological order per channel, then capacity cap ---
    plan_cap = resolve_policy("__default__", policy_data)["plan_capacity_cap"]
    ordered_rows: list[dict] = []
    cyclic_packages: list[str] = []
    # Index the entries once; scanning the whole entry list per package is
    # quadratic in the resolved set at registry scale.
    entry_by = {(e["channel"], e["package"]): e for e in all_entries}
    for channel in sorted(per_channel_ledger):
        ledger = per_channel_ledger[channel]
        topo = topological_order(ledger)
        reach = reach_counts(ledger, topo)          # #REG-7172
        for pkg, count in reach.items():
            entry_by[(channel, pkg)]["reach_count"] = count
        for local_idx, (pkg, cyclic) in enumerate(topo):
            res = ledger[pkg]
            dep_edges = sorted({d["package"] for d in res["deps"]})
            alt_entry = entry_by[(channel, pkg)]
            if cyclic:
                cyclic_packages.append(f"{channel}/{pkg}")
            ordered_rows.append({
                "channel": channel,
                "package": pkg,
                "version": res["version"],
                "status": res["status"],
                "provenance": res["provenance"],
                "cyclic": cyclic,
                "dep_count": len(dep_edges),
                "dep_edges": dep_edges,
                "reselect_count": res.get("reselect_count", 0),
                "alternatives_count": alt_entry["alternatives_count"],
                "reach_count": reach.get(pkg, 0),
                "reason": "cycle-break" if cyclic else res["reason"],
                "_topo": local_idx,
            })

    # Capacity cap (#REG-7146): keep the first plan_capacity_cap rows per channel
    # over the topological order; the rest defer to the next reconcile cycle and
    # contribute to no plan-derived summary field.
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

    # --- summary aggregates ---
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
        "max_reach_count": max((e["reach_count"] for e in all_entries), default=0),
    }

    # --- resolution.json: object keyed by package -> list per channel ---
    by_package: dict[str, list[dict]] = {}
    for entry in all_entries:
        by_package.setdefault(entry["package"], []).append(entry)
    resolution: dict[str, list[dict]] = {}
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
