#!/usr/bin/env python3
from selenium import webdriver
from time import sleep
import urllib.parse
from bs4 import BeautifulSoup
from multiprocessing import Queue, Process
from multiprocessing.queues import Empty
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from os import getpid
from time import strftime
from antigate import AntiGate, AntiGateError
from PIL import Image
import csv

API_KEY = '363de6f86b118a98f3a904bf9b3e2e77'


def log(string):
    with open('scraper.log', 'a') as LOG:
        LOG.write(str(strftime('%H:%M:%S ')) + string + '\n')
        print(str(strftime('%H:%M:%S ')) + string)


class GetLinkedin:
    def __init__(self, keywords_file_name='data3.csv', proxies_file_name='proxy.txt'):
        self.keywords = Queue()
        with open(keywords_file_name, 'r', newline='') as fp:
            csv_reader = csv.reader(fp)
            for line in csv_reader:
                self.keywords.put(line)
        with open(proxies_file_name, 'r') as fp:
            self.proxies = [line.strip() for line in fp.readlines()]
            self.proxies.append('')
        self.run()

    def run(self):
        processes = []
        for proxy in self.proxies:
            p = Process(target=self.scrap, args=(proxy, self.keywords))
            p.start()
            processes.append(p)
            log('Started %i process' % len(processes))
            sleep(3)
        with open('data-final.csv', 'w', newline='') as fp:
            csv_writer = csv.writer(fp)
            csv_writer.writerow(
                ['Searched Company Name', 'Found Company Name', 'City', 'State', 'Country', 'First Name', 'Last Name',
                 'Title', 'Updated', 'Phone', 'Email', 'Domain MX Record', 'SMTP Check', 'Email Score',
                 'Linkedin Account'])




    @staticmethod
    def scrap(proxy, keywords):
        pid = getpid()

        def __start(args=None):
            status = 1
            while status:
                try:
                    if args:
                        driver = webdriver.Chrome(chrome_options=args)
                    else:
                        driver = webdriver.Chrome()
                    status = 0
                except WebDriverException:
                    status = 1
                    sleep(1)
            return driver

        def start():
            dc = webdriver.ChromeOptions()
            dc.add_argument('--no-sandbox')
            if proxy:
                dc.add_argument('--proxy-server=%s' % proxy)
                return __start(dc)
            else:
                return __start()

        driver = start()

        def captcha():
            try:
                img = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.TAG_NAME, 'img')))
                sleep(1)
                driver.save_screenshot('%i.png' % pid)
                location, size = img.location, img.size
                im = Image.open('%i.png' % pid)  # uses PIL library to open image in memory
                left = location['x']
                top = location['y']
                right = location['x'] + size['width']
                bottom = location['y'] + size['height']
                im = im.crop((left, top, right, bottom))  # defines crop points
                im.save('%i.png' % pid)  # saves new cropped image
                solve = AntiGate(API_KEY, '%i.png' % pid)
                field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, 'captcha')))
                field.send_keys(solve.captcha_result)
                field.submit()
                return solve
            except TimeoutException:
                log("Timeout exception")
                keywords.put(row)
                return 1
            except AntiGateError:
                log("Antigate Error")
                return 0

        while not keywords.empty():
            try:
                row = keywords.get()
                keyword = 'site:linkedin.com %s %s %s' % (row[5], row[6], row[0])
            except Empty:
                break
            try:
                url = "https://www.google.com/search?filter=0&" + urllib.parse.urlencode({'q': keyword})
                driver.get(url)
                while driver.current_url.split('google.com')[0] in (
                        'https://ipv4.', 'https://ipv6.', 'http://ipv4.', 'http://ipv6.'):
                    log('%s is raising captcha!' % proxy)
                    s = 0
                    while not s:
                        s = captcha()
                    if s == 1:
                        break
                    try:
                        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'logocont')))
                        log('Captcha successfully resolved as %s' % s.captcha_result)
                        break
                    except TimeoutException:
                        log('Captcha wrongly resolved as %s' % s.captcha_result)
                        s.abuse()
                        continue

                if driver.current_url[:19] != url[:19]:
                    log('Wrong site loaded by %s (%s)' % (proxy, driver.current_url))
                    keywords.put(row)
                    break
                try:
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'logocont')))
                except TimeoutException:
                    log('Site not fully loaded by %s' % proxy)
                    keywords.put(row)
                    break
                try:
                    row.append(BeautifulSoup(driver.page_source, 'lxml').find('h3', {'class': 'r'}).a['href'][7:])
                except AttributeError:
                    pass  # No profile
                with open('data-final.csv', 'a', newline='') as fp:
                    csv_writer = csv.writer(fp)
                    csv_writer.writerow(row)
                log('Successful scrap of %s by %s in process %s' % (keyword, proxy, str(pid)))
            except Exception as e:
                log(str(e))
                keywords.put(row)
                driver.quit()
                driver = start()
        driver.quit()


GetLinkedin()
