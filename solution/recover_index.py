#!/usr/bin/env python3
"""Rebuild the authoritative registry index truncated by the failed migration.

Implements the registry governance board's final recovery decision (#REG-7170 in
/app/incident/registry_governance_log.md), which supersedes the #REG-7002 draft
and revises the #REG-7009 interim: start from the pre-migration snapshot in file
order, then replay the journal in ascending journal_seq order; an ``append``
entry overwrites the first record of that package already carrying the same
version string in place (and is otherwise appended to the end of the package's
release list), a ``retract`` entry removes every record of that package carrying
that version, journal bookkeeping fields never reach the recovered index, and
the result is written back to /app/data/registry_index.json.
"""

from __future__ import annotations

import json
from pathlib import Path

INDEX_PATH = Path("/app/data/registry_index.json")
SNAPSHOT_PATH = Path("/app/data/registry_snapshot_pre_migration.json")
JOURNAL_PATH = Path("/app/data/registry_replay_journal.json")

RELEASE_FIELDS = ("version", "yanked", "deps")


def recover(snapshot: dict, journal: list[dict]) -> dict:
    index = {package: [dict(record) for record in rows] for package, rows in snapshot.items()}
    for entry in sorted(journal, key=lambda e: e["journal_seq"]):
        package = entry["package"]
        version = entry["version"]
        if entry["journal_op"] == "retract":
            # A retract contributes no record of its own, so a retract naming a
            # package the snapshot never held leaves no key behind either.
            if package in index:
                index[package] = [r for r in index[package] if r["version"] != version]
            continue
        rows = index.setdefault(package, [])
        record = {field: entry[field] for field in RELEASE_FIELDS}
        for position, existing in enumerate(rows):
            if existing["version"] == version:
                rows[position] = record
                break
        else:
            rows.append(record)
    return index


def main() -> None:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    journal = json.loads(JOURNAL_PATH.read_text(encoding="utf-8"))
    recovered = recover(snapshot, journal)
    INDEX_PATH.write_text(json.dumps(recovered, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
