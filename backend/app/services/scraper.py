import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

IUT_NOTICE_BOARD_URL = "https://www.iutoic-dhaka.edu/notices"


class IUTWebsiteScraper:
    def __init__(self, base_url: str = IUT_NOTICE_BOARD_URL):
        self.base_url = base_url

    async def fetch_recent_notices(self) -> List[Dict[str, Any]]:
        """Scrape the notice board page for newly posted notices and PDFs."""
        logger.info(f"Checking for new notices on {self.base_url}...")
        results = []
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self.base_url)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {self.base_url}, status code: {response.status_code}")
                    return results

                soup = BeautifulSoup(response.text, "html.parser")
                # Parse notice links and titles
                # Actual HTML structure will be mapped to the live site elements
                for item in soup.find_all("a", href=True):
                    href = item["href"]
                    if ".pdf" in href.lower() or "/notice/" in href.lower():
                        results.append({
                            "title": item.get_text(strip=True) or "Official Notice",
                            "url": href if href.startswith("http") else f"https://www.iutoic-dhaka.edu{href}",
                        })
        except Exception as e:
            logger.error(f"Error executing scraper: {e}")

        return results


scraper_service = IUTWebsiteScraper()
