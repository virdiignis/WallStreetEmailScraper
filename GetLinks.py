#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from time import sleep


class GetLinks:
    """
    Gets links to hedge funds and prop companies from wallstreetoasis.com, and saves them to links.txt file.
    """

    @staticmethod
    def get_links():
        links = []
        for i in range(6):
            response = requests.get(
                'http://www.wallstreetoasis.com/wso-company-database?title=&tid[0]=28320&distance[postal_code]=&distance[country]=us&distance[search_distance]=&distance[search_units]=mile&country=All&&&body_value=&page=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,%i' % i)
            links.extend([tab.a['href'] for tab in BeautifulSoup(response.text, 'lxml').find_all('td', {
                'class': 'views-field views-field-title'})])
            sleep(0.5)
        for i in range(26):
            response = requests.get(
                'http://www.wallstreetoasis.com/wso-company-database?title=&tid[0]=39&distance[postal_code]=&distance[country]=us&distance[search_distance]=&distance[search_units]=mile&country=All&&&body_value=&page=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,%i' % i)
            links.extend([tab.a['href'] for tab in BeautifulSoup(response.text, 'lxml').find_all('td', {
                'class': 'views-field views-field-title'})])
            sleep(0.5)
        with open('links.txt', 'w') as fp:
            fp.writelines([str(link + '\n') for link in links])
