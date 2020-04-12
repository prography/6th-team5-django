import datetime
import json
import re
import os
import sys

from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from concertinfo.models import *


INTERPARK_BASE_URL = 'http://ticket.interpark.com/'
INTERPARK_NOTICE_URL = 'webzine/paper/TPNoticeList.asp'
INTERPARK_CATEGORY_URLS = {
    'BALLAD': 'TPGoodsList.asp?Ca=Liv&SubCa=Bal',
    'ROCK_METAL': 'TPGoodsList.asp?Ca=Liv&SubCa=Roc',
    'RAP_HIPHOP': 'TPGoodsList.asp?Ca=Liv&SubCa=Rap',
    'JAZZ_SOUL': 'TPGoodsList.asp?Ca=Liv&SubCa=Jaz',
    'DINNER': 'TPGoodsList.asp?Ca=Liv&SubCa=Din',
    'PORK_TROT': 'TPGoodsList.asp?Ca=Liv&SubCa=Por',
    'FOREIGN': 'TPGoodsList.asp?Ca=Liv&SubCa=For',
    'FESTIVAL': 'TPGoodsList.asp?Ca=Liv&SubCa=Fes',
    'INDIE': 'TPGoodsList.asp?Ca=Liv&SubCa=Ind',
}
INTERPARK_PRICE_URL = 'Ticket/Goods/GoodsInfoJSON.asp?Flag=SalesPrice&GoodsCode={}'

random_agent = UserAgent().random
headers = {'User-Agent': random_agent, 'Referer': INTERPARK_BASE_URL}


