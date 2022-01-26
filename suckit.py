import argparse
import requests
import sys 
import urllib.request
from lxml import html
import json
import os
import errno

print("""
  ____  _   _  ____ _  _____ _____ _      __     ______                                  _    
 / ___|| | | |/ ___| |/ /_ _|_   _| |    / / __ / /  _ \  ___ _ __  _ __ ___   __ _ _ __| | __
 \___ \| | | | |   | ' / | |  | | | |   / / '__/ /| | | |/ _ \ '_ \| '_ ` _ \ / _` | '__| |/ /
  ___) | |_| | |___| . \ | |  | | |_|  / /| | / / | |_| |  __/ | | | | | | | | (_| | |  |   < 
 |____/ \___/ \____|_|\_\___| |_| (_) /_/ |_|/_/  |____/ \___|_| |_|_| |_| |_|\__,_|_|  |_|\_\


 - A downloader for saving our favorite shows from radio24syv
""")

def allowed_years(year):
    x = int(year)
    if x > 2019 or x < 2010:
        raise argparse.ArgumentTypeError(f"year '{x}' must be between 2010 and 2019 (both included)")
    return x

parser = argparse.ArgumentParser(description='suckit! => an /r/Denmark radio24syv Downloader')
parser.add_argument('url', type=str, help='For instance: https://www.24syv.dk/programmer/den-korte-radioavis')
parser.add_argument('start_year', type=allowed_years, help='Specify which year to start from')
parser.add_argument('end_year', type=allowed_years, help='Specify which year to end with')
args = parser.parse_args()
url = args.url
years = range(args.start_year, args.end_year)
api_baseurl = "https://api.radio24syv.dk/v2/"
scriptDirectory = os.path.dirname(os.path.realpath(__file__))

print(scriptDirectory)
sys.exit("suckit")

def ensure_download_dir(local_path):
    if not os.path.exists(os.path.dirname(f"{local_path}")):
        try:
            os.makedirs(os.path.dirname(f"{local_path}"))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def update_programs():
    response = requests.get(f"{api_baseurl}programs")
    data = response.text
    with open("programs.json", "w") as f:
        f.write(data) 

def find_podcast(slug):
    with open("programs.json") as f:
        data = json.load(f)
        for podcast in data:
            if podcast["slug"] == slug:
                return podcast

        exit(f"Failed to find podcast based on the slug: {slug}")


def suckit(years):
    print("==== Computer.. Engaging suck-mode ====\n")
    
    #reading file
    slug = url.split('/')[-1]

    selected_podcast = find_podcast(slug)
    program = selected_podcast["videoProgramId"]

    print(f"=> All your podcast are belong to us: {slug} ({program})\n")

    months = ['12','11','10','9','8','7','6','5','4','3','2','1']

    for year in years:
        for month in months:
            print(f"- Sucking {year}-{month}")
            page = requests.get(f"{api_baseurl}podcasts/program/{program}/?year={year}&month={month}")
            page = page.json()
            for p in page:
                audioInfoUrl = p["audioInfo"]["url"]
                print(f"http://arkiv.radio24syv.dk/attachment{audioInfoUrl}?source=websitedownload")
                filename = audioInfoUrl.split("/")[-1]
                createdAt = p["publishInfo"]["createdAt"]
                dl_filename = f"/e/radio24syv/podcasts/{slug}/{year}/{month}/{createdAt}-{filename}"
                ensure_download_dir(dl_filename)
                try:
                    urllib.request.urlretrieve(f"http://arkiv.radio24syv.dk/attachment{audioInfoUrl}?source=websitedownload", f"{dl_filename}")            
                except:
                    print("failed, moving on")

update_programs()
suckit(years)
