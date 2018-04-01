import lxml.html
import pandas as pd
import re
import json
import os
from bs4 import BeautifulSoup as soup
import re

class CrunchbaseScrapper(object):

    def __init__(self):
        pass

    # function for refromat the json
    @staticmethod
    def format_json(company_json):
        # companyJson['Operating Status'] = ''
        try:
            full_date = company_json['Founded Date']
            if (len(full_date.replace(' ', '').split(',')) > 1):
                fyear = full_date.replace(' ', '').split(',')[1]
                company_json['Founded Year'] = fyear.strip()
        except:
            pass
        # companyJson['Funding Status'] = ''
        # companyJson['Last Funding Type'] = ''
        try:
            company_json['Number of Employees'] = \
            company_json['Number of Employees'].replace(' ', '').replace('+', '').split('-')[1]
        except:
            pass
        # companyJson['Number of Acquisitions'] = ''
        # companyJson['Number of Investments'] = ''
        # companyJson['Number of Funding Rounds'] = ''
        try:
            tempstr = company_json['Total Funding Amount'].replace('$', '').replace('CAD', '').replace('CA', '')
            if (tempstr.endswith('K')):
                company_json['Total Funding Amount'] = str(float(tempstr.replace('K', '')) * 1000)
            elif (tempstr.endswith('M')):
                company_json['Total Funding Amount'] = str(float(tempstr.replace('M', '')) * 1000000)
            elif (tempstr.endswith('B')):
                company_json['Total Funding Amount'] = str(float(tempstr.replace('B', '')) * 1000000000)
            else:
                company_json['Total Funding Amount'] = str(float(tempstr))
        except:
            pass
        # companyJson['Number of Lead Investors'] = ''
        # companyJson['Number of Investors'] = ''
        # companyJson['Number of Exits'] = ''
        # companyJson['Number of Current Team Members'] = ''
        # companyJson['Number of Board Members / Advisors'] = ''
        # companyJson['Number of Sub-Orgs'] = ''
        try:
            company_json['CB Rank (Company)'] = int(company_json['CB Rank (Company)'].replace(',', ''))
        except:
            pass
        # companyJson['Number of Events'] = ''
        return company_json

    @classmethod
    def scrape_content(cls, content):
        company_json = dict()
        company_json['Operating Status'] = ''
        company_json['Founded Date'] = ''
        company_json['Funding Status'] = ''
        company_json['Last Funding Type'] = ''
        company_json['Number of Employees'] = ''
        company_json['Number of Acquisitions'] = ''
        company_json['Number of Investments'] = ''
        company_json['Number of Funding Rounds'] = ''
        company_json['Total Funding Amount'] = ''
        company_json['Number of Lead Investors'] = ''
        company_json['Number of Investors'] = ''
        company_json['Number of Exits'] = ''
        company_json['Number of Current Team Members'] = ''
        company_json['Number of Board Members / Advisors'] = ''
        company_json['Number of Sub-Orgs'] = ''
        company_json['CB Rank (Company)'] = ''
        company_json['Number of Events'] = ''

        crunch_page_soup = soup(content, "html.parser")

        x = crunch_page_soup.findAll("div", {"class": "layout-wrap layout-row"})
        my_list = re.sub(r'\n+', '\n', x[0].text).replace('  ', '').replace('\xa0', '').replace('\n\n', '\n').split(
            '\n')[1:]
        i = 0

        while i < len(my_list):
            if (my_list[i] == 'Operating Status' or
                        my_list[i] == 'Founded Date' or
                        my_list[i] == 'Funding Status' or
                        my_list[i] == 'Last Funding Type' or
                        my_list[i] == 'Number of Employees' or
                        my_list[i] == 'Founded Date'):
                company_json[my_list[i]] = my_list[i + 1]
            i = i + 1

        y = crunch_page_soup.findAll("div",
                                     {"class": "flex-100 flex-gt-sm-50 bigValueItem layout-column ng-star-inserted"})
        for i in range(len(y)):
            my_list = re.sub(r'\n+', '\n', y[i].text).replace('  ', '').replace('\xa0', '').replace('\n\n', '\n').split(
                '\n')[1:]
            if (my_list[0] == 'Number of Acquisitions' or
                        my_list[0] == 'Number of Investments' or
                        my_list[0] == 'Number of Funding Rounds' or
                        my_list[0] == 'Total Funding Amount' or
                        my_list[0] == 'Number of Lead Investors' or
                        my_list[0] == 'Number of Investors' or
                        my_list[0] == 'Number of Exits' or
                        my_list[0] == 'Number of Current Team Members' or
                        my_list[0] == 'Number of Board Members / Advisors' or
                        my_list[0] == 'Number of Sub-Orgs' or
                        my_list[0] == 'CB Rank (Company)' or
                        my_list[0] == 'Number of Events'):
                company_json[my_list[0]] = my_list[1]

        return cls.format_json(company_json)


    @classmethod
    def scrape_funding_list(cls, content):
        crunch_page_soup = soup(content, "html.parser")
        funding_rows_div = crunch_page_soup.find_all("div", {'class': "component--grid-row"})
        # raise InterruptedError
        empty_funding = {
            'investors': 0,
            'amount': 0,
            'date': None
        }
        funding = dict()
        funding['A'] = empty_funding
        funding['B'] = empty_funding
        funding['C'] = empty_funding
        funding['D'] = empty_funding
        funding['E'] = empty_funding
        funding['F'] = empty_funding
        funding['G'] = empty_funding
        funding['H'] = empty_funding

        for row in funding_rows_div:
            date = row.find("span", {'class': 'component--field-formatter field-type-date ng-star-inserted'})
            date = date.getText()

            amount = row.find("span", {'class': 'component--field-formatter field-type-money ng-star-inserted'})
            amount = amount.getText().strip()[1:]

            if (amount.endswith('K')):
                mul_amount =  1000
            elif (amount.endswith('M')):
                mul_amount = 1000000
            elif (amount.endswith('B')):
                mul_amount = 1000000000
            else:
                mul_amount = 1

            label = row.find("span", {"class": "flex cb-overflow-ellipsis identifier-label"})
            label = label.getText()
            series_type = label.split('-')[0].strip()[-2:]
            if series_type[0] == ' ':
                series_type = series_type[1].upper()
            else:
                series_type = None

            investors = None
            print(series_type, series_type in funding)
            investors = row.find({'div': {"class": "cb-link component--field-formatter field-type-integer ng-star-inserted"}})
            investors = investors.getText()
            investors = re.findall(r'\d+', investors)[0]

            if series_type in funding:
                if amount:
                    funding[series_type]['amount'] += (float(amount[:-1])*mul_amount)
                funding[series_type]['investors'] += int(investors)
                funding[series_type]['date'] = date.strip()

            print(series_type, amount, investors, date)

        return {'fundingType': funding}




