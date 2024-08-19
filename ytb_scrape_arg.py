from dotenv import load_dotenv
load_dotenv()
from os import getpid
from sys import argv
from time import sleep
from ytb_scrape import scrape_pipeline

def main():
    if len(argv) <= 1:
        print("[ERROR] too less arguments of urls to scrape.")
        exit()
    pid = getpid()
    for url in argv[1:]:
        print(f"[INFO] now scrape url:{url}")
        sleep(1)
        scrape_pipeline(pid, channel_url=url)

if __name__ == "__main__":
    main()