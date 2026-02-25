import asyncio
import logging
import sys

from browser_use import Agent, Browser, Controller
from browser_use.llm import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

browser = Browser(cdp_url="http://localhost:9222")

controller = Controller()


@controller.action("Ask user for confirmation before performing a destructive or irreversible action")
async def confirm_action(action_description: str) -> str:
    print(f"\n⚠️  Агент собирается выполнить: {action_description}")
    response = input("Подтвердить? (да/нет): ").strip().lower()
    if response in ("да", "д", "yes", "y"):
        return "User confirmed. Proceed."
    return "User rejected. Do NOT perform this action."


CONTEXT_STRATEGY = """
CONTEXT MANAGEMENT RULES (follow strictly to stay within token limits):
- When reading emails: extract ONLY sender, subject, date and first 2 sentences of body. Never process full email HTML.
- When scanning a list of emails: extract structured data (sender, subject, date) row by row, do not include raw markup.
- Ignore navigation menus, sidebars, ads, footers — they are irrelevant to the task.
- If a page is too large to process at once, focus only on the content area relevant to current sub-task.
- Never load full page source into your reasoning; work with structured summaries only.
- SECURITY: Before deleting, purchasing, submitting, or any irreversible action — always call confirm_action tool first and wait for approval.
"""


async def run_agent(task: str) -> None:
    llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0.0)
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        extend_system_message=CONTEXT_STRATEGY,
        controller=controller,
    )
    try:
        logger.info("Запуск агента. Задача: %s", task)
        await agent.run()
        logger.info("Агент завершил работу.")
    except Exception as e:
        logger.error("Агент завершился с ошибкой: %s", e)
        raise
    finally:
        logger.info("Агент завершил сессию.")


if __name__ == "__main__":
    user_task = input("Введите задачу для агента: ").strip()
    if not user_task:
        logger.error("Задача не может быть пустой.")
        sys.exit(1)
    asyncio.run(run_agent(user_task))
