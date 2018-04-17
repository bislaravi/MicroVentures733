from cmpt733.core.EntityParser import EntityParser
import datetime as dt
from datetime import datetime as dt
from dateutil import relativedelta
import requests

funding_stages = {
    'angel': 1,
    'seed': 2,
    'a': 3,
    'b': 4,
    'c': 5
}


class FeatureExtractor(object):

    def extract_company_feature(self, company_file):
        company_js = EntityParser.LoadJsonEntity(company_file)
        if company_js is None:
            return None
        features = self.get_feature_template()
        founded_year = company_js['founded_year']
        founded_month = company_js['founded_month'] if company_js['founded_month'] else 1
        founded_day = company_js['founded_day'] if company_js['founded_day'] else 1
        try:
            founded_date = dt(founded_year, founded_month, 1).date()
        except TypeError:
            return None



        funding_rounds = company_js['funding_rounds']
        total_funding = 0
        if funding_rounds:
            max_fund_code = 0
            max_funding_round = None
            for round in funding_rounds:
                code = round['round_code']
                raised_amt = round['raised_amount']
                if raised_amt:
                    total_funding += raised_amt
                if round['round_code'] in funding_stages.keys():
                    year = round['funded_year']
                    month = round['funded_month']
                    day = round['funded_day'] if round['funded_day'] else 1
                    try:
                        fund_date = dt(year, month, day)
                    except:
                        continue

                    date_diff = relativedelta.relativedelta(fund_date, founded_date)
                    months_diff = (date_diff.years * 12) + date_diff.months
                    if features[code+'_months']:
                        if features[code+'_months'] < months_diff:
                            features[code + '_months'] = months_diff
                    else:
                        features[code + '_months'] = months_diff

                    if features[code + '_raised_amount']:
                        if raised_amt:
                            features[code + '_raised_amount'] += raised_amt
                    else:
                        features[code+'_raised_amount'] = raised_amt
        try:
            features['investment_per_funding_round'] = total_funding / len(funding_rounds)
        except ZeroDivisionError:
            features['investment_per_funding_round'] = 0
        company_website = company_js['homepage_url']
        features['no_of_employees'] = company_js['number_of_employees']
        features['com_domain'] = True if '.com' in company_website else False
        features['number_of_milestone'] = len(company_js.get('milestones', []))
        features['number_of_offices'] = len(company_js['offices'])
        features['category'] = company_js['category_code']
        features['number_of_providers'] = len(company_js['providerships'])
        features['number_of_competitors'] = len(company_js['competitions'])
        features['number_of_products'] = len(company_js['products'])
        features['number_of_funding_rounds'] = len(funding_rounds)
        features['number_of_investments'] = len(company_js['investments'])
        features['headquarter_location'] = self.find_company_headquarter(company_js)
        features['number_of_co_founder'] = self.get_num_of_co_founders(company_js)

        company_permalink = company_js['permalink']

        for competitor in company_js['competitions']:
            comp = competitor['competitor']
            permalink = comp['permalink']
            got_series_c = self.find_business_above_series_c_or_ipo_merger(permalink)
            if got_series_c:
                if features['number_of_competitors_got_series_c'] is None:
                    features['number_of_competitors_got_series_c'] = 1
                else:
                    features['number_of_competitors_got_series_c'] += 1

        features['label'] = self.find_business_above_series_c_or_ipo_merger('', company_js)
        features['label_date'], features['label_stage'] = self.get_business_above_series_c_or_ipo_merger_date('', company_js)
        company_age = relativedelta.relativedelta(features['label_date'], founded_date)
        company_age_months = (company_age.years * 12) + company_age.months
        features['company_age_months'] = company_age_months
        features['name'] = company_js['name']
        features['permalink'] = company_js['permalink']
        features['number_of_tech_crunch_article'] = self.get_tech_crunch_articles_count(
            company_permalink, features['label_date'])

        no_of_phd, no_of_financial, no_of_engineer, \
            no_of_companies_by_founder, \
            no_of_successful_company_by_founder = self.get_team_background(company_js)

        features['number_of_financial_background'] = no_of_financial
        features['number_of_engineering_background'] = no_of_engineer
        features['number_of_phd'] = no_of_engineer
        features['number_of_companies_by_founder'] = no_of_companies_by_founder
        features['successful_companies_by_founder'] = no_of_successful_company_by_founder
        return features

    def find_company_headquarter(self, company_js):
        offices = company_js['offices']

        if offices:
            for office in offices:
                if office['description'] == 'Headquarters':
                    return office['city']
        else:
            return None



    def get_tech_crunch_articles_count(self, permalink, label_date):
        articles = EntityParser.get_file_handler('data/article_crawled_urls/' + permalink)
        if not articles:
            return 0
        no_of_tech_crunch_articles = 0
        while True:
            x = articles.readline()
            x = x.rstrip()
            if not x:
                break
            else:
                data = x.split(',')
                date = data[0]
                date = date.split('/')
                if len(date[2]) == 1:
                    date[2] = '0'+date[2]
                date = '/'.join(date)
                date = dt.strptime(date, "%m/%d/%y")
                if date and label_date:
                    if date.date() <= label_date.date():
                        no_of_tech_crunch_articles += 1
                else:
                    no_of_tech_crunch_articles += 1

        return no_of_tech_crunch_articles

    def find_business_above_series_c_or_ipo_merger(self, permalink, company_js=None):

        if not company_js:
            company_js = EntityParser.LoadJsonEntity('data/company/'+permalink)
        if company_js:
            deadpooled_year = company_js['deadpooled_year']
            deadpooled_month = company_js['deadpooled_month']
            if deadpooled_year and deadpooled_month:
                return False
            funding_rounds = company_js.get('funding_rounds')
            if funding_rounds:
                for round in funding_rounds:
                    if round['round_code'] not in ['angel', 'seed', 'a', 'b', 'unattributed']:
                        return True
            acquisition = company_js.get('acquisition', [])
            ipo = company_js.get('ipo', [])
            if acquisition and len(acquisition) > 1:
                return True
            if ipo:
                return True
        return None

    def get_business_above_series_c_or_ipo_merger_date(self, permalink, company_js=None):
        if not company_js:
            company_js = EntityParser.LoadJsonEntity('data/company/'+permalink)

        if company_js:
            deadpooled_year = company_js['deadpooled_year']
            deadpooled_month = company_js['deadpooled_month']
            if deadpooled_year and deadpooled_month:
                return dt(deadpooled_year, deadpooled_month, 1), 'Dead'
            funding_rounds = company_js.get('funding_rounds')
            label_date = None
            last_funding_round = None
            if funding_rounds:
                for round in funding_rounds:
                    if round['round_code'] not in ['angel', 'seed', 'a', 'b', 'unattributed']:
                        round_year = round['funded_year']
                        round_month = round['funded_month']
                        round_day = round['funded_day']
                        try:
                            round_date = dt(round_year, round_month, round_day)
                        except:
                            continue
                        if label_date is not None:
                            if label_date > round_date:
                                label_date = round_date
                                last_funding_round = round['round_code']
                        else:
                            last_funding_round = round['round_code']
                            label_date = round_date
                if label_date is not None:
                    return label_date, last_funding_round

            acquisition = company_js.get('acquisition', [])
            ipos = company_js.get('ipo', [])
            if acquisition and len(acquisition) > 1:

                acq_year = acquisition['acquired_year']
                acq_month = acquisition['acquired_month']
                acq_day = acquisition['acquired_day']
                try:
                    acq_date = dt(acq_year, acq_month, acq_day)
                    if label_date is not None:
                        if label_date > acq_date:
                            label_date = acq_date
                    else:
                        label_date = acq_date
                    if label_date is not None:
                        return label_date, 'acquired'
                except:
                    pass

            if ipos:
                ipo_year = ipos['pub_year']
                ipo_month = ipos['pub_month']
                ipo_day = ipos['pub_day']
                try:
                    ipo_date = dt(ipo_year, ipo_month, ipo_day)
                    if label_date is not None:
                        if label_date > ipo_date:
                            label_date = ipo_date
                    else:
                        label_date = ipo_date
                    if label_date is not None:
                        return label_date, 'ipo'
                except:
                    pass



            return label_date, None

    def get_num_of_co_founders(self, company_js):
        team = company_js['relationships']
        no_of_co_founders = 0
        for people in team:
            title = people['title']
            title = title.lower()
            if 'founder' in title:
                no_of_co_founders += 1
        return no_of_co_founders

    def get_team_background(self, company_js):
        team = company_js['relationships']
        company_permalink = company_js['permalink']
        no_of_phd = 0
        no_of_financial = 0
        no_of_engineer = 0
        no_of_companies_by_founder = 0
        no_of_successfull_company_by_founder = 0
        for people in team:
            people_perma_link = people['person']['permalink']
            title = people['title']
            is_co_founder = True if 'founder' in title else False
            people_js = EntityParser.LoadJsonEntity('data/person/'+people_perma_link)
            if people_js:
                people_degree = people_js['degrees']
                if is_co_founder:
                    person_companies = people_js['relationships']
                    for company in person_companies:
                        firm = company['firm']
                        if firm['permalink'] != company_permalink:
                            if 'founder' in company['title'].lower() or 'president' in company['title'].lower():
                                no_of_companies_by_founder += 1
                                is_company_successful = self.find_business_above_series_c_or_ipo_merger(firm['permalink'])
                                if is_company_successful:
                                    no_of_successfull_company_by_founder += 1


                for degree in people_degree:
                    people_degree_type = degree['degree_type']
                    people_degree_title = str(degree['subject']).lower()

                    if str(people_degree_type).lower() == 'phd':
                        no_of_phd += 1
                    if 'engineering' in people_degree_title:
                        no_of_engineer += 1
                    if 'finance' in people_degree_title or str(people_degree_type).lower() == 'mba'\
                            or 'business' in people_degree_title or 'management' in people_degree_title:
                        no_of_financial += 1
        return no_of_phd, no_of_financial, no_of_engineer, no_of_companies_by_founder, no_of_successfull_company_by_founder











    def get_feature_template(self):
        return {
            'no_of_employees': None,
            'company_age_months': None,
            'number_of_milestone': None,
            'number_of_tech_crunch_article': None,
            'number_of_hacker_news_article': None,
            'number_of_competition': None,
            'c_months': None,
            'a_months': None,
            'b_months': None,
            'angel_months': None,
            'seed_months': None,
            'a_num': None,
            'b_num': None,
            'c_num': None,
            'angel_num': None,
            'seed_num': None,
            'a_raised_amount': None,
            'b_raised_amount': None,
            'c_raised_amount': None,
            'angel_raised_amount': None,
            'seed_raised_amount': None,
            'number_of_competitors_got_series_c': None,
            'headquarter_location': None,
            'number_of_products': None,
            'number_of_offices': None,
            'number_of_providers': None,
            'number_of_funding_rounds': None,
            'number_of_investments': None,
            'number_of_acquisition': None,
            'number_of_co_founder': None,
            'number_of_financial_background': None,
            'number_of_engineering_background': None,
            'number_of_phd': None,
            'investment_per_funding_round': None,
            'number_of_companies_by_founder': None,
            'successful_companies_by_founder': None,
            'name': None,
            'category': None
        }

import os


def get_features_for_all_companies():
    total_file = 0
    all_companies_features = []
    fs = FeatureExtractor()
    for subdir, dirs, files in os.walk('data/company'):
        for file in files:
            print(file)
            feature = fs.extract_company_feature('data/company/%s'%file)
            if feature is not None:
                all_companies_features.append(feature)
            total_file += 1
    print(total_file)
    return all_companies_features

