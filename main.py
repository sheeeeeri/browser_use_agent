from browser_use import Agent, Browser, ChatAnthropic, Controller
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Подключаемся к уже запущенному Chrome (запусти start_chrome_debug.bat перед стартом скрипта)
browser = Browser(
    cdp_url='http://localhost:9222',
)

context_strategy = """
CONTEXT MANAGEMENT RULES (follow strictly to stay within token limits):
- When reading emails: extract ONLY sender, subject, date and first 2 sentences of body. Never process full email HTML.
- When scanning a list of emails: extract structured data (sender, subject, date) row by row, do not include raw markup.
- Ignore navigation menus, sidebars, ads, footers — they are irrelevant to the task.
- If a page is too large to process at once, focus only on the content area relevant to current sub-task.
- Never load full page source into your reasoning; work with structured summaries only.
- SECURITY: Before deleting, purchasing, submitting, or any irreversible action — always call confirm_action tool first and wait for approval.
"""
controller = Controller()

@controller.action("Ask user for confirmation before performing a destructive or irreversible action")
async def confirm_action(action_description: str) -> str:
    print(f"\n⚠️  Агент собирается выполнить: {action_description}")
    response = input("Подтвердить? (да/нет): ").strip().lower()
    if response in ("да", "д", "yes", "y"):
        return "User confirmed. Proceed."
    return "User rejected. Do NOT perform this action."

async def main():
    llm = ChatAnthropic(model='claude-sonnet-4-5', temperature=0.0)
    task = "Прочитай последние 10 писем в почте mail.ru и удали спам"
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        extend_system_message=context_strategy, 
        controller=controller
    )
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())