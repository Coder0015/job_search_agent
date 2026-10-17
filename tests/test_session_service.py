from app.services.session_service import SessionService


def test_create_session_binds_resume():
    service = SessionService()

    session = service.create_session("resume_sales_001")

    assert session.session_id
    assert session.resume_id == "resume_sales_001"
    assert session.thread_id
    assert session.created_at is not None
    assert service.get_session(session.session_id) == session


def test_sessions_have_independent_ids_and_threads():
    service = SessionService()

    first = service.create_session("resume_sales_001")
    second = service.create_session("resume_developer_001")

    assert first.session_id != second.session_id
    assert first.thread_id != second.thread_id
    assert first.resume_id != second.resume_id


def test_get_missing_session_returns_none():
    service = SessionService()

    assert service.get_session("missing-session") is None


def test_delete_session_only_removes_target():
    service = SessionService()
    first = service.create_session("resume_sales_001")
    second = service.create_session("resume_developer_001")

    service.delete_session(first.session_id)

    assert service.get_session(first.session_id) is None
    assert service.get_session(second.session_id) == second


def test_delete_missing_session_is_safe():
    service = SessionService()

    service.delete_session("missing-session")

    assert service.get_session("missing-session") is None
