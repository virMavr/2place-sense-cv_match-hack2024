from os import name
import requests
import fake_useragent
from bs4 import BeautifulSoup
import time
import json
import urllib.request

def get_links(text): # text - запрос, по которому ищутся вакансии в hh.ru
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=f'https://hh.ru/search/vacancy?text={text}&area=1&page=1',
        headers={"user-agent": ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, 'lxml')

    try:
        page_count = int(soup.find("div", attrs={"class": "pager"}).find_all("span", recursive=False)[-1].find("a").find("span").text)
    except:
        return

    for page in range(page_count):
        try:
            data = requests.get(
                url=f'https://hh.ru/search/vacancy?text={text}&area=1&page={page}',
                headers={"user-agent": ua.random}
            )
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, 'lxml')
            for a in soup.find_all("a", attrs={"class": "bloko-link", "target": "_blank"}):
                if f"{a.attrs['href'].split('?')[0]}" != "https://feedback.hh.ru/article/details/id/5951":
                    yield f"{a.attrs['href'].split('?')[0]}"
        except Exception as e:
            print(f"{e}")
        time.sleep(1)


def get_resume(link):
    fp = urllib.request.urlopen(link)
    mybytes = fp.read()

    mystr = mybytes.decode("utf8")
    fp.close()

    soup = BeautifulSoup(mystr, 'html.parser')

    try:
        name = soup.find('h1', attrs={"data-qa": "vacancy-title"}).text
    except:
        name = ''
    try:
        description = soup.find('div', attrs={"data-qa": "vacancy-description"}).text
    except:
        description = ''
    try:
        company = soup.find('span', attrs={"class": "vacancy-company-name"}).text.replace('\xa0', '')
    except:
        company = ''

    resume = {
        'name': name,
        'company': company,
        'description': description
    }

    return resume


counter = 0
data = []
spheres = ['python', 'C++ программист', 'Data science', 'Web-дизайн', 'Web программист', 'ML инженер', 'Разработчик игр', 'Сисадмин', 'Информационная безопасность', 'Менеджер', 'Финансист']
for job in spheres:
    counter = 0
    for a in get_links(job):
        if a != 'https://adsrv.hh.ru/click':
            data.append(get_resume(a))
            time.sleep(1)
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            counter += 1
            if counter == 50:
                break
