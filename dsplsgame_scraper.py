import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

def get_game_links(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    
    game_links = []
    for a_tag in soup.select('.post-title a'):
        if a_tag and 'category' not in a_tag['href']:
            game_links.append(a_tag['href'])
    
    print(f"Found {len(game_links)} game links on the page.")
    return game_links

def extract_download_links(game_url):
    response = requests.get(game_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    mediafire_links = []
    for a_tag in soup.find_all('a', href=True):
        if 'mediafire.com' in a_tag['href']:
            mediafire_links.append(a_tag['href'])
    
    print(f"Found {len(mediafire_links)} MediaFire links for {game_url}")
    return mediafire_links

def extract_game_metadata(game_url):
    response = requests.get(game_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.find('h1', class_='post-title').text.strip() if soup.find('h1', class_='post-title') else 'Unknown'
    cover_img = soup.find('img', {'src': re.compile(r'\.jpg|\.png')})
    cover_url = cover_img['src'] if cover_img else ''
    
    metadata = {
        "name": title,
        "cover_url": cover_url,
    }
    
    text_content = soup.get_text()
    patterns = {
        "title_id": r"(CUSA\d+)",
        "region": r"\b(EUR|USA|JPN)\b",
        "size": r"(\d+(?:\.\d+)?\s*(?:GB|MB))",
        "version": r"Version\s*(\d+\.\d+)",
        "release": r"Release\s*:\s*(\d{4})",
        "min_fw": r"Firmware\s*:\s*(\d+\.\d+)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text_content, re.IGNORECASE)
        if match:
            if key == "size":
                metadata[key] = match.group(0)
            else:
                metadata[key] = match.group(1)
    return metadata

def scrape_dlpsgame():
    base_url = "DLPSGAME_LINK_HERE"
    page = 1
    data = {"DATA": {}}
    
    # Ensure JSON file exists
    if not os.path.exists("games.json"):
        with open("games.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    while True:
        print(f"Scraping page {page}...")
        page_url = f"{base_url}{page}/"
        response = requests.get(page_url)
        
        if response.status_code == 404 or "Nothing Found" in response.text:
            print("No more pages to scrape.")
            break
        
        game_links = get_game_links(response)
        if not game_links:
            print("No games found on this page, stopping.")
            break
        
        for game_url in game_links:
            print(f"Extracting {game_url}")
            mediafire_links = extract_download_links(game_url)
            metadata = extract_game_metadata(game_url)
            
            with open("games.json", "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {"DATA": {}}
            
            for link in mediafire_links:
                data["DATA"][link] = metadata
            
            with open("games.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"Added {len(mediafire_links)} links to JSON file.")
            time.sleep(1)
        
        page += 1
    
    print("Scraping complete. Data saved to games.json")

scrape_dlpsgame()
