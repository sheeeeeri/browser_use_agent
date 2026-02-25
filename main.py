from browser_use import Agent, Browser, ChatAnthropic
from dotenv import load_dotenv
import asyncio

load_dotenv()

browser = Browser(
    executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    user_data_dir=r'C:\Users\kkosherkaa\AppData\Local\Google\Chrome\User Data',
    profile_directory='Default',
    headless=False,
)

async def main():
    llm = ChatAnthropic(model='claude-sonnet-4-5', temperature=0.0)
    task = "Войди в последнее мое письмо в mail.ru"
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())