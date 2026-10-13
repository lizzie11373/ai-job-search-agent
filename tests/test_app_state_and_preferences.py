from pathlib import Path

from job_agent.models.preference import CandidatePreferenceProfile
from job_agent.storage.app_state_repository import (
    is_setup_completed,
    set_setup_completed,
)
from job_agent.storage.database import initialize_database
from job_agent.storage.preference_repository import (
    load_candidate_preferences,
    save_candidate_preferences,
)


def test_setup_completed_is_durable_singleton(tmp_path: Path):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)
    assert is_setup_completed(db_path=db_path) is False
    set_setup_completed(True, db_path=db_path)
    assert is_setup_completed(db_path=db_path) is True


def test_preferences_persist_only_v1_categories(tmp_path: Path):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)

    save_candidate_preferences(
        CandidatePreferenceProfile(
            preferred_locations={"Bay Area", "New York"},
            accepted_work_modes={"Hybrid", "Remote"},
            accepted_employment_types={"Full-Time"},
            minimum_compensation=200000,  # deliberately not persisted in V1
            preferred_industries={"Technology"},
            preferred_company_sizes={"Large"},
        ),
        db_path=db_path,
    )

    loaded = load_candidate_preferences(db_path=db_path)
    assert loaded.preferred_locations == {"Bay Area", "New York"}
    assert loaded.accepted_work_modes == {"Hybrid", "Remote"}
    assert loaded.accepted_employment_types == {"Full-Time"}
    assert loaded.preferred_industries == {"Technology"}
    assert loaded.preferred_company_sizes == {"Large"}
    assert loaded.minimum_compensation is None


def test_finish_setup_state_can_exist_before_first_successful_run(
    tmp_path: Path,
    monkeypatch,
):
    from job_agent.services import ui_service

    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)

    def fail_run_agent(**kwargs):
        raise RuntimeError("first run interrupted")

    import job_agent.services.agent_run_service as run_module
    monkeypatch.setattr(run_module, "run_agent", fail_run_agent)

    try:
        ui_service.finish_setup_and_run_agent(
            emails=[],
            db_path=db_path,
        )
    except RuntimeError as exc:
        assert "interrupted" in str(exc)
    else:
        raise AssertionError("Expected interrupted first run")

    assert is_setup_completed(db_path=db_path) is True
