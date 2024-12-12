import requests
import os

def save(url, filename):
    # Ensure the directory for saving images exists
    os.makedirs('images', exist_ok=True)

    # Set headers to simulate a browser request and include a Referer header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://opinion.inquirer.net/'  # Replace with the page the image is from
    }

    try:
        # Send a GET request to fetch the image
        response = requests.get(url, headers=headers, timeout=10)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the image to the 'images' directory
            with open(f'images/{filename}', 'wb') as file:
                file.write(response.content)
                print(f"{filename} downloaded successfully.")
        else:
            print(f"Failed to retrieve the image. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        # Handle potential errors during the request (e.g., network issues)
        print(f"An error occurred: {e}")

# Example usage:
# save('https://example.com/image.png', 'image.png')