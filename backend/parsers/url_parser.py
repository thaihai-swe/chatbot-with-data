import requests
from bs4 import BeautifulSoup


def parse_url(url, timeout_seconds=30):
    response = requests.get(url, timeout=timeout_seconds)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    text = " ".join(soup.stripped_strings)

    return {
        "text": text,
        "metadata": {
            "title": title,
            "source_url": url,
        },
        "errors": [],
    }
