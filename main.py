from browser_use import Agent, Browser, ChatAnthropic
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Подключаемся к уже запущенному Chrome (запусти start_chrome_debug.bat перед стартом скрипта)
browser = Browser(
    cdp_url='http://localhost:9222',
)

async def main():
    llm = ChatAnthropic(model='claude-sonnet-4-5', temperature=0.0)
    task = "Прочитай последние 10 писем в почте mail.ru и удали спам"
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())