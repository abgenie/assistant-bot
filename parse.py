import urllib3
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup


urllib3.disable_warnings()


def main():

    articles_gazprom = parse_gazprom('https://gazprombank.investments/blog/')
    write_articles_to_file('ГАЗПРОМБАНК', articles_gazprom)

    articles_tinkoff = parse_tinkoff('https://www.tinkoff.ru/invest/research/all/')
    write_articles_to_file('ТИНЬКОФФ', articles_tinkoff)

    articles_dohod = parse_dohod('https://www.dohod.ru/analytic/research')
    write_articles_to_file('ДОХОД', articles_dohod)


def write_articles_to_file(title: str, articles: list[str]) -> None:
    """Сохраняет полученные данные в файл"""
    with open('message.txt', 'a', encoding='utf8') as f:
        f.write(title + '\n')
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


def parse_gazprom(url: str) -> list[str]:
    """Парсит данные с сайта 'https://gazprombank.investments'"""

    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}, verify=False).text
    soup = BeautifulSoup(response, 'html.parser')

    articles = []

    section = soup.find('div', 'blog-grid')

    wide_card = section.find('a', 'article-wide__link')
    article_date = string_to_date(wide_card.find('span', 'stats__creation-date').text)
    article_link = url + wide_card['href'][6:]
    article_title = wide_card.find('h1').text.strip()

    articles.append(f'{article_date}\n<a href="{article_link}">{article_title}</a>\n')

    cards = section.find_all('a', 'article-card__link')
    for card in cards:
        article_date = string_to_date(card.find('span', 'stats__creation-date').text)
        article_link = url + card['href'][6:]
        article_title = card.find('h3').text.strip()

        articles.append(f'{article_date}\n<a href="{article_link}">{article_title}</a>\n')

    return articles


def parse_tinkoff(url: str) -> list[str]:
    """Парсит данные с сайта 'https://www.tinkoff.ru'"""

    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}, verify=False)
    response.encoding = 'UTF-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    cards = soup.find_all('a', 'Link-module__link_UWSCx Link-module__link_theme_default_s_i0Q')[:6]
    for card in cards:
        article_date = string_to_date(card.find('div', 'ResearchCatalogNews__date_Irh8b').text)
        article_link = card['href']
        article_title = card.find('div', 'ResearchCatalogNews__title_c1Sx2').text.strip()

        articles.append(f'{article_date}\n<a href="{article_link}">{article_title}</a>\n')

    return articles


def parse_dohod(url: str) -> list[str]:
    """Парсит данные с сайта 'https://www.dohod.ru'"""

    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}, verify=False).text
    soup = BeautifulSoup(response, 'html.parser')

    articles = []

    cards = soup.find_all('a', 'clr-black t-tdn products__slide slider-main__slide '
                               'swiper-slide products__slide--chart bg-white products__analytic_blog_item')

    for card in cards:
        article_date = string_to_date(card.time.text)
        article_link = 'https://www.dohod.ru/' + card['href']
        article_title = card.h4.text.strip()

        articles.append(f'{article_date}\n<a href="{article_link}">{article_title}</a>\n')

    return articles


if __name__ == '__main__':
    main()
