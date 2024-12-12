import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def now():
	# Load the article links from the JSON file
	json_file = "inq_editorial.json"
	try:
		with open(json_file, "r", encoding="utf-8") as file:
			articles = json.load(file)
		print("Loaded articles JSON file successfully.")
	except FileNotFoundError as e:
		print(f"JSON file not found: {json_file}. Error: {e}")
		return
	except json.JSONDecodeError as e:
		print(f"Error decoding JSON file: {json_file}. Error: {e}")
		return

	# Directory to save markdown files
	output_dir = "articles"
	os.makedirs(output_dir, exist_ok=True)
	print(f"Output directory '{output_dir}' created/exists.")

	# User-Agent header to bypass restrictions
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
	}

	# Scrape each article
	for postdate, article_data in articles.items():
		url = article_data["href"]
		title = article_data["title"]
		print(f"Processing article: {title} (URL: {url})")
		

		try:
			response = requests.get(url, headers=headers)
			if response.status_code == 200:
				print(f"Successfully fetched article: {url}")
				soup = BeautifulSoup(response.text, "html.parser")

				# Article Type
				art_type = "EDITORIAL"

				# Title
				entry_title_div = soup.find("h1", class_="entry-title")
				entry_title = entry_title_div.text.strip() if entry_title_div else title

				# Publication (Byline)
				authorship = "Unknown Publication"
				plat_div = soup.find("div", id="byline")
				if plat_div:
					authorship = plat_div.text.strip()

				# Image URL (featured image)
				image_url = None
				
				# Manual image link generation (based on format)
				image_url = f"https://opinion.inquirer.net/files/{int(postdate[:4])}/{int(postdate[4:6])}/editorial{int(postdate)}.png"

				# Additional debug output to verify
				print(f"Featured image URL: {image_url}")
				
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

				print(f"Saved article to file: {filename}")
			else:
				print(f"Failed to fetch article: {url} (HTTP {response.status_code})")
		except requests.RequestException as e:
			print(f"Request error while fetching article: {url}. Error: {e}")
		except Exception as e:
			print(f"Unexpected error while processing article: {url}. Error: {e}")

	print("Article scraping completed.")

if __name__ == '__main__':
	now()