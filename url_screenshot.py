from crawl4ai import WebCrawler
import base64

# Create the WebCrawler instance
crawler = WebCrawler()
crawler.warmup()

# Run the crawler with the screenshot parameter
result = crawler.run(url="https://crawl4ai.com/mkdocs/full_details/advanced_features/", screenshot=True)

# Save the screenshot to a file
with open("screenshot.png", "wb") as f:
    f.write(base64.b64decode(result.screenshot))

print("Screenshot saved to 'screenshot.png'!")