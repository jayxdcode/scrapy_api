import re
import os
import requests
from bs4 import BeautifulSoup
import json
from downloadFile import save

def sanitize_filename(filename):
	# Replace invalid characters in filenames with an underscore
	# Replace spaces with underscores
	return re.sub(r'[\\/*?:"<>| ]', '_', filename)

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
		print(f"\nProcessing article: {title} (URL: {url})")

		try:
			# Fetch the article
			response = requests.get(url, headers=headers)
			if response.status_code == 200:
				print(f"Successfully fetched article: {url}")
				soup = BeautifulSoup(response.text, "html.parser")

				# Article Type
				art_type = "EDITORIAL"

				# Title
				entry_title_div = soup.find("h1", class_="entry-title")
				entry_title = entry_title_div.text.strip() if entry_title_div else title

				# Sanitize title for file name
				clean_title = sanitize_filename(entry_title)

				# Get the author's name (same as remote file)
				authorship = "Unknown Publication"
				plat_div = soup.find("div", id="byline")
				if plat_div:
					authorship = plat_div.text.strip()

				# Image Filename (featured image)
				image_filename = f'editorial{postdate[4:8] + postdate[:4]}.png'

				# Construct the image URL
				image_url = f"https://opinion.inquirer.net/files/{postdate[:4]}/{postdate[4:6]}/{image_filename}"
				fallback = f"https://opinion.inquirer.net/files/{clean_title}-620x620.png"
				fallback_srcset = "placeholder"

				# Flag to check if an image URL worked
				image_url_valid = False

				# Check if the image URL is valid
				try:
					image_response = requests.get(image_url, headers=headers)
					if image_response.status_code == 200:
						print(f"\033[92mFeatured image URL: {image_url} (1/4)\033[0m")  # Green color for success
						save(image_url, image_filename)  # Download the image
						image_url_valid = True  # Mark as valid
					else:
						print(f"\033[91mImage not found or inaccessible at: {image_url} (HTTP {image_response.status_code})\033[0m")  # Red color for failure
				except requests.RequestException as e:
					print(f"\033[91mRequest error for image URL: {image_url}. Error: {e}\033[0m")  # Red color for error

				# If no valid image was found
				if not image_url_valid:
					print("No valid image URL found. Attempting additional fallbacks...")

					# Second fallback: Get the first link from srcset
					if not image_url_valid:
						try:
							# Find picture element inside section#inq_section
							section = soup.find('section', id='inq_section')
							picture = section.find('img') if section else None
							if picture:
								srcset = picture.get('srcset', '')
								source = picture.get('data-lazy-src', '')
								s = picture.get('src', '')

								# Check if srcset exists before using fallback_srcset
								if srcset:
									links = srcset.split(", ")
									if links:
										fallback_srcset = links[0].replace(" 620w", "")
										try:
											image_response = requests.get(fallback_srcset, headers=headers)
											if image_response.status_code == 200:
												print(f"\033[92m***Second Fallback Worked! URL (srcset): {fallback_srcset}\033[0m")
												save(fallback_srcset, image_filename)
												image_url_valid = True
											else:
												print(f"\033[91mImage not found in srcset: {fallback_srcset}\033[0m")
										except requests.RequestException as e:
											print(f"\033[91mRequest error for second fallback URL: {fallback_srcset}. Error: {e} (2/4)\033[0m")

								if source:
									image_response = requests.get(source, headers=headers)
									if image_response.status_code == 200:
										print(f"\033[92m***Third Fallback Worked! URL (source): {source}\033[0m")
										save(source, image_filename)
										image_url_valid = True
									else:
										print(f"\033[91mImage not found in source {source} (3/4)\033[0m")
								
								if s:
									image_response = requests.get(source, headers=headers)
									if image_response.status_code == 200:
										print(f"\033[92m***Fourth Fallback Worked! (Thank god. its the last) URL: {s}\033[0m")
										save(s, image_filename)
										image_url_valid = True
									else:
										print(f"\033[91mImage not found in src {s} (4/4)\033[0m")
								
							else:
								print("\033[91mNo picture element found in section#inq_section or no srcset available.\033[0m")
						except requests.RequestException as e:
							print(f"\033[91mRequest error for second fallback URLs. Error: {e}\033[0m")

				# If still no valid image found
				if not image_url_valid:
					print("\033[91mNo valid image URL found for this article.\033[0m")

				# Article Content (the main body of the article)
				section = soup.find('section', id='inq_section')
				content = []
				if section:
					for tag in section.find_all(["p", "h2"]):
						if tag.name == "h2":
							content.append(f'## {tag.get_text().strip()}')
						elif tag.name == 'p':
							paragraph_text = tag.get_text()
							if "Subscribe to our daily newsletter" in paragraph_text or \
							   "Subscribe to our newsletter!" in paragraph_text or \
							   "By providing an email address. I agree to the Terms of Use and acknowledge that I have read the Privacy Policy." in paragraph_text:
								continue
							content.append(paragraph_text)

				# Initialize markdown content string
				md_content = f"**{art_type}**\n\n"
				md_content += f"# {entry_title}\n\n"
				md_content += f"****{authorship}****\n\n"
				if image_url_valid:
					md_content += f"![Image](https://raw.githubusercontent.com/github-jl14/scrapy_api/refs/heads/main/images/{image_filename})\n\n"
				if content:
					md_content += "\n\n".join(content)
				else:
					md_content += "\nNo content available."

				# Save to markdown file
				filename = f"{postdate}_{clean_title}.md"
				filepath = os.path.join(output_dir, filename)
				with open(filepath, "w", encoding="utf-8") as md_file:
					md_file.write(md_content)

				print(f"Saved article to file: {filename}")
			else:
				print(f"\033[91mFailed to fetch article: {url} (HTTP {response.status_code})\033[0m")
		except requests.RequestException as e:
			print(f"\033[91mRequest error while fetching article: {url}. Error: {e}\033[0m")
		except Exception as e:
			print(f"\033[91mUnexpected error while processing article: {url}. Error: {e}\033[0m")

	print("Article scraping completed.")

if __name__ == '__main__':
	now()