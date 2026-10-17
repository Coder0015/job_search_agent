from app.services.session_service import SessionService


def main():
    service = SessionService()
    first = service.create_session("resume_sales_001")
    second = service.create_session("resume_developer_001")

    assert first.session_id != second.session_id
    assert first.thread_id != second.thread_id
    assert first.resume_id == "resume_sales_001"
    assert second.resume_id == "resume_developer_001"
    assert service.get_session(first.session_id) == first
    assert service.get_session(second.session_id) == second

    service.delete_session(first.session_id)
    assert service.get_session(first.session_id) is None
    assert service.get_session(second.session_id) == second

    service.delete_session(first.session_id)
    assert service.get_session("missing-session") is None

    print("SessionService 检查通过")
    print(f"第一个会话：{first.session_id} -> {first.thread_id}")
    print(f"第二个会话：{second.session_id} -> {second.thread_id}")


if __name__ == "__main__":
    main()
