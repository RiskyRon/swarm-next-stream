import os
import aiofiles
from gpt_researcher import GPTResearcher
import asyncio

async def get_report(query: str, report_type: str):
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    
    # Get additional information
    research_context = researcher.get_research_context()
    research_costs = researcher.get_costs()
    research_images = researcher.get_research_images()
    research_sources = researcher.get_research_sources()
    
    return report, research_context, research_costs, research_images, research_sources

async def save_markdown_report(report: str, file_path: str):
    # Ensure the directory for the file exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    async with aiofiles.open(file_path, mode='w') as file:
        await file.write(report)

async def save_images(images: list, dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    for idx, image in enumerate(images):
        image_path = os.path.join(dir_path, f"research_image_{idx + 1}.png")
        # Ensure the image data is in bytes format before writing
        if isinstance(image, str):
            image = image.encode('utf-8')
        async with aiofiles.open(image_path, mode='wb') as image_file:
            await image_file.write(image)

if __name__ == "__main__":
    query = "Research Kamala Harris's relationship with Judge Joe Brown?"
    report_type = "research_report"
    
    report_output_path = "./output/research_report.md"
    images_output_dir = "./output/images"

    report, context, costs, images, sources = asyncio.run(get_report(query, report_type))
    
    # Save report to markdown file
    asyncio.run(save_markdown_report(report, report_output_path))

    # Save images to project directory
    asyncio.run(save_images(images, images_output_dir))
    
    print("Report saved to:", report_output_path)
    print("Images saved to:", images_output_dir)
    print("\nResearch Costs:")
    print(costs)
    print("\nNumber of Research Images:")
    print(len(images))
    print("\nNumber of Research Sources:")
    print(len(sources))
