#!/usr/bin/env python3
from selenium import webdriver
from bs4 import BeautifulSoup
import csv


class GetData:
    """
    Scrapes data from wallstreetoasis.com. using links.txt. Produces data.csv file with companies information.
    """

    def __init__(self):
        """
        Loads links to scrape.
        """
        self.links = []

        def load_links(filename):
            with open(filename, 'r') as fp:
                for link in fp.readlines():
                    self.links.append('http://www.wallstreetoasis.com%s' % link.strip())

        load_links('prop/links.txt')
        load_links('hedge/links.txt')

    def run(self):
        """
        Runs companies scraping job. Single-processed.
        :return: 0 on success
        """
        chrome = webdriver.Chrome()
        csvfile = open('data.csv', 'w')
        csv_writer = csv.writer(csvfile, dialect='excel')
        for link in self.links:
            chrome.get(link)
            assert chrome.current_url == link, 'We have been redirected?'
            company_name = ' '.join(link.split('/')[-1].split('-')).title()
            b = BeautifulSoup(chrome.page_source, 'lxml')
            try:
                website = b.find('div', {
                    'class': 'field field-name-field-website field-type-link-field field-label-above'}).text[9:]
            except AttributeError:
                website = ''
            try:
                email_convention = b.find('div', {
                    'class': 'field field-name-field-emailconvention field-type-text field-label-above'}).text[18:]
            except AttributeError:
                email_convention = ''
            telephones = []
            for adr in b.find_all('div', {'class': 'adr'}):
                loc = adr.find('span', {'class': 'locality'})
                phon = adr.find('span', {'itemprob': 'telephone'})
                if loc and phon:
                    telephones[loc.text.strip()] = phon.text.strip()
            boston = 'boston' in str(b.find('div', {'class': 'node-content clear-block'}).text).lower()
            ma = any([i in str(b.find('div', {'class': 'node-content clear-block'}).text).lower() for i in
                      (' ma ', 'massachusetts')])
            ct = any([i in str(b.find('div', {'class': 'node-content clear-block'}).text).lower() for i in
                      (' ct ', 'connecticut')])
            ny = any([i in str(b.find('div', {'class': 'node-content clear-block'}).text).lower() for i in
                      ('ny', 'new york')])
            csv_writer.writerow([company_name, website, email_convention, boston, ma, ct, ny, str(telephones)])
        csvfile.close()
        chrome.close()
        return 0
