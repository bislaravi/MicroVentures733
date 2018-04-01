import requests
import os
import json
from .domain_manager import DomainManager
from .facebook_numbers import fbAnalytics, extract_facebook_handle
from .mysql_manager import MySQLManager

class DataCollectionPipeline:

    def __init__(self):
        self.CRUNCH_BASE_API_KEY = 'ba0d88b5d3132eec1e701579e3bf8052'
        self.CRUNCH_BASE_URL = 'https://api.crunchbase.com/v3.1/odm-organizations?page=%s' + \
                               '&items_per_page=250&user_key=%s'

        self.SIMILAR_WEB_API_KEY = 'd59e308ce98949fdba672477b0a3c4e8'

    # Getting all Companies from crunch base database
    def get_companies_from_crunch_base(self):
        pages = 2573
        for i in range(2, pages+1):
            res = requests.get(self.CRUNCH_BASE_URL % (str(i), self.CRUNCH_BASE_API_KEY))
            json_path = 'data/data_pipeline/%s.json'
            if res.status_code == 200:
                res_json = res.json()
                data = res_json.get('data')
                items = data.get('items')

                for item in items:
                    name = item['properties']['name']
                    domain = item.get('properties').get('domain')
                    fb_link = item.get('properties').get('facebook_url')
                    correct_fb_domain = self.correct_domain_fb_link(domain, fb_link)
                    if correct_fb_domain:
                        domain_url = DomainManager.extract_domain(domain)
                        is_startup, startup_row = self.check_if_business_in_collected_startups(domain_url, name)
                        print(is_startup, name, startup_row)
                        if is_startup:
                            if not os.path.exists(json_path % startup_row):
                                with open(json_path % startup_row, 'w+') as json_file:
                                    json.dump(item, json_file)


    @staticmethod
    def check_if_business_in_collected_startups(domain_url, name):
        result = MySQLManager.execute_query('SELECt * FROM crunchbase.Startup where homepage like"%{0}%"'
                                            .format(domain_url))
        try:
            if len(result) > 0:
                name = bytes(name, 'utf-8')
                name_str = name.decode('unicode_escape').encode('ascii','ignore')
                name_str = str(name_str)
                name_str = name_str.replace(' ', '').lower()

                query2 = 'SELECt * FROM crunchbase.Startup where replace(lower(name), " ", "") like "%{0}%"'.format(name_str)

                result = MySQLManager.execute_query(query2)
                return len(result) == 1, result[0][0]
            else:
                return len(result) == 1, result[0][0]
        except IndexError:
            return False, None

    def correct_domain_fb_link(self, domain, fb_link):
        correct = True
        if not domain and fb_link:
            return False
        if fb_link:
            handle = extract_facebook_handle(fb_link)
            if handle:
                if domain:
                    pass
                    # try:
                    #     requests.get('http://%s' % domain)
                    # except (requests.ConnectionError, requests.TooManyRedirects):
                    #     correct = False
                else:
                    correct = False
            else:
                correct = False
        else:
            correct = False
        return correct

    # Delete all companies where domain does not work or facebook handle is invalid
    def delete_all_files_with_domain_not_working(self):
        for root, dirs, files in os.walk("data/data_pipeline"):
            file_remove = False
            for filename in files:

                try:
                    data = json.load(open('data/data_pipeline/%s' % filename, 'r'))
                    domain = data.get('properties').get('domain')
                    fb_link = data.get('properties').get('facebook_url')
                    file_remove = self.correct_domain_fb_link(domain, fb_link)

                except json.JSONDecodeError:
                    file_remove = True

            if file_remove:
                os.remove('data/data_pipeline/%s' % filename)
                print('File Removed Due to invalid Domain!')



