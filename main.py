import json
from collections import Counter
from pprint import pprint

import requests
from bs4 import BeautifulSoup


def is_valid(word):
    return "[" not in word and "]" not in word


def extract_lyrics(url):
    print(f"Fetching lyrics {url}...")
    r = requests.get(url)
    if r.status_code != 200:
        print("Page impossible a recuperer.")
        return []

    soup = BeautifulSoup(r.content, 'html.parser')
    lyrics = soup.find("div", class_="lyrics")
    if not lyrics:
        return extract_lyrics(url)

    if "released" in lyrics.stripped_strings:
        return []

    all_words = []
    for sentence in lyrics.stripped_strings:
        sentence_words = [word.strip(",").strip(".").lower() for word in sentence.split() if is_valid(word)]
        all_words.extend(sentence_words)

    return all_words


def get_all_urls():
    page_number = 1
    links = []
    while True:
        r = requests.get(f"https://genius.com/api/artists/1167573/songs?page={page_number}&sort=popularity")
        if r.status_code == 200:
            print(f"Fetching page {page_number}")
            response = r.json().get("response", {})
            next_page = response.get("next_page")

            songs = response.get("songs")
            links.extend([song.get("url") for song in songs])
            page_number += 1

            if not next_page:
                print("No more pages to fetch.")
                break

    return links


def get_all_words():
    urls = get_all_urls()
    words = []
    for url in urls:
        lyrics = extract_lyrics(url=url)
        words.extend(lyrics)

    # with open("data-michel-sardou.json", "w") as f:
    #    json.dump(words, f, indent=4)

    # with open("data.json", "r") as f:
    #     words = json.load(f)

    counter = Counter([w for w in words if len(w) > 5])
    most_common_words = counter.most_common(15)
    pprint(most_common_words)


get_all_words()
