import concurrent.futures
import time

import urllib3
import json
from datetime import datetime, timedelta
from pathlib import Path


def get_link_to_archive(site, date_str):
    url = "https://archive.org/wayback/available?url={}&timestamp={}".format(site, date_str)
    http = urllib3.PoolManager()
    request = http.urlopen('GET', url)

    string = request.data.decode()
    # print(string)
    json_data = json.loads(string)
    return json_data['archived_snapshots']['closest']['url']


def get_text_from_link(link):
    from bs4 import BeautifulSoup
    from bs4.element import Comment
    import urllib.request

    def tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def text_from_html(body):
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)

    html = urllib.request.urlopen(link).read()
    return text_from_html(html)


def save_text_to_file(data, filename, name):
    file1 = open("{}/{}.txt".format(filename, name), "w+")
    file1.write(data)


def fileExist(filename, name):
    try:
        f = open("{}/{}.txt".format(filename, name))
        f.close()
        return True
    except IOError:
        return False


def get_archive(date_str, site, site_dir, attempts=10):
    if fileExist(site_dir, date_str):
        return 2

    for x in range(attempts):
        try:
            link = get_link_to_archive(date_str=date_str, site=site)
            text = get_text_from_link(link)
            save_text_to_file(data=text, filename=site_dir, name=date_str)
            return 0
        except:
            time.sleep(2)
    return 1


def get_all_archives_before(site, start_str, end_str):
    site_dir = "sites/" + site
    Path(site_dir).mkdir(parents=True, exist_ok=True)
    start = datetime.strptime(start_str, '%Y%m%d').date()
    end = datetime.strptime(end_str, '%Y%m%d').date()
    current = start
    return current, start, end, site_dir


def generate_dates_between(start, end):
    dates = []
    current = start
    while (current <= end):
        current_str = current.strftime('%Y%m%d')
        dates.append(current_str)
        current = current + timedelta(days=1)
    return dates


def get_all_archives(start_str, end_str, site):
    good, bad, exist = (0, 0, 0)
    threaded_start = time.time()

    current, start, end, site_dir = get_all_archives_before(site, start_str, end_str)
    dates = generate_dates_between(start, end)
    total = len(dates)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for date in dates:
            futures.append(executor.submit(get_archive, date_str=date, site=site, site_dir=site_dir))
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result == 0:
                good += 1
            elif result == 1:
                bad += 1
            elif result == 2:
                exist += 1
            print("good: {}  bad: {}  exist: {}  {}/{} Czas: {}".format(good, bad, exist, good+bad+exist, total, (time.time() - threaded_start) / 60))


threaded_start = time.time()
get_all_archives('20190901', '20201229', 'pap.pl')
print("Threaded time:", (time.time() - threaded_start) / 60)
