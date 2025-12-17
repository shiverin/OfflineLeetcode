import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# --- CONFIGURATION ---
INPUT_DB_FILE = "database.json"       # Your database file from the scraper
OUTPUT_DB_FILE = "database_offline.json" # The final, processed database
STATIC_DIR = "static"                 # Name of the folder for static assets
IMAGE_SUBDIR = "images"               # Subfolder for downloaded images
# ---------------------

# Headers to avoid 403 errors from Wikimedia or other servers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def download_and_update_images():
    """
    Parses a database file, downloads all images found in HTML content,
    and updates the HTML to point to local copies.
    """

    # Create the directories if they don't exist
    image_dir_path = os.path.join(STATIC_DIR, IMAGE_SUBDIR)
    if not os.path.exists(image_dir_path):
        os.makedirs(image_dir_path)
        print(f"📁 Created directory: {image_dir_path}")

    # Load the database
    try:
        with open(INPUT_DB_FILE, 'r', encoding='utf-8') as f:
            database = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Input file not found at '{INPUT_DB_FILE}'")
        return

    print("🚀 Starting image processing...")

    # Iterate through each problem in the database
    for problem_id, problem_data in database.items():
        if "description" not in problem_data:
            continue

        html_content = problem_data["description"]
        soup = BeautifulSoup(html_content, "html.parser")

        images_found = soup.find_all("img")
        if not images_found:
            continue

        print(f"\nProcessing '{problem_data['title']}'...")

        for img_tag in images_found:
            original_src = img_tag.get("src")
            if not original_src or not original_src.startswith("http"):
                print(f"  - Skipping non-HTTP or empty src: {original_src}")
                continue

            try:
                # Generate a local filename from the URL
                url_path = urlparse(original_src).path
                filename = os.path.basename(url_path)
                local_filepath = os.path.join(image_dir_path, filename)

                # Download the image if it doesn't already exist
                if not os.path.exists(local_filepath):
                    print(f"  - Downloading {original_src}...")
                    response = requests.get(original_src, stream=True, headers=HEADERS)
                    response.raise_for_status()  # Raise an exception for bad status codes
                    with open(local_filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"    -> Saved to {local_filepath}")
                else:
                    print(f"  - Image already exists: {filename}")

                # Update the src attribute to the new local path
                new_src_path = f"/{STATIC_DIR}/{IMAGE_SUBDIR}/{filename}"
                img_tag["src"] = new_src_path

            except requests.exceptions.RequestException as e:
                print(f"  ❌ Failed to download {original_src}: {e}")
            except Exception as e:
                print(f"  ❌ An unexpected error occurred: {e}")

        # Update the problem's description with the modified HTML
        database[problem_id]["description"] = str(soup)

    # Save the updated database to a new file
    with open(OUTPUT_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Success! All images processed. New database saved as '{OUTPUT_DB_FILE}'.")
    print(f"👉 Remember to use '{OUTPUT_DB_FILE}' in your application.")

# --- RUN THE SCRIPT ---
if __name__ == "__main__":
    download_and_update_images()