class InterparkCrawl:
    '''
        인터파크 크롤링을 위한 클래스.
        크게 다음 2가지를 크롤링한다.
        1. 판매중 페이지
        2. 티켓오픈 공지 페이지
    '''
    def __openedConcertsDetailUrls(self, category):
        '''
            판매중 페이지에서 해당하는 카테고리에 속한 모든 공연의 상세페이지 URL이 담긴 리스트를 반환한다.

            :param str category: 카테고리

            :return: 해당 카테고리의 공연 URL 리스트
        '''
        category_url = INTERPARK_BASE_URL + INTERPARK_CATEGORY_URLS[category]

        html_text = requests.get(category_url, headers=headers).text
        soup = BeautifulSoup(html_text, 'html.parser')
        short_urls = soup.findAll('span', class_='fw_bold')
        full_urls = [INTERPARK_BASE_URL + short_url.a['href'] for short_url in short_urls]
        return full_urls

    def __openedConcertInfo(self, detail_url):
        '''
            판매중인 공연의 상세페이지의 공연 정보가 담긴 딕셔너리를 반환한다.

            :param str detail_url: 공연 상세페이지 URL
            
            :return: 해당 공연 정보가 담긴 딕셔너리
        '''
        html_text = requests.get(detail_url, headers=headers).text
        soup = BeautifulSoup(html_text, 'html.parser')
        general = json.loads(soup.find('script', type='application/ld+json').text)

        goods_code = detail_url[-8:]
        price_html_text = requests.get(
                INTERPARK_BASE_URL + INTERPARK_PRICE_URL.format(goods_code),
                headers=headers).text
        price_re = re.search(r'^Callback\((.*)\);$', price_html_text).groups()[0]
        price = json.loads(price_re)['JSON']

        return {'general': general, 'price': price}

    def __createOpenedConcert(self, url, concert_title, info):
        '''
            판매중 상세페이지에서 추출한 정보를 처리하여 Concert 모델을 반환한다.

            :param str url: 공연 상세페이지 URL
            :param str concert_title: 공연 제목
            :param dict info: 공연 정보가 담긴 딕셔너리 (__openedConcertInfo의 반환값)

            :return: 생성한 Concert 모델
        '''
        concert = Concert(
                detail_url=url,
                title=concert_title,
                location=info['general']['location']['name'],
                start_date=datetime.datetime.strptime(info['general']['startDate'], '%Y%m%d').date(),
                end_date=datetime.datetime.strptime(info['general']['endDate'], '%Y%m%d').date(),
                is_opened=True,
                open_time=None,
                )
        return concert

    def __createPrice(self, price_each, concert):
        '''
            판매중 상세페이지에서 추출한 정보를 처리하여 Price 모델을 반환한다.

            :param dict price_each: 가격 정보가 담긴 딕셔너리
            :param Concert concert: 해당 가격 정보에 대응되는 Concert 모델

            :return: 생성한 Price 모델
        '''
        price = Price(
                price_type=price_each['SeatGradeName'],
                price=price_each['SalesPrice'],
                concert=concert,
                )
        return price

    def __createArtist(self, artist_name, genre):
        '''
            멜론 가수 상세정보 페이지에서 추출한 정보를 처리하여 Artist 모델을 반환한다.

            :param str artist_name: 가수명
            :param Genre genre: 해당 가수에 대응되는 Genre 모델

            :return: 생성한 Artist 모델
        '''
        artist = Artist(
                name=artist_name,
                genre=genre,
                )
        return artist
        
    def __createGenre(self, genre_name):
        '''
            새로운 Genre 모델을 반환한다.

            :param str genre_name: 장르명

            :return: 생성한 Genre 모델
        '''
        genre = Genre(name=genre_name)
        return genre
        
    def __createConcertArtist(self, concert, artist):
        '''
            Concert - Artist 중개 테이블인 ConcertArtist를 반환한다.

            :param Concert concert: 짝지을 Concert 모델
            :param Artist artist: 짝지을 Artist 모델

            :return: 생성한 ConcertArtist 모델
        '''
        ca = ConcertArtist(
                concert=concert,
                artist=artist,
                )
        return ca
        
    def __createConcertGenre(self, concert, genre, priority):
        '''
            Concert - Genre 중개 테이블인 ConcertGenre를 반환한다.

            :param Concert concert: 짝지을 Concert 모델
            :param Genre genre: 짝지을 Genre 모델
            :param int priority: 해당 콘서트에 대한 장르 우선순위

            :Return: 생성한 ConcertGenre 모델
        '''
        cg = ConcertGenre(
                concert=concert,
                genre=genre,
                priority=priority,
                )
        return cg

    def __searchArtistInMelon(self, artist):
        '''
            Selenium webdriver를 초기화한 뒤 멜론에서 가수명을 검색한다.

            :return: 해당 webdriver 객체
        '''
        print(f'Started searching {artist}')
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={random_agent}')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', options=options)
        driver.get(f'https://www.melon.com/search/artist/index.htm?q={artist}&section=&searchGnbYn=Y&kkoSpl=N&kkoDpType=&ipath=srch_form#params%5Bq%5D={artist}&params%5Bsq%5D=&params%5Bsort%5D=hit&params%5Bsection%5D=all&params%5Bsex%5D=&params%5BactType%5D=&params%5Bdomestic%5D=&params%5BgenreCd%5D=&params%5BactYear%5D=&po=pageObj&startIndex=1')
        return driver

    def __findArtistGenre(self, artist, driver):
        '''
            멜론 가수 상세정보 페이지에서 해당 가수의 장르를 찾아 반환한다.

            :param str artist: 가수명
            :param webdriver driver: webdriver 객체
            
            :return: 장르명
        '''
        wait = WebDriverWait(driver, 10)
       
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ellipsis')))
        driver.find_element_by_class_name('ellipsis').click()
        artist_id = re.search(r'(artistId=)(\d+)', driver.current_url).groups()[1]
        artist_detail_url = f'https://www.melon.com/artist/detail.htm?artistId={artist_id}'

        driver.get(artist_detail_url)
        html_text = driver.page_source
        driver.quit()
        soup = BeautifulSoup(html_text, 'html.parser')
        artist_infos = soup.findAll('dl', class_='list_define clfix')
        info_str = ''
        for info in artist_infos:
            info_str += str(info)
        return re.search(r'(장르</dt>\n<dd>)([^, <]+)', info_str).groups()[1]

    def __orderGenres(self, genres):
        '''
            장르 등장 빈도수가 높은 순서대로 정렬한 리스트를 반환한다.

            :param list genres: 각 항목의 우선순위가 동일하며 중복이 존재할 수 있는 장르 리스트
            
            :return: 입력받은 리스트의 항목을 등장 빈도수가 높은 순서대로 정렬한 리스트

            ex) __orderGenres(['Rock', 'Electronic', 'Hiphop', 'Hiphop', 'Hiphop', 'Rock']) == ['Hiphop', 'Rock', 'Electronic']
        '''
        counted_genres = []
        genre_count = {}
        for genre in genres:
            if genre not in counted_genres:
                genre_count.setdefault(genre, genres.count(genre))
                counted_genres.append(genre)

        sorted_genre_count = sorted(genre_count.items(), key=lambda item: item[1], reverse=True)
        return [a[0] for a in sorted_genre_count]

    def saveOpenedConcerts(self, category):
        '''
            판매중 공연에서 해당 카테고리에 속하는 모든 공연과 관련 정보들을 저장한다.

            :param str category: 카테고리
        '''
        already_saved_concerts = [model.title for model in Concert.objects.all()]
        already_saved_artists = [model.name for model in Artist.objects.all()]
        already_saved_genres = [model.name for model in Genre.objects.all()]

        for url in self.__openedConcertsDetailUrls(category):
            price = None
            genre = None
            artist = None
            ca = None
            info = self.__openedConcertInfo(url)
            concert_title = info['general']['name']
            if concert_title not in already_saved_concerts:
                concert = self.__createOpenedConcert(url, concert_title, info)

                new_prices = []
                new_price_models = []
                for price_each in info['price']:
                    price_type = price_each['SeatGradeName']
                    if price_type not in new_prices:
                        price = self.__createPrice(price_each, concert)
                        new_prices.append(price.price_type)
                        new_price_models.append(price)

                new_artists = []
                for artist_name in info['general']['performer']['name'].split(','):
                    if artist_name == '':
                        pass
                    else:
                        if artist_name not in already_saved_artists:
                            driver = self.__searchArtistInMelon(artist_name)
                            artist_genre = self.__findArtistGenre(artist_name, driver)
                            
                            if artist_genre not in already_saved_genres:
                                genre = self.__createGenre(artist_genre)
                                genre.save()
                                print(f'Saved genre: {genre.name}')
                                already_saved_genres.append(genre.name)
                            else:
                                genre = Genre.objects.get(name=artist_genre)
                            artist = self.__createArtist(artist_name, genre)
                        else:
                            artist = Artist.objects.get(name=artist_name)
                        if artist not in new_artists:
                            new_artists.append(artist)
                        
                        ca = self.__createConcertArtist(concert, artist)

                genres = [artist.genre.name for artist in new_artists]
                concert_genres = self.__orderGenres(genres)
                
                priority = 0
                new_cgs = []
                for genre_str in concert_genres:
                    genre = Genre.objects.get(name=genre_str)
                    cg = self.__createConcertGenre(concert, genre, priority)
                    priority += 1
                    new_cgs.append(cg)
                
                for artist in new_artists:
                    artist.save()
                    print(f'Saved artist: {artist.name}')
                    already_saved_artists.append(artist.name)
                concert.save()
                print(f'Saved concert: {concert.title}')
                already_saved_concerts.append(concert.title)
                for price in new_price_models:
                    price.save()
                    print(f'Saved price: {price.price_type}')
                if ca is not None:
                    ca.save()
                for cg in new_cgs:
                    if cg is not None:
                        cg.save()

    def __noticedConcertsDetailUrls(self):
        '''
            티켓오픈 공지 페이지의 모든 상세페이지 URL이 담긴 리스트를 반환한다.

            :return: 오픈예정 공연 URL 리스트
        '''
        pass

    def __noticedConcertInfo(self, detail_url):
        '''
            오픈예정 공연의 정보가 담긴 딕셔너리를 반환한다.

            :param str detail_url: 공연 상세페이지 URL
            
            :return: 해당 공연 정보가 담긴 딕셔너리 
        '''
        pass

    def saveNoticedConcerts(self):
        '''
            모든 오픈예정 공연과 관련 정보들을 저장한다.
        '''
        pass


if __name__ == '__main__':
    inpark = InterparkCrawl()
    for category in INTERPARK_CATEGORY_URLS.keys():
        print(f'Started crawling {category}')
        inpark.saveOpenedConcerts(category)
        print(f'Ended crawling {category}')
#    print('Started crawling notice')
#    inpark.saveNoticedConcerts()
#    print('Ended crawling notice')
