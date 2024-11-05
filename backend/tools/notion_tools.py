from typing import Dict, List, Optional, Any, Union
import logging
from notion_client import Client
import os
from datetime import datetime

class NotionHandler:
    def __init__(self):
        self.notion = Client(auth=os.environ["NOTION_TOKEN"])
        self.default_parent_id = os.environ.get("NOTION_PARENT_PAGE")
        if not self.default_parent_id:
            raise ValueError("NOTION_PARENT_PAGE environment variable not set")
        self.logger = logging.getLogger(__name__)

    def search_pages(self, query: str) -> Dict[str, Any]:
        """
        Search for pages in Notion.
        
        Args:
            query (str): Search query
            
        Returns:
            Dict containing search results
        """
        try:
            results = self.notion.search(query=query).get("results", [])
            return {
                "success": True,
                "results": [
                    {
                        "id": page.get("id"),
                        "title": self._get_page_title(page),
                        "url": page.get("url"),
                        "last_edited": page.get("last_edited_time")
                    }
                    for page in results
                ]
            }
        except Exception as e:
            self.logger.error(f"Error searching Notion: {str(e)}")
            return {"success": False, "error": str(e)}

    def create_page(self, title: str, content: List[Dict[str, Any]], parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new page in Notion.
        
        Args:
            title (str): Page title
            content (List[Dict]): List of block contents
            parent_id (Optional[str]): ID of the parent page/database. If None, uses default parent page.
            
        Returns:
            Dict containing the created page info
        """
        try:
            # Use provided parent_id or default to NOTION_PARENT_PAGE
            page_parent_id = parent_id or self.default_parent_id
            
            # Create the page
            new_page = self.notion.pages.create(
                parent={"page_id": page_parent_id},
                properties={
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    }
                },
                children=content
            )
            
            return {
                "success": True,
                "page_id": new_page["id"],
                "url": new_page["url"]
            }
        except Exception as e:
            self.logger.error(f"Error creating page: {str(e)}")
            return {"success": False, "error": str(e)}

    def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a page's properties.
        
        Args:
            page_id (str): ID of the page to update
            properties (Dict): Properties to update
            
        Returns:
            Dict containing the update status
        """
        try:
            updated_page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            return {
                "success": True,
                "page_id": updated_page["id"],
                "url": updated_page["url"]
            }
        except Exception as e:
            self.logger.error(f"Error updating page: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """
        Get the content of a page.
        
        Args:
            page_id (str): ID of the page
            
        Returns:
            Dict containing the page content
        """
        try:
            blocks = self.notion.blocks.children.list(page_id).get("results", [])
            return {
                "success": True,
                "content": self._format_blocks(blocks)
            }
        except Exception as e:
            self.logger.error(f"Error getting page content: {str(e)}")
            return {"success": False, "error": str(e)}

    def _get_page_title(self, page: Dict[str, Any]) -> str:
        """Helper method to extract page title"""
        if "properties" in page:
            title_prop = page["properties"].get("title", {})
            if "title" in title_prop:
                title_items = title_prop["title"]
                if title_items and "plain_text" in title_items[0]:
                    return title_items[0]["plain_text"]
        return "Untitled"

    def _format_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Helper method to format blocks for display"""
        formatted_blocks = []
        for block in blocks:
            block_type = block["type"]
            if block_type in block:
                content = block[block_type]
                if "text" in content:
                    text_content = " ".join([text["plain_text"] for text in content["text"]])
                    formatted_blocks.append({
                        "type": block_type,
                        "content": text_content
                    })
        return formatted_blocks

# Create singleton instance
notion_handler = NotionHandler()

def search_notion(query: str) -> str:
    """
    Search Notion pages and return formatted results.
    """
    result = notion_handler.search_pages(query)
    if result["success"]:
        if not result["results"]:
            return "No results found."
        
        response = "Found the following pages:\n\n"
        for page in result["results"]:
            response += f"- [{page['title']}]({page['url']})\n"
        return response
    return f"Error searching Notion: {result.get('error')}"

def create_notion_page(title: str, content: str, parent_id: Optional[str] = None) -> str:
    """
    Create a new Notion page with the given content.
    
    Args:
        title (str): The title of the new page
        content (str): The content for the page
        parent_id (Optional[str]): Parent page ID. If None, uses NOTION_PARENT_PAGE from environment
    """
    # Convert content string to Notion blocks format
    blocks = [{
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": content}}]
        }
    }]
    
    result = notion_handler.create_page(title, blocks, parent_id)
    if result["success"]:
        return f"Page created successfully: {result['url']}"
    return f"Error creating page: {result.get('error')}"

def get_notion_page_content(page_id: str) -> str:
    """
    Get the content of a Notion page.
    """
    result = notion_handler.get_page_content(page_id)
    if result["success"]:
        content = result["content"]
        if not content:
            return "Page is empty."
        
        response = "Page content:\n\n"
        for block in content:
            response += f"{block['content']}\n\n"
        return response
    return f"Error getting page content: {result.get('error')}"

def update_notion_page(page_id: str, title: str) -> str:
    """
    Update a Notion page's title.
    """
    properties = {
        "title": {
            "title": [
                {
                    "text": {
                        "content": title
                    }
                }
            ]
        }
    }
    
    result = notion_handler.update_page(page_id, properties)
    if result["success"]:
        return f"Page updated successfully: {result['url']}"
    return f"Error updating page: {result.get('error')}"