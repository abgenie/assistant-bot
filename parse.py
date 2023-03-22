import urllib3
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from data import *

urllib3.disable_warnings()
from_what_date_to_parse = date.today() - timedelta(days=how_many_days_ago_to_parse)


def main():

    # Проходим по всем разделам всех сайтов
    write_title_to_file('Газпромбанк')
    for url in GAZPROM_BLOGS:
        parse_gazprom(url)

    write_title_to_file('Открытие')
    for url in OPEN_BLOGS:
        parse_open(url)

    write_title_to_file('Доход')
    for url in DOHOD:
        parse_dohod(url)

    write_title_to_file('Тинькофф')
    parse_tinkoff(TINKOFF)


def select_sort_new_for_open(url: str) -> BeautifulSoup:
    """Выбирает метод сортировки статей 'Сначала новое',
    возвращает объект 'BeautifulSoup' с отсортированными статьями"""
    options = Options()
    options.arguments.append('-headless')
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    # Переключаем метод сортировки записей 'Сначала новое'
    driver.find_element(By.ID, 'multiselect').click()
    driver.find_element(By.CLASS_NAME, 'DropdownRow_content__2VdTx').click()

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    driver.close()
    return soup


def write_title_to_file(title: str) -> None:
    """Записывает название сайта в файл"""
    with open(filename, 'a', encoding='utf8') as f:
        f.write(f'<strong>{title}</strong>\n')


def write_articles_to_file(section_title: str, articles: list[str]) -> None:
    """Сохраняет полученные данные в файл"""
    with open(filename, 'a', encoding='utf8') as f:
        f.write(section_title + '\n')
        for article in articles:
            f.write(article)
        f.write('\n')


def string_to_date(date_str: str) -> date:
    """Преобразует строку вида '01 января 2023' в объект 'date'.
    При неудаче вызывает ошибку 'MonthRecognitionError'
    """

    if 'Сегодня' in date_str:
        return date.today()
    elif 'Вчера' in date_str:
        return date.today() - timedelta(days=1)
    day, month, year = date_str.split()
    match month:
        case 'января':
            month = 1
        case 'февраля':
            month = 2
        case 'марта':
            month = 3
        case 'апреля':
            month = 4
        case 'мая':
            month = 5
        case 'июня':
            month = 6
        case 'июля':
            month = 7
        case 'августа':
            month = 8
        case 'сентября':
            month = 9
        case 'октября':
            month = 10
        case 'ноября':
            month = 11
        case 'декабря':
            month = 12
        case _:
            # Если не получится распознать месяц указываем декабрь,
            # дата скорее всего будет из будущего, что будет заметно в сообщении
            month = 12

    return date(int(year), month, int(day))


def parse_gazprom(url: str) -> None:
    """Парсит данные с сайта 'https://gazprombank.investments'"""

    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}, verify=False).text
    soup = BeautifulSoup(response, 'html.parser')

    section_title = soup.h1.text.upper()

    articles = []
    cards = soup.find_all('a', 'card')
    for card in cards:
        # Получаем дату и сравниваем с датой последнего парсинга
        article_date = string_to_date(card.find('span', 'card-date').text)
        if article_date < from_what_date_to_parse:
            continue

        article_link = url + card['href'].split('/')[-2]
        article_title = card.find('span', 'card-title').text.strip()

        articles.append(f'{article_date}\n<a href="{article_link}">{article_title}</a>\n')

    if articles:
        write_articles_to_file(section_title, articles)


def parse_open(url: str) -> None:
    """Парсит данные с сайта 'https://journal.open-broker.ru'"""

    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}, verify=False).text
    soup = BeautifulSoup(response, 'html.parser')

    section_title = soup.h1.text.upper()

    # Если сортировка не по дате, то переключаем её с помощью Selenium и возвращаем новый soup
    if not soup.find('span', 'MultiSelect_multiselectText__38MZ5').text == 'Сначала новое':
        soup = select_sort_new_for_open(url)

    articles = []
    cards = soup.find_all('a', 'CardSmall_card__1SmUx Category_rootArticle__1XgQa')
    for card in cards:
        # Получаем дату и проверяем, сравниваем с датой последнего парсинга
        raw_date = card.find('p', 'CardSmall_noWrap__3I1yt Paragraph-module__paragraph--g4xw7 '
                                  'Paragraph-module__paragraph--p4--uYcdM '
                                  'Paragraph-module__paragraph--fixed_60--Mqv6o').text[:-8]

        try:
            # Проверяем указан ли в конце год
            int(raw_date[-4:])
        except ValueError:
            # Если не указан, добавляем текущий год
            raw_date += ' ' + str(date.today().year)

        article_date = string_to_date(raw_date)
        if article_date < from_what_date_to_parse:
            break

        article_link = url + card['href'].split('/')[-2]
        article_title = card.find('p', 'CardSmall_cardTitle__bv6e3 Paragraph-module__paragraph--g4xw7 '
                                       'Paragraph-module__paragraph--p1--iBqRO').text
        article_title = article_title.replace(' ', ' ').strip()

        articles.append(f'{article_date}\n<a href="{article_link}">{article_title}</a>\n')

    if articles:
        write_articles_to_file(section_title, articles)


def parse_dohod(url: str) -> None:
    """Парсит данные с сайта 'https://www.dohod.ru'"""

    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}, verify=False).text
    soup = BeautifulSoup(response, 'html.parser')

    section_title = soup.h1.text.upper()

    articles = []
    if url == 'https://www.dohod.ru/analytic/research':
        cards = soup.find_all('a', 'clr-black t-tdn products__slide slider-main__slide '
                                   'swiper-slide products__slide--chart bg-white products__analytic_blog_item')
    else:
        cards = soup.find_all('a', 't-tdn article__link')

    for card in cards:
        if url == 'https://www.dohod.ru/analytic/research':
            article_date = string_to_date(card.time.text)
        else:
            list_date = [int(x) for x in card.time['datetime'].split('-')]
            article_date = date(*list_date)

        if article_date < from_what_date_to_parse:
            break

        article_link = 'https://www.dohod.ru/' + card['href']
        article_title = card.h4.text.strip()

        articles.append(f'{article_date}\n<a href="{article_link}">{article_title}</a>\n')

    if articles:
        write_articles_to_file(section_title, articles)


def parse_tinkoff(url: str) -> None:
    """Парсит данные с сайта 'https://www.tinkoff.ru'"""

    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}, verify=False)
    response.encoding = 'UTF-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    cards = soup.find_all('a', 'Link-module__link_UWSCx Link-module__link_theme_default_s_i0Q')
    for card in cards:
        # Получаем дату и проверяем, сравниваем с датой последнего парсинга
        article_date = string_to_date(card.find('div', 'ResearchCatalogNews__date_Irh8b').text)
        if article_date < from_what_date_to_parse:
            break

        article_link = card['href']
        article_title = card.find('div', 'ResearchCatalogNews__title_c1Sx2').text.strip()

        articles.append(f'{article_date}\n<a href="{article_link}">{article_title}</a>\n')

    if articles:
        write_articles_to_file('Все статьи', articles)


if __name__ == '__main__':
    main()
