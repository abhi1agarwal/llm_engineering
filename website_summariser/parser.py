import requests
from bs4 import BeautifulSoup

class Website:
    """
    A class to represent a Webpage, fetch its content, and parse it.
    """
    def __init__(self, url: str):
        """
        Initializes the Website object by fetching and parsing the content from the given URL.
        Args:
            url: The URL of the website to process.
        """
        self.url = url
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            self.title = "Error Fetching Title"
            self.text = "Error fetching content."
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        
        # Remove irrelevant tags
        for irrelevant_tag in soup.find_all(['script', 'style', 'img', 'input', 'nav', 'footer', 'aside', 'header', 'form', 'iframe', 'link', 'meta']):
            irrelevant_tag.decompose()
            
        if soup.body:
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            # Fallback if no body tag, try to get text from the whole document
            self.text = soup.get_text(separator="\n", strip=True)

        if not self.text.strip():
            self.text = "No main textual content found after filtering." 