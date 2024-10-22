from gpt_researcher import GPTResearcher
import asyncio

def run_async(coroutine):
    """Helper function to run async functions in a sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

async def fetch_report(query):
    """
    Fetch a research report based on the provided query and report type.
    """
    researcher = GPTResearcher(query=query)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def generate_research_report(query):
    """
    Synchronous wrapper for research report generation.
    """
    return run_async(fetch_report(query))

if __name__ == "__main__":
    QUERY = "argument for why Kamala Harris is a good candidate for president?"
    report = generate_research_report(QUERY)
    print(report)