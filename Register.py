#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from random import randint

PASS = ''#####


class Register:
    """
    Helps with accounts registration on connect.data.com using poczta.o2.pl email accounts. Requires manual interaction.
    """

    @staticmethod
    def register():
        """
        Helps with accounts registration on connect.data.com using poczta.o2.pl email accounts.
        Requires manual interaction.
        :return: 0 on success
        """
        with open('O2Accounts.txt') as fp:
            mails = [l.strip() for l in fp.readlines()]
        c = webdriver.Chrome()
        wait = WebDriverWait(c, 10)
        for mail in mails:
            c.get('https://connect.data.com/registration/signup')
            wait.until(ec.visibility_of_element_located((By.ID, 'userFullName'))).send_keys(
                '%s %s' % (mail.split('.')[0], mail.split('.')[0]))
            wait.until(ec.visibility_of_element_located((By.ID, 'userEmail'))).send_keys(mail)
            wait.until(ec.visibility_of_element_located((By.ID, 'userConfirmEmail'))).send_keys(mail)
            wait.until(ec.visibility_of_element_located((By.ID, 'password'))).send_keys(PASS)
            Select(wait.until(ec.visibility_of_element_located((By.ID, 'userProfession')))).select_by_index(
                randint(1, 7))
            wait.until(ec.visibility_of_element_located((By.ID, 'EUAgreement'))).click()
            input('OK? -signed up?')
            c.get('http://poczta.o2.pl')
            wait.until(ec.visibility_of_element_located((By.ID, 'login'))).send_keys(mail)
            p = wait.until(ec.visibility_of_element_located((By.ID, 'pass')))
            p.send_keys('123456')
            p.submit()
            input('OK? - confirmed?')
        return 0
