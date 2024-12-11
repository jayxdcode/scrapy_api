import requests
from bs4 import BeautifulSoup
import json
import os
import logging

# Configure logging
logging.basicConfig(
    filename="article_scraper.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # Set to DEBUG for detailed logging
)

def now():
    # Load the article links from the JSON file
    json_file = "inq_editorial.json"
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            articles = json.load(file)
        logging.info("Loaded articles JSON file successfully.")
    except FileNotFoundError as e:
        logging.error(f"JSON file not found: {json_file}. Error: {e}")
        return
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON file: {json_file}. Error: {e}")
        return

    # Directory to save markdown files
    output_dir = "articles"
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Output directory '{output_dir}' created/exists.")

    # User-Agent header to bypass restrictions
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    # Scrape each article
    for postdate, article_data in articles.items():
        url = article_data["href"]
        title = article_data["title"]
        logging.info(f"Processing article: {title} (URL: {url})")

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                logging.info(f"Successfully fetched article: {url}")
                soup = BeautifulSoup(response.text, "html.parser")

                # Article Type
                art_type_div = soup.find("div", id="art_kicker")
                art_type = art_type_div.text.strip() if art_type_div else "Unknown Type"

                # Title
                entry_title_div = soup.find("h1", class_="entry-title")
                entry_title = entry_title_div.text.strip() if entry_title_div else title

                # Authorship (Byline)
                authorship = "Unknown Author"
                art_plat_div = soup.find("div", id="art_plat")
                if art_plat_div:
                    author_tag = art_plat_div.find("span", class_="author-name")
                    if author_tag:
                        authorship = author_tag.text.strip()
                elif soup.find("div", class_="author"):
                    authorship = soup.find("div", class_="author").text.strip()

                # Image URL (featured image)
                img_tag = None
                figure_div = soup.find("figure", class_="wp-block-image")
                if figure_div:
                    img_tag = figure_div.find("img")
                image_url = img_tag["src"] if img_tag else None

                # Article Content (the main body of the article)
                content = []
                for element in soup.find_all(["p", "h2"], recursive=False):
                    # Ignore certain <p> classes
                    if element.name == "p" and element.get("class") in [["headertext"], ["footertext"]]:
                        continue
                    content.append(element.text.strip())

                # Initialize markdown content string
                md_content = f"# {entry_title}\n\n"
                md_content += f"***{art_type}***\n\n"
                md_content += f"****{authorship}****\n\n"
                if image_url:
                    md_content += f"![Image]({image_url})\n\n"
                if content:
                    md_content += "\n\n".join(content)
                else:
                    md_content += "\nNo content available."

                # Save to markdown file
                filename = f"{postdate}_{entry_title.replace(' ', '_').replace('/', '_')}.md"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as md_file:
                    md_file.write(md_content)

                logging.info(f"Saved article to file: {filename}")
            else:
                logging.warning(f"Failed to fetch article: {url} (HTTP {response.status_code})")
        except requests.RequestException as e:
            logging.error(f"Request error while fetching article: {url}. Error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error while processing article: {url}. Error: {e}")

    logging.info("Article scraping completed.")

if __name__ == '__main__':
    now()