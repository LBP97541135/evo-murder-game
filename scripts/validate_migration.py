"""Validate legacy SQLite data migration.

The script intentionally prints ASCII-only text so it works in PowerShell,
cmd.exe, UTF-8 terminals, CI logs, and redirected output.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from dataclasses import dataclass, field
from typing import Iterable


DB_PATH = os.getenv("SQLITE_PATH", "data/murder_mystery.db")


@dataclass
class CheckResult:
    table: str
    status: str = "ok"
    details: list[str] = field(default_factory=list)

    def fail(self, detail: str) -> None:
        self.status = "error"
        self.details.append(detail)

    def warn(self, detail: str) -> None:
        if self.status != "error":
            self.status = "warning"
        self.details.append(detail)

    def note(self, detail: str) -> None:
        self.details.append(detail)


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    if not table_exists(conn, table):
        return -1
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def columns(conn: sqlite3.Connection, table: str) -> set[str]:
    if not table_exists(conn, table):
        return set()
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def require_table(conn: sqlite3.Connection, table: str) -> CheckResult:
    result = CheckResult(table)
    if not table_exists(conn, table):
        result.fail(f"missing table: {table}")
    else:
        result.note(f"rows: {count_rows(conn, table)}")
    return result


def require_columns(conn: sqlite3.Connection, result: CheckResult, required: Iterable[str]) -> None:
    existing = columns(conn, result.table)
    missing = [name for name in required if name not in existing]
    if missing:
        result.fail(f"missing columns: {', '.join(missing)}")
    else:
        result.note("required columns: ok")


def compare_equal(conn: sqlite3.Connection, old_table: str, new_table: str) -> CheckResult:
    result = CheckResult(new_table)
    if not table_exists(conn, old_table):
        result.status = "skip"
        result.note(f"legacy table absent: {old_table}")
        return result
    if not table_exists(conn, new_table):
        result.fail(f"missing table: {new_table}")
        return result

    old_count = count_rows(conn, old_table)
    new_count = count_rows(conn, new_table)
    result.note(f"legacy rows: {old_count}")
    result.note(f"new rows: {new_count}")
    if old_count != new_count:
        result.fail(f"row count mismatch: {old_table}={old_count}, {new_table}={new_count}")
    return result


def compare_at_least(conn: sqlite3.Connection, old_table: str, new_table: str) -> CheckResult:
    """Validate legacy rows exist while allowing additional native rows."""

    result = CheckResult(new_table)
    if not table_exists(conn, old_table):
        result.status = "skip"
        result.note(f"legacy table absent: {old_table}")
        return result
    if not table_exists(conn, new_table):
        result.fail(f"missing table: {new_table}")
        return result

    old_count = count_rows(conn, old_table)
    new_count = count_rows(conn, new_table)
    result.note(f"legacy rows: {old_count}")
    result.note(f"new rows: {new_count}")
    if new_count < old_count:
        result.fail(f"new table lost rows: {new_table}={new_count} < {old_table}={old_count}")
    elif new_count > old_count:
        result.note("new table has additional native rows; accepted")
    return result


def validate_scripts(conn: sqlite3.Connection) -> CheckResult:
    result = require_table(conn, "scripts")
    if result.status != "error":
        require_columns(conn, result, ["status", "metadata_json", "duration_minutes"])
    return result


def validate_characters(conn: sqlite3.Connection) -> CheckResult:
    result = compare_equal(conn, "characters", "script_characters")
    if result.status == "ok":
        missing = conn.execute(
            """
            SELECT c.id
            FROM characters c
            LEFT JOIN script_characters sc ON sc.id = c.id
            WHERE sc.id IS NULL
            LIMIT 5
            """
        ).fetchall()
        if missing:
            result.fail(f"missing migrated character ids: {[row[0] for row in missing]}")
    return result


def validate_truths(conn: sqlite3.Connection) -> CheckResult:
    result = CheckResult("script_truths")
    if not table_exists(conn, "spoiler_stories"):
        result.status = "skip"
        result.note("legacy table absent: spoiler_stories")
        return result
    if not table_exists(conn, "script_truths"):
        result.fail("missing table: script_truths")
        return result

    old_count = count_rows(conn, "spoiler_stories")
    expected = conn.execute("SELECT COUNT(DISTINCT script_id) FROM spoiler_stories").fetchone()[0]
    new_count = count_rows(conn, "script_truths")
    result.note(f"legacy rows: {old_count}")
    result.note(f"expected distinct scripts: {expected}")
    result.note(f"new rows: {new_count}")
    if new_count != expected:
        result.fail(f"row count mismatch: script_truths={new_count}, expected={expected}")
    return result


def validate_game_sessions(conn: sqlite3.Connection) -> CheckResult:
    result = require_table(conn, "game_sessions")
    if result.status != "error":
        require_columns(conn, result, ["host_user_id", "metadata_json"])
    if not table_exists(conn, "game_phase_events"):
        result.fail("missing table: game_phase_events")
    else:
        result.note(f"game_phase_events rows: {count_rows(conn, 'game_phase_events')}")
    return result


def validate_conversations(conn: sqlite3.Connection) -> CheckResult:
    result = CheckResult("conversation_threads")
    if not table_exists(conn, "conversation_turns"):
        result.status = "skip"
        result.note("legacy table absent: conversation_turns")
        return result
    if not table_exists(conn, "conversation_threads") or not table_exists(conn, "conversation_messages"):
        result.fail("missing conversation_threads or conversation_messages")
        return result

    old_turns = count_rows(conn, "conversation_turns")
    threads = count_rows(conn, "conversation_threads")
    messages = count_rows(conn, "conversation_messages")
    result.note(f"legacy turns: {old_turns}")
    result.note(f"threads: {threads}")
    result.note(f"messages: {messages}")
    if old_turns > 0 and threads == 0:
        result.fail("no threads created from legacy turns")
    if messages < old_turns:
        result.fail(f"message count too low: messages={messages}, legacy turns={old_turns}")
    return result


def validate_evidence(conn: sqlite3.Connection) -> CheckResult:
    result = compare_at_least(conn, "evidences", "evidence_instances")
    if result.status == "ok":
        require_columns(conn, result, ["is_public"])
    return result


def validate_agents(conn: sqlite3.Connection) -> CheckResult:
    result = compare_at_least(conn, "agent_nodes", "agents")
    if result.status == "ok":
        missing = conn.execute(
            """
            SELECT an.id
            FROM agent_nodes an
            LEFT JOIN agents a ON a.id = an.id
            WHERE a.id IS NULL
            LIMIT 5
            """
        ).fetchall()
        if missing:
            result.fail(f"missing migrated agent ids: {[row[0] for row in missing]}")
    return result


def validate_agent_states(conn: sqlite3.Connection) -> CheckResult:
    return compare_equal(conn, "agent_game_states", "agent_runtime_states")


def validate_experiences(conn: sqlite3.Connection) -> CheckResult:
    return compare_equal(conn, "genes", "experience_records")


def validate_skills(conn: sqlite3.Connection) -> CheckResult:
    result = compare_at_least(conn, "capsules", "skills")
    if result.status == "ok":
        missing = conn.execute(
            """
            SELECT c.id
            FROM capsules c
            LEFT JOIN skills s ON s.id = c.id
            WHERE s.id IS NULL
            LIMIT 5
            """
        ).fetchall()
        if missing:
            result.fail(f"missing migrated skill ids: {[row[0] for row in missing]}")
    return result


def validate_migration(allow_warnings: bool = False) -> int:
    print("=" * 60)
    print("  Migration validation report")
    print("=" * 60)
    print(f"database: {DB_PATH}")
    print(f"allow_warnings: {allow_warnings}")
    print()

    if not os.path.exists(DB_PATH):
        print(f"[FAIL] database file does not exist: {DB_PATH}")
        return 1

    validators = [
        validate_scripts,
        validate_characters,
        validate_truths,
        validate_game_sessions,
        validate_conversations,
        validate_evidence,
        validate_agents,
        validate_agent_states,
        validate_experiences,
        validate_skills,
    ]

    conn = sqlite3.connect(DB_PATH)
    try:
        results = [validator(conn) for validator in validators]
    finally:
        conn.close()

    labels = {
        "ok": "[OK]",
        "warning": "[WARN]",
        "error": "[FAIL]",
        "skip": "[SKIP]",
    }
    for result in results:
        print(f"{labels.get(result.status, '[?]')} {result.table}: {result.status}")
        for detail in result.details:
            print(f"  {detail}")
        print()

    ok_count = sum(result.status == "ok" for result in results)
    warning_count = sum(result.status == "warning" for result in results)
    error_count = sum(result.status == "error" for result in results)
    skip_count = sum(result.status == "skip" for result in results)

    print("=" * 60)
    print("  Summary")
    print("=" * 60)
    print(f"  ok: {ok_count}")
    print(f"  warnings: {warning_count}")
    print(f"  errors: {error_count}")
    print(f"  skipped: {skip_count}")
    print()

    if error_count:
        print("[RESULT] failed: migration has errors")
        return 1
    if warning_count and not allow_warnings:
        print("[RESULT] failed: migration has warnings")
        return 1
    print("[RESULT] passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate legacy SQLite data migration.")
    parser.add_argument(
        "--allow-warnings",
        action="store_true",
        help="Return 0 when warnings exist. Errors still fail.",
    )
    args = parser.parse_args()
    return validate_migration(allow_warnings=args.allow_warnings)


if __name__ == "__main__":
    sys.exit(main())
