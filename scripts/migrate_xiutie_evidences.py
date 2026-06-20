"""
从 murder_mystery(6).db 迁移锈铁大道证物到 data/murder_mystery.db。
保留 data 库中已有证物，补充 db(6) 的完整证物条目，确保总数 >= MIN_EVIDENCES。
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DB = ROOT / "murder_mystery(6).db"
TARGET_DB = ROOT / "data" / "murder_mystery.db"
SCRIPT_ID = "xiutie-avenue-missing-three-minutes"
MIN_EVIDENCES = 12

# 优先迁移：核心推理链 + 各角色关联证物（按游戏价值排序）
PRIORITY_IDS = [
    "ev_wrench",
    "ev_body",
    "ev_cctv_loop",
    "ev_coffee_drug",
    "ev_guchen_notebook",
    "ev_guchen_phone",
    "ev_anonymous_letters",
    "ev_cabinet_pry",
    "ev_temp_log",
    "ev_factory_map",
    "ev_head_injury_left",
    "ev_recording_pen",
    "ev_shenhe_recorder",
    "ev_zhoulan_gloves",
    "ev_qinye_fingerprint",
    "ev_back_door_wiped",
    "ev_coffee_fingerprint",
    "ev_linyuan_pills",
    "ev_control_room_photo",
    "ev_desk_blood",
]

IMPORTANCE_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def fetch_evidences(db_path: Path, script_id: str) -> dict[str, dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM script_evidences WHERE script_id = ?",
        (script_id,),
    ).fetchall()
    conn.close()
    return {row["id"]: dict(row) for row in rows}


def insert_evidence(conn: sqlite3.Connection, row: dict) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO script_evidences (
            id, script_id, name, description, category, importance,
            initial_state, image_filename, related_characters,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            script_id = excluded.script_id,
            name = excluded.name,
            description = excluded.description,
            category = excluded.category,
            importance = excluded.importance,
            initial_state = excluded.initial_state,
            image_filename = excluded.image_filename,
            related_characters = excluded.related_characters,
            updated_at = excluded.updated_at
        """,
        (
            row["id"],
            row["script_id"],
            row["name"],
            row["description"],
            row["category"],
            row["importance"],
            row["initial_state"],
            row.get("image_filename") or "",
            row.get("related_characters") or "[]",
            row.get("created_at") or now,
            now,
        ),
    )


def main() -> None:
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"源数据库不存在: {SOURCE_DB}")
    if not TARGET_DB.exists():
        raise FileNotFoundError(f"目标数据库不存在: {TARGET_DB}")

    source = fetch_evidences(SOURCE_DB, SCRIPT_ID)
    if not source:
        raise RuntimeError(f"源库中未找到 script_id={SCRIPT_ID} 的证物")

    target_conn = sqlite3.connect(TARGET_DB)
    try:
        existing = {
            r[0]
            for r in target_conn.execute(
                "SELECT id FROM script_evidences WHERE script_id = ?",
                (SCRIPT_ID,),
            ).fetchall()
        }
        print(f"目标库现有证物: {len(existing)} 条")

        migrated: list[str] = []
        for eid in PRIORITY_IDS:
            if eid not in source:
                print(f"  跳过（源库无此 id）: {eid}")
                continue
            insert_evidence(target_conn, source[eid])
            migrated.append(eid)

        current = {
            r[0]
            for r in target_conn.execute(
                "SELECT id FROM script_evidences WHERE script_id = ?",
                (SCRIPT_ID,),
            ).fetchall()
        }

        if len(current) < MIN_EVIDENCES:
            remaining = [
                eid
                for eid in sorted(
                    source.keys(),
                    key=lambda x: (
                        IMPORTANCE_RANK.get(source[x]["importance"], 9),
                        x,
                    ),
                )
                if eid not in current
            ]
            for eid in remaining:
                insert_evidence(target_conn, source[eid])
                migrated.append(eid)
                current.add(eid)
                if len(current) >= MIN_EVIDENCES:
                    break

        target_conn.commit()

        final_rows = target_conn.execute(
            "SELECT id, name, importance FROM script_evidences WHERE script_id = ? ORDER BY importance, id",
            (SCRIPT_ID,),
        ).fetchall()

        print(f"\n已迁移/更新 {len(migrated)} 条证物")
        print(f"最终证物总数: {len(final_rows)} 条\n")
        for eid, name, importance in final_rows:
            tag = " [updated]" if eid in migrated and eid in existing else ""
            tag = tag or (" [new]" if eid in migrated else "")
            print(f"  {eid} | {importance:8} | {name}{tag}")

        if len(final_rows) < MIN_EVIDENCES:
            raise RuntimeError(f"迁移后仍不足 {MIN_EVIDENCES} 条证物")
    finally:
        target_conn.close()


if __name__ == "__main__":
    main()
