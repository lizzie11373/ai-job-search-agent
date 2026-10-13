from pathlib import Path

from job_agent.storage.database import DEFAULT_DB_PATH, get_connection


def is_setup_completed(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> bool:
    connection = get_connection(db_path)
    try:
        row = connection.execute(
            "SELECT setup_completed FROM app_state WHERE singleton_id = 1"
        ).fetchone()
    finally:
        connection.close()
    return bool(row["setup_completed"]) if row is not None else False


def set_setup_completed(
    completed: bool = True,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> None:
    connection = get_connection(db_path)
    try:
        with connection:
            connection.execute(
                """
                INSERT INTO app_state (singleton_id, setup_completed)
                VALUES (1, ?)
                ON CONFLICT(singleton_id)
                DO UPDATE SET setup_completed = excluded.setup_completed
                """,
                (1 if completed else 0,),
            )
    finally:
        connection.close()
