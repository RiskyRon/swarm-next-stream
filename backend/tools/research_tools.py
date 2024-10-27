import asyncio
import logging
from gpt_researcher import GPTResearcher # type: ignore
import asyncio
import nest_asyncio  # type: ignore # Add this import

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()
async def fetch_report(query):
    """
    Fetch a research report based on the provided query and report type.
    """
    researcher = GPTResearcher(query=query)
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

def run_async(coroutine):
    """Helper function to run async functions in a sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def generate_research_report(query: str) -> str:
    """
    Synchronous function to generate a research report.
    Uses the current event loop if one exists, or creates a new one if needed.
    """
    async def _async_research():
        try:
            researcher = GPTResearcher(query=query)
            await researcher.conduct_research()
            return await researcher.write_report()
        except Exception as e:
            logging.error(f"Error in _async_research: {str(e)}")
            return f"Error conducting research: {str(e)}"

    try:
        # Get the current event loop
        loop = asyncio.get_running_loop()
        # Create a new task in the current loop
        return loop.run_until_complete(_async_research())
    except RuntimeError:
        # If no event loop is running, create a new one
        return asyncio.run(_async_research())
    except Exception as e:
        logging.error(f"Error in generate_research_report: {str(e)}")
        return f"Error generating research report: {str(e)}"