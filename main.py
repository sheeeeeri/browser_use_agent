import asyncio
import logging
import sys

import httpx
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

CDP_URL = "http://localhost:9222"


async def wait_for_chrome(retries: int = 15, delay: float = 1.0) -> bool:
    """Ждёт, пока Chrome откроет отладочный порт 9222."""
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{CDP_URL}/json/version")
                if resp.status_code == 200:
                    logger.info("Chrome доступен на порту 9222.")
                    return True
        except Exception:
            pass
        logger.info("Ожидание Chrome... попытка %d/%d", attempt, retries)
        await asyncio.sleep(delay)
    return False


browser = Browser(cdp_url=CDP_URL)

controller = Controller()


@controller.action("Ask user for confirmation before performing a destructive or irreversible action")
async def confirm_action(action_description: str) -> str:
    print(f"\n⚠️  Агент собирается выполнить: {action_description}")
    response = input("Подтвердить? (да/нет): ").strip().lower()
    if response in ("да", "д", "yes", "y"):
        return "User confirmed. Proceed."
    return "User rejected. Do NOT perform this action."


SECURITY_RULE = (
    "SECURITY: Before deleting, purchasing, submitting, or any irreversible action "
    "— always call confirm_action tool first and wait for approval."
)


async def run_agent(task: str) -> None:
    llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0.0)
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        extend_system_message=SECURITY_RULE,
        controller=controller,
        use_vision=False,
        max_history_items=10,
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


async def main_loop() -> None:
    if not await wait_for_chrome():
        logger.error(
            "Chrome недоступен на порту 9222. "
            "Запустите start_chrome_debug.bat и повторите попытку."
        )
        return

    while True:
        try:
            user_task = input("\nВведите задачу (или 'выход' для завершения): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nЗавершение работы.")
            break
        if not user_task:
            print("Задача не может быть пустой. Попробуйте снова.")
            continue
        if user_task.lower() in ("выход", "exit", "quit", "q"):
            print("Завершение работы.")
            break
        await run_agent(user_task)


if __name__ == "__main__":
    asyncio.run(main_loop())
