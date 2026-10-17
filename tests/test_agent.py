import json

from langgraph.checkpoint.memory import MemorySaver

from app.agents.factory.deepseek_agent import create_job_agent
from app.agents.prompts.resume_context import format_resume_context
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.job_service import JobService


TEST_RESUME_ID = "resume_sales_001"
EXIT_COMMANDS = {"退出", "exit", "quit"}
HISTORY_COMMANDS = {"历史", "history"}


def main():
    job_repository = JobRepository()
    job_service = JobService(job_repository)

    resume_repository = ResumeRepository()
    resume = resume_repository.get_by_id(TEST_RESUME_ID)
    if resume is None:
        raise ValueError(f"测试简历不存在：{TEST_RESUME_ID}")

    resume_context = format_resume_context(resume)
    checkpointer = MemorySaver()
    thread_id = f"manual-test-{TEST_RESUME_ID}"

    agent = create_job_agent(
        job_service=job_service,
        checkpointer=checkpointer,
        resume_context=resume_context,
    )

    print(f"当前测试简历：{resume.name}（{resume.id}）")
    print("已注入简历上下文：")
    print(resume_context)
    print("\n开始多轮对话。输入“历史”查看消息记录，输入“退出”结束。")

    while True:
        try:
            user_input = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n对话结束。")
            break

        if not user_input:
            print("请输入求职问题。")
            continue

        command = user_input.casefold()
        if command in EXIT_COMMANDS:
            print("对话结束。")
            break

        if command in HISTORY_COMMANDS:
            state = agent.get_state(
                {"configurable": {"thread_id": thread_id}}
            )
            messages = state.values.get("messages", [])
            print(f"当前历史消息数：{len(messages)}")
            for index, message in enumerate(messages, start=1):
                content = message.content
                if isinstance(content, str) and len(content) > 100:
                    content = content[:100] + "..."
                print(f"{index}. [{message.type}] {content}")
            continue

        state_before = agent.get_state(
            {"configurable": {"thread_id": thread_id}}
        )
        message_count_before = len(
            state_before.values.get("messages", [])
        )

        try:
            result = agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input,
                        }
                    ]
                },
                config={
                    "configurable": {
                        "thread_id": thread_id,
                    }
                },
            )
        except Exception as exc:
            print(f"Agent 调用失败：{type(exc).__name__}: {exc}")
            continue

        messages = result.get("messages", [])
        new_messages = messages[message_count_before:]
        if not new_messages:
            print("Agent 没有产生新的消息。")
            continue

        print_tool_messages(new_messages)
        print(f"\nAI：{messages[-1].content}")


def print_tool_messages(messages):
    """打印本轮 Agent 新增的工具调用及工具返回，便于调试。"""
    found_tool_activity = False

    for message in messages:
        tool_calls = getattr(message, "tool_calls", None) or []
        for tool_call in tool_calls:
            found_tool_activity = True
            print("\n[工具调用]")
            print(f"工具名称：{tool_call.get('name', '未知工具')}")
            print(
                "调用参数："
                f"{json.dumps(tool_call.get('args', {}), ensure_ascii=False)}"
            )

        if getattr(message, "type", None) == "tool":
            found_tool_activity = True
            print("\n[工具返回]")
            print(f"工具名称：{getattr(message, 'name', '未知工具')}")
            content = message.content
            try:
                parsed = json.loads(content)
                print(json.dumps(parsed, ensure_ascii=False, indent=2))
            except (TypeError, json.JSONDecodeError):
                print(content)

    if not found_tool_activity:
        print("\n[本轮未调用工具]")


if __name__ == "__main__":
    main()
