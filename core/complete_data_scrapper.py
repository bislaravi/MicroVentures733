import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .domain_manager import DomainManager
import json
from .TorCrawler import TorCrawler
from .s3_manager import S3Manager
from .mysql_manager import MySQLManager
from .facebook_numbers import fbAnalytics
import time
import os
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import random

from .scrapper_crunchbase import CrunchbaseScrapper
from .scrapper_similarweb import SimilarWebScrapper
from selenium.webdriver.firefox.options import Options

import MySQLdb


class Complete_Data_Scrapper(object):

    crunchbase_open_data = 'https://api.crunchbase.com/v3.1/odm-organizations?user_key=ba0d88b5d3132eec1e701579e3bf8052'

    def __init__(self):
        self.proxies = []
        proxies_req = Request('https://www.sslproxies.org/')
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
        )
        proxies_req.add_header('User-Agent', user_agent)
        proxies_doc = urlopen(proxies_req).read().decode('utf8')

        soup = BeautifulSoup(proxies_doc, 'html.parser')
        proxies_table = soup.find(id='proxylisttable')

        # Save proxies in the array
        for row in proxies_table.tbody.find_all('tr'):
            self.proxies.append({
                'ip': row.find_all('td')[0].string,
                'port': row.find_all('td')[1].string
            })


    def get_all_company_data(self, start_position, end_position):
        # Open database connection
        start_position = start_position+1 if start_position == 1 else start_position
        result = MySQLManager.execute_query('SELECT * FROM crunchbase.Startup where id BETWEEN %s and %s' %(start_position, end_position))
        print('hello')
        for row in result:
            row_id, name, city, domain, fb_handle, tw_handle, hacker_news, is_scrapped = row
            domain = DomainManager.extract_domain(domain)
            self.scrape_company_data(row_id, name, domain, fb_handle, tw_handle, city)



    def get_web_driver(self,tor_enabled=True):
        def random_proxy():
            return random.randint(0, len(self.proxies) - 1)
        proxy_index = random_proxy()
        proxy = self.proxies[proxy_index]
        options = Options()
        options.add_argument("--headless")
        if tor_enabled:
            profile = webdriver.FirefoxProfile()
            profile.set_preference('network.proxy.type', proxy['port'])
            profile.set_preference('network.proxy.http', proxy['ip'])
            profile.set_preference('network.proxy.http_port', 8118)
            print('hello')
            return webdriver.Firefox(profile, executable_path=os.path.abspath(os.getcwd()) + "/core/geckodriver")

        else:
            return webdriver.Firefox(executable_path=os.path.abspath(os.getcwd()) + "/core/geckodriver")

    def scrape_company_data(self, row_id, company_name, domain, facebook_handle, tw_handle, city):

        # if self.crawler:
        #     self.crawler.rotate()
        driver = self.get_web_driver()
        sw_data = dict()
        cb_data = dict()
        fb_data = dict()

        actual_name = company_name
        company_name = company_name.lower()
        company_name = company_name.split(' ')
        company_name = company_name[0] if company_name[0] != 'the' else company_name[1]



        crunchbase_url = 'https://www.crunchbase.com/organization/%s' % company_name
        owler_url='https://www.owler.com/company/%s' % company_name
        similar_web='https://www.similarweb.com/website/%s' % domain
        funding_pages='https://www.crunchbase.com/organization/%s/funding_rounds/funding_rounds_list'%company_name

        crunchbase_exist=False

        delay = 30  # seconds

        try:
            driver.get(crunchbase_url)
            myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'section-recent-news-activity')))
            cb_data = CrunchbaseScrapper.scrape_content(driver.page_source)
            # f = open('data/crunch_base_pages/%s.html' % row_id, 'w+')
            # f.write(driver.page_source)
            # f.close()
            crunchbase_exist = True
        except TimeoutException:
            print("Loading took too much time!")

        # if not os.path.exists('data/owler_pages/%s.html' % company_name):
        #     try:
        #         driver.get(owler_url)
        #         myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'profile')))
        #         f = open('data/owler_pages/%s.html' % company_name, 'w+')
        #         f.write(driver.page_source)
        #         f.close()
        #     except TimeoutException:
        #         print("Loading took too much time!")
        #
        #     time.sleep(3)
        try:
            driver.get(similar_web)
            myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'websiteRanks-valueContainer')))
            # f = open('data/similar_web_pages/%s.html' % row_id, 'w+')
            # f.write(driver.page_source)
            # f.close()
            sw_data = SimilarWebScrapper.scrape_similar_web(driver.page_source)
        except TimeoutException:
            print("Loading took too much time!")

        funding_data = dict()
        if not os.path.exists('data/funding_stages_pages/%s.html' % company_name) and crunchbase_exist:
            try:
                driver.get(funding_pages)
                myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'section-layout-content')))
                # f = open('data/funding_stages_pages/%s.html' % company_name, 'w+')
                # f.write(driver.page_source)
                # f.close()
                funding_data = CrunchbaseScrapper.scrape_funding_list(driver.page_source)
            except TimeoutException:
                print("Loading took too much time!")


        driver.quit()


        fb = fbAnalytics(facebook_handle, company_name, domain)
        fb_j = fb.get_json_data() if not None else dict()
        fb_data.update(fb_j)
        if fb_data:
            fb_data['twitter_handle'] = tw_handle
            fb_data['city'] = city
            # with open('data/facebook_data/%s.json'%row_id, 'w+') as fb_json:
            #     json.dump(fb_data, fb_json)
        cb_data.update(funding_data)
        cb_data.update(sw_data)
        cb_data.update(fb_data)
        cb_data['id'] = row_id
        cb_data['name'] = actual_name
        with open('data/complete_data/%s.json' % row_id, 'w+') as complete_data:
            json.dump(cb_data, complete_data)

        S3Manager.transafer_file_to_s3('data/complete_data/%s.json' % row_id, str(row_id)+'.json')
        MySQLManager.execute_query('UPDATE crunchbase.Startup  SET scrapped = True Where id=%s' % str(row_id))

# cc = Complete_Data_Scrapper()
# cc.get_all_company_data(1, 1)


