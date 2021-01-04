import PTN
from rotten_tomatoes_client import RottenTomatoesClient
import webbrowser
import os
import sys
import logging
import json
from pathlib import Path
import urllib

ROTTEN_BASE_URL = "https://www.rottentomatoes.com/"
ROTTEN_SEARCH_URL = "https://www.rottentomatoes.com/search?search="

FILMWEB_SEARCH_URL = "https://www.filmweb.pl/search?q="
IMDB_SEARCH_URL = "https://www.imdb.com/find?q="

url = 'http://docs.python.org/'

# Windows
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'


def get_shows(data, title):
    shows = data.get("tvSeries")
    if shows:
        return ROTTEN_BASE_URL + shows[0].get("url")


def choose_closest_movie_by_year(elements, year):
    last = 0
    last_elem = None
    for f in elements:
        current = f["year"]
        if current == year:
            return f
        if current < year:
            last = year - current
            last_elem = f
        else:
            return f if ((current - year) <= last) else last_elem


def rotten_url(element):
    return ROTTEN_BASE_URL + element.get("url")


def rotten_search(url):
    return ROTTEN_SEARCH_URL + url


def get_movies(data, title, year):
    movies = data.get("movies")

    if len(movies) == 0:
        return rotten_search(title + " " + str(year))

    if len(movies) == 1:
        return rotten_url(movies[0])

    filtered_titles = []

    for m in movies:
        if title == m["name"]:
            filtered_titles.append(m)

    filtered_titles.sort(key=lambda b: b["year"])
    if len(filtered_titles) == 1:
        return rotten_url(filtered_titles[0])
    closest = choose_closest_movie_by_year(filtered_titles, year)
    return rotten_url(closest) if closest is not None else rotten_url(movies[0])


def process(name, only_rotten):
    logging.debug("Process: " + name)
    if name:
        info = PTN.parse(name)
        logging.debug("Parsed torrent name: ")
        logging.debug(json.dumps(info, sort_keys=True, indent=3))
        title = info.get('title')
        year = info.get('year') if info.get('year') else ""
        search = RottenTomatoesClient.search(title, limit=20)
        logging.debug("Search result: ")
        logging.debug(json.dumps(search, sort_keys=True, indent=3))

        if len(search["tvSeries"]) != 0 and ("season" in info or "episode" in info):
            result_url = get_shows(search, title)
        else:
            result_url = get_movies(search, title, year)
        show_url = result_url

        logging.debug(title)
        logging.debug(ROTTEN_BASE_URL + show_url)

        webbrowser.get(chrome_path).open(show_url)
        if not only_rotten:
            webbrowser.get(chrome_path).open(FILMWEB_SEARCH_URL + title + " " + str(year))
            webbrowser.get(chrome_path).open(IMDB_SEARCH_URL + title + " " + str(year))
        print(info)


def handle_path(path):
    if os.path.isdir(path):
        logging.info("Got directory")
        return Path(path).parts[-1]
    elif os.path.isfile(path):
        logging.info("Got file")
        return Path(path).name.stem


if __name__ == '__main__':
    deb = 0
    logging.basicConfig(filename=os.path.dirname(sys.argv[0]) + os.sep + "log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logging.info("Start")
    path = "Z:\\Torrents\\Beautiful.Boy.2018.MULTi.1080p.BluRay.x264-PTRG"

    logging.debug(sys.argv)
    if deb:
        target = handle_path(path)
    else:
        if len(sys.argv) < 2:
            logging.debug("No path given")
            sys.exit(1)
        target = handle_path(sys.argv[1])

    if len(sys.argv) == 3:
        logging.debug("Only Rotten mode")
        process(target, True)
    else:
        process(target, False)
