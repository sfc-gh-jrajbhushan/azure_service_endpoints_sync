# src/downloader.py
import logging
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

def download_file(url, file_path):
    logger = logging.getLogger()
    output_file = " "
    logger.info("downloader.py: download_file()")        

    # Custom headers if needed (not necessary today)
    headers = {
        'User-Agent': 'your-user-agent',
        'Authorization': 'Bearer your-token'
    }

    # Make a GET request to the URL, allowing redirection
    response = requests.get(url, headers=headers, allow_redirects=True)

    if response.status_code == 200:
        # Use BeautifulSoup to parse links in the page to identify the download file (download.microsoft.com)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)

        found = False
        for link in links:
            if "download.microsoft.com" in link['href']:
                print(f"Found download link: {link['href']}")
                logger.info(f"Found download link: {link['href']}")
                found = True
                download_url = link['href']
                break
        
        if not found:
            print("'download.microsoft.com' not found in any links.")
        else:
            print("File to be downloaded is at the Link: ", download_url)
            logger.info(f"File to be downloaded is at the Link: {download_url}")

            # Extract the filename from the download url (ServiceTags_Public_<YYYYMMDD>.json)
            parsed_url = urlparse(download_url)
            file_name = os.path.basename(parsed_url.path)
            output_file = os.path.join(file_path, file_name)

            try:
                response = requests.get(download_url)
                response.raise_for_status()  # Check for HTTP errors

                with open(output_file, 'w') as file:
                    file.write(response.text)
                
                print(f"Azure IP addresses successfully downloaded to {output_file}")

            except requests.exceptions.RequestException as e:
                print(f"Error downloading Azure IP addresses: {e}")

    else:
        print("Failed to download the file. Status code:", response.status_code)

    print("output_file:", output_file)
    return [output_file, file_name]

    
