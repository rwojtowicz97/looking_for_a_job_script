from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import csv


my_url = 'https://ogloszenia.trojmiasto.pl/praca-zatrudnie/it-programowanie/'
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()
first_page_soup = soup(page_html, "html.parser")
first_container = first_page_soup.findAll("div", {"class":"list__item__wrap__content"})
last_page = first_page_soup.find("a", {"title":"ostatnia strona"})
last_page_number = int(last_page["data-page-number"])


def add_all_pages(first_container):
    all_pages = first_container
    for page in range(1, last_page_number+1):
        base_url = 'https://ogloszenia.trojmiasto.pl/praca-zatrudnie/it-programowanie/?strona=' + str(page)
        base_url = my_url + '?strona=' + str(page)
        uClient = uReq(base_url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")
        container = page_soup.findAll("div", {"class":"list__item__wrap__content"})
        all_pages = all_pages + container
    return all_pages


containers = add_all_pages(first_container)


with open('jobs.csv', mode='w', newline='') as jobs:
    fieldnames = ['Stanowisko', 'Lokalizacja', 'Pracodawca', 'Link']
    writer = csv.DictWriter(jobs, fieldnames=fieldnames, delimiter=',')
    writer.writeheader()

    position_keywords = ['junior', 'intern', 'młodszy', 'staż']
    location_keywords = ['Praca sezonowa']

    for container in containers:
        position = container.div.a["title"]
        if any(x in position.lower() for x in position_keywords):
            location = container.div.p.text.strip()
            if any(y in location for y in location_keywords):
                location.replace(location_keywords[0], '')
            employer = container.find("p", {"class": "list--item--details--info--work"})
            url_to_offer = container.div.h2.a["href"]
            if employer != None:
                employer = container.find("p", {"class": "list--item--details--info--work"}).text
            else:
                employer = 'Brak'
            writer.writerow(
                {'Stanowisko': position, 'Lokalizacja': location, 'Pracodawca': employer, 'Link': url_to_offer})
        else:
            continue
