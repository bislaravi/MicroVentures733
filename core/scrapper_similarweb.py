import lxml.html
import pandas as pd
import re
import json
import os
from bs4 import BeautifulSoup as soup


class SimilarWebScrapper(object):

    def __init__(self):
        pass

    @classmethod
    def scrape_similar_web(cls, content):
        company_json = dict()
        similar_page_soup = soup(content, "html.parser")
        container_header = similar_page_soup.findAll("ul", {
            "class": "websiteHeader-companyInfoList is-collapsed js-websiteHeader-companyInfoList"})
        try:
            year_founded_str = container_header[0].p.getText()
            if (int(year_founded_str) > 1900 and int(year_founded_str) < 2019):
                company_json['year_founded'] = int(year_founded_str)
            else:
                company_json['year_founded'] = ''
        except:
            company_json['year_founded'] = ''

        container = similar_page_soup.findAll("div", {"class": "websiteRanks-valueContainer js-websiteRanksValue"})
        category = similar_page_soup.findAll("a", {"class": "websiteRanks-nameText"})

        try:
            company_json['country'] = category[1].getText()
            company_json['category'] = category[2].getText().split(' > ')[0]
        except IndexError:
            company_json['country'] = None
            company_json['category'] = None
        try:
            company_json['global_rank'] = int(container[0].getText().replace(' ', '').replace('\n', '').replace(',', ''))
            company_json['country_rank'] = int(
                container[1].getText().replace(' ', '').replace('\n', '').replace(',', ''))
            company_json['category_rank'] = int(
                container[2].getText().replace(' ', '').replace('\n', '').replace(',', ''))
        except:
            company_json['global_rank'] = ''
            company_json['country_rank'] = ''
            company_json['category_rank'] = ''

        container_web_presence = similar_page_soup.findAll("div", {"class": "websitePage-engagementInfo"})
        web_presence = container_web_presence[0].findAll("span", {"class": "engagementInfo-valueNumber js-countValue"})
        if (len(web_presence) == 4):
            try:
                total_visit_str = web_presence[0].getText()
                if (total_visit_str.endswith('K')):
                    company_json['total_visit'] = str(float(total_visit_str.replace('K', '')) * 1000)
                elif (total_visit_str.endswith('M')):
                    company_json['total_visit'] = str(float(total_visit_str.replace('M', '')) * 1000000)
                elif (total_visit_str.endswith('B')):
                    company_json['total_visit'] = str(float(total_visit_str.replace('B', '')) * 1000000000)
                else:
                    company_json['total_visit'] = total_visit_str
                avg_vis_dur_str = web_presence[1].getText().split(':')
                avg_vis_dur_in_min = int(avg_vis_dur_str[0]) * 60 + int(avg_vis_dur_str[1]) + int(
                    avg_vis_dur_str[2]) / 60
                company_json['avg_visit_duration_minute'] = float(avg_vis_dur_in_min)
                company_json['pages_per_visit'] = float(web_presence[2].getText())
                company_json['bounce_rate'] = float(web_presence[3].getText().replace('%', ''))
            except:
                company_json['total_visit'] = ''
                company_json['avg_visit_duration_minute'] = ''
                company_json['pages_per_visit'] = ''
                company_json['bounce_rate'] = ''
        else:
            company_json['total_visit'] = ''
            company_json['avg_visit_duration_minute'] = ''
            company_json['pages_per_visit'] = ''
            company_json['bounce_rate'] = ''

        #getting number of subdomains

        try:
            domain_area = similar_page_soup.find("div", {'data-tab':'subdomains'})
            domain = domain_area.find('span', {'class':"websiteContent-tableColumn websiteContent-tableColumn--narrow"})
            import re
            subdomain = re.findall(r'\d+', domain.getText())
            company_json['subdomain'] = int(subdomain[0])
        except:
            company_json['subdomain'] = None

        #Getting number of Google App

        try:
            google_apps = similar_page_soup.find("div", {'class': 'apps-store-group google'})
            google_apps = len(google_apps.find_all("li", {'class': 'mobileApps-appItem'}))
            company_json['google_apps'] = google_apps
        except:
            company_json['google_apps'] = None

        #Getting number of IOS

        try:
            apple_apps = similar_page_soup.find("div", {'class': 'apps-store-group apple'})
            apple_apps = len(apple_apps.find_all("li", {'class': 'mobileApps-appItem'}))
            company_json['app_store_apps'] = apple_apps
        except:
            company_json['app_store_apps'] = 0


        # Getting Traffic Search Percentages
        try:

            search = similar_page_soup.find({'span': {'class': 'subheading-value searchText'}})
            search = float(search.getText().replace('%', ''))
            company_json['search_percentage'] = search
        except:
            company_json['search_percentage'] = 0

        # Getting Traffic Social Percentages
        try:

            social = similar_page_soup.find({'span': {'class': 'subheading-value social'}})
            social = float(social.getText().replace('%', ''))
            company_json['social_percentage'] = social
        except:
            company_json['social_percentage'] = None

        # Getting Traffic referrals Percentages
        try:

            referrals = similar_page_soup.find({'span': {'class': 'subheading-value referrals'}})
            referrals = float(referrals.getText().replace('%', ''))
            company_json['referrals_percentage'] = referrals
        except:
            company_json['referrals_percentage'] = None

        # Getting Traffic display Percentages
        try:

            display = similar_page_soup.find({'span': {'class': 'subheading-value display'}})
            display = float(display.getText().replace('%', ''))
            company_json['ads_percentage'] = display
        except:
            company_json['ads_percentage'] = None

        return company_json