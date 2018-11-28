#!/usr/bin/env python3
from selenium import webdriver
import csv
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
from multiprocessing import Process, Queue
from multiprocessing.queues import Empty
import os
from bs4 import BeautifulSoup
import re
from antigate import AntiGate, AntiGateError
from PIL import Image

PASS = 0##########  # Is standard pass to connect.data.com accounts.
API_KEY = ''##################### # Key to anti-captcha.com API


class GetContacts:
    """
    Scrapes contacts from connect.data.com by company search. Takes names from data.csv,
    but omits ones specified in done.txt.
    """

    def __init__(self):
        self.csv = Queue()
        with open('done.txt') as fp:
            done = [i.strip() for i in fp]
        with open('data.csv', newline='') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row[0] not in done:
                    self.csv.put(row)
        self.proxies = Queue()
        with open('proxy.txt') as fp:
            for line in fp:
                self.proxies.put(line)
        self.accounts = Queue()
        with open('O2Accounts.txt') as fp:
            [self.accounts.put(l.strip()) for l in fp]

    def run(self, processes_number):
        """
        Runs scraping. Takes results from subprocesses and writes them to data2.csv
        :param processes_number: number of processes to simultaneously scrape with
         (be carefull not to exceed number of accounts).
        :return: 0 on success
        """
        display = Display(visible=0, size=(1024, 768))
        display.start()
        csv_file = open('data2.csv', 'a', newline='')
        csv_writer = csv.writer(csv_file)
        procs = []
        for i in range(processes_number):
            q = Queue()
            p = Process(target=self.scrap, args=(q, self.proxies.get()))
            p.start()
            procs.append([p, q])
            sleep(1)
        while any([p.is_alive() for p, q in procs]):
            for p, q in procs:
                while not q.empty():
                    csv_writer.writerow(q.get())
            sleep(1)
        csv_file.close()
        display.stop()
        return 0

    def scrap(self, results, proxy):
        """
        Single scraping process. 
        :param results: Queue to put scraped results in.
        :param proxy: String with proxy address and port 'IP:port' 
        :return: 0 on success
        """
        pid = os.getpid()
        opts = webdriver.ChromeOptions()
        opts.add_argument('--no-sandbox')
        opts.add_argument('--proxy-server=%s' % proxy)
        chrome = webdriver.Chrome(chrome_options=opts)
        wait = WebDriverWait(chrome, 10)

        def login():
            chrome.delete_all_cookies()
            chrome.get('https://connect.data.com/login')
            if chrome.current_url != 'https://connect.data.com/login':
                chrome.quit()
                self.scrap(results, self.proxies.get())
            email = self.accounts.get()
            chrome.find_element_by_id('j_username').send_keys(email)
            chrome.find_element_by_id('j_password').send_keys(PASS)
            chrome.find_element_by_id('login_btn').click()
            wait.until(ec.visibility_of_element_located((By.ID, "homepageSBS")))

        login()
        keys = Keys.SPACE + (Keys.ARROW_DOWN * 4) + Keys.ENTER  # setting 200 results on page

        while not self.csv.empty():
            try:
                row = self.csv.get()
            except Empty:
                break

            def search():
                chrome.get('https://connect.data.com/search#p=advancedsearch;;t=contacts')
                wait.until(ec.visibility_of_element_located((By.ID, 'companies'))).send_keys(row[0])
                wait.until(ec.visibility_of_element_located((By.CLASS_NAME, 'search-button'))).click()

            search()

            def captcha():
                try:
                    img = WebDriverWait(chrome, 20).until(
                        ec.visibility_of_element_located((By.ID, 'recaptcha_challenge_image')))
                    sleep(1)
                    chrome.save_screenshot('%i.png' % pid)
                    location, size = img.location, img.size
                    im = Image.open('%i.png' % pid)  # uses PIL library to open image in memory
                    left = location['x']
                    top = location['y'] - 100
                    right = location['x'] + 310
                    bottom = location['y'] - 35
                    im = im.crop((left, top, right, bottom))  # defines crop points
                    im.save('%i.png' % pid)  # saves new cropped image
                    solution = AntiGate(API_KEY, '%i.png' % pid)
                    field = wait.until(ec.visibility_of_element_located((By.ID, 'recaptcha_response_field')))
                    field.send_keys(solution.captcha_result)
                    field.submit()
                    return solution
                except TimeoutException:
                    return 0
                except AntiGateError:
                    return 1

            solve = captcha()
            if solve:
                try:
                    sleep(1)
                    WebDriverWait(chrome, 20).until(
                        ec.visibility_of_element_located((By.ID, 'recaptcha_challenge_image')))
                    if solve != 1:
                        solve.abuse()
                    if not self.accounts.empty():
                        login()
                except TimeoutException:
                    pass

            try:
                wait.until(ec.visibility_of_element_located((By.CLASS_NAME, 'ownContact')))
            except TimeoutException:
                with open('done.txt', 'a') as fp:
                    fp.write(row[0] + '\n')
                continue
            wait.until(ec.visibility_of_element_located((By.ID, 'pageSize'))).send_keys(keys)

            while True:
                sleep(2)
                wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'save-search')))
                result = BeautifulSoup(chrome.page_source, 'lxml').find('table', {'class': 'result'})
                contacts = result.find_all('tr', {'class': 'general-display-none', 'style': 'display: table-row;',
                                                  'id': re.compile("[0-9]{8}")})
                for con in contacts:
                    name = con.find('td', {'class': 'td-name'}).getText().split(', ')
                    last_name, first_name = name[0], name[1]
                    company = con.find('td', {'class': 'td-company'}).getText().strip()
                    title = con.find('td', {'class': 'td-title'}).getText().strip()
                    city = con.find('td', {'class': 'td-city'}).getText().strip()
                    state = con.find('td', {'class': 'td-state'}).getText().strip()
                    country = con.find('td', {'class': 'td-country'}).getText().strip()
                    updated = con.find('td', {'class': 'td-updated'}).getText().strip()
                    target_company = row[0]
                    mail_convention = row[2]
                    results.put(
                        [target_company, company, city, state, country, first_name, last_name, mail_convention, title,
                         updated])
                try:
                    wait.until(
                        ec.visibility_of_element_located((By.CLASS_NAME, 'table-navigation-next-image-active'))).click()
                except TimeoutException:
                    break
            with open('done.txt', 'a') as fp:
                fp.write(row[0] + '\n')
        chrome.quit()
        return 0
