from os import name
import requests
import fake_useragent
from bs4 import BeautifulSoup
import time
import json
import urllib.request

def get_links(text):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=f'https://hh.ru/search/resume?text={text}&area=1&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&fromSearchLine=false&page=1',
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
                url=f'https://hh.ru/search/resume?text={text}&area=1&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&fromSearchLine=false&page={page}',
                headers={"user-agent": ua.random}
            )
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, 'lxml')
            for a in soup.find_all("a", attrs={"class": "bloko-link", "target": "_blank"}):
                if f"{a.attrs['href'].split('?')[0]}" != "https://feedback.hh.ru/article/details/id/5951":
                    yield f"https://hh.ru/{a.attrs['href'].split('?')[0]}"
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
        heading = soup.find('span', attrs={"class": "resume-block__title-text"}).text

    except:
        heading = ''

    try:
        work_hours = soup.find('div', attrs={"class": "resume-block-container"}).text.replace('\xa0', ' ').replace('\n', ' ')
    except:
        work_hours = ''

    try:
        experience_stack = soup.find('div', attrs={"data-qa": "resume-block-experience"}).text.replace('\xa0', ' ').replace('\n', ' ')
    except:
        experience_stack = ''

    try:
        elements = soup.find_all('div', attrs={'class': 'bloko-tag bloko-tag_inline'})
        skills = ' '.join(element.get_text(strip=True) for element in elements)
    except:
        skills = ''

    try:
        biography = soup.find('div', attrs={"data-qa": "resume-block-skills-content"}).text.replace('\xa0', ' ').replace('\n', ' ')
    except:
        biography = ''

    try:
        education = soup.find('div', attrs={"data-qa": "resume-block-education"}).text.replace('\xa0', ' ').replace('\n', ' ')
    except:
        education = ''

    try:
        extra_education = soup.find('div', attrs={"data-qa": "resume-block-additional-education"}).text.replace('\xa0', ' ').replace('\n', ' ')
    except:
        extra_education = ''

    resume = {
        'heading': heading,
        'work_hours': work_hours,
        'experience_stack': experience_stack,
        'skills': skills,
        'biography': biography,
        'education': education,
        'extra_education': extra_education
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
            with open('resume.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            counter += 1
            if counter == 20:
                break
