import createMD as create
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Function to convert date to ISO format (YYYYMMDD)
def format_date(postdate_text):
    try:
        return datetime.strptime(postdate_text.strip(), "%B %d, %Y").strftime("%Y%m%d")
    except ValueError:
        return None

# URL of the webpage to scrape
url = "https://opinion.inquirer.net/category/editorial"

# Set a user-agent header to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# Send a GET request with the user-agent header
response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all article blocks
    articles = soup.find_all("div", id="ch-ls-box")

    # Dictionary to store articles
    articles_data = {}

    for article in articles:
        # Check if the div#ch-cat contains the text "Editorial"
        category_div = article.find("div", id="ch-cat")
        if category_div and category_div.text.strip() == "Editorial":
            # Get the post date
            postdate_span = article.find("div", id="ch-postdate").find("span")
            if not postdate_span:
                continue

            postdate = format_date(postdate_span.text)
            if not postdate:
                continue

            # Get the article link and title
            title_anchor = article.find("a")
            if not title_anchor:
                continue

            title = title_anchor.text.strip()
            href = title_anchor["href"]

            # Save to dictionary
            articles_data[postdate] = {
                "title": title,
                "postdate": postdate,
                "href": href
            }

    # Save data to a JSON file
    with open("inq_editorial.json", "w", encoding="utf-8") as json_file:
        json.dump(articles_data, json_file, indent=4, ensure_ascii=False)

    print("Scraping completed. Articles saved to 'inq_editorial.json'.")
else:
    print(f"Failed to fetch the webpage. HTTP Status Code: {response.status_code}")

create.now()