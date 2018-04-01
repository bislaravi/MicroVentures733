import requests
import json

# graph-api info
need_data = json.load(open('data/key.json'))
fbat = need_data['fbat']


def extract_facebook_handle(facebook_link, obj=None):
    facebook_handle = None
    is_valid = False

    if facebook_link and 'facebook.com' not in facebook_link:
        facebook_handle = facebook_link
    else:
        pattern = '(?:https?:\\/\\/)?(?:[\\w\\-]+\\.)?'\
                  'facebook\\.com\\/(?:(?:\\w)*#!\\/)?(?:pages\\/)?'\
                  '(?:[\\w\\-]*\\/)*([\\w\\-\\.]*)'
        start = facebook_link.index('http')
        facebook_link = facebook_link[start:]
        facebook_link = facebook_link.replace("'", "").replace('"', "").replace(')', "").replace('(', "")
        try:
            matches = re.match(pattern, facebook_link)
            facebook_handle = matches.group(1)
        except:
            pass

        if not facebook_handle:
            try:
                pattern = 'http[s]?://(www|[a-zA-Z]{2}-[a-zA-Z]{2})\\.facebook\\.com/'\
                          '(pages/[a-zA-Z0-9\\.-]+/[0-9]+|[a-zA-Z0-9\\.-]+)[/]?'
                matches = re.match(pattern, facebook_link)
                facebook_handle = matches.group(2)
            except:
                pass

    return facebook_handle



class fbAnalytics:
    """docstring for fbAnalytics"""

    def __init__(self, fbLink, company_name, domain):
        self.check = True
        self.name = company_name
        self.domain = domain
        self.fbLink = fbLink if fbLink != 'NULL' else None

        if self.fbLink:
            self.companyName = extract_facebook_handle(fbLink)

            try:
                self.graphLink = 'https://graph.facebook.com/v2.12/' + \
                                 self.companyName + \
                                 '?fields=fan_count,about,verification_status,rating_count,start_info,talking_about_count&access_token=' + \
                                 fbat
                self.getback = requests.get(self.graphLink)
                self.jsonValues = self.getback.json()
            # successful status_code = 200
            # print(self.getback.status_code)
            except:
                self.check = False

    def get_json_data(self):
        if self.fbLink:
            try:
                if self.getback and self.getback.status_code == 200:
                    return self.getback.json()
                else:
                    return dict()
            except AttributeError:
                return dict()
        else:
            return dict()

    # returns facebook-handle
    def getfbHandle(self):
        if self.check == True and self.getback.status_code == 200:
            return self.companyName
        else:
            return '-'

    # provides the total number of followers
    def getfbFollower(self):
        if self.check == True and self.getback.status_code == 200:
            return self.jsonValues.get('fan_count')
        else:
            return None

    # provides how many people are talking about
    def getfbTalkingAbout(self):
        if self.check == True and self.getback.status_code == 200:
            return self.jsonValues.get('talking_about_count')
        else:
            return None

    # total number of rating given
    def getfbTotalRating(self):
        if self.check == True and self.getback.status_code == 200:
            return self.jsonValues.get('rating_count')
        else:
            return None

    # verification type of the facebook page
    def getVerificationType(self):
        if self.check == True and self.getback.status_code == 200:
            return self.jsonValues.get(u'verification_status')
        else:
            return None

    # provide start date if exists
    def getStartDate(self):
        if self.check == True and self.getback.status_code == 200:
            try:
                year = self.jsonValues[u'start_info'][u'date'][u'year']
                try:
                    month = self.jsonValues[u'start_info'][u'date'][u'month']
                except:
                    month = 1
            except:
                year = 0
                month = 0

            return [month, year]
        else:
            return None

    # provide start year
    def getStartYear(self):
        if self.check == True and self.getback.status_code == 200:
            return self.getStartDate()[1]
        else:
            return None

    def get_data_for_fb(self):
        if self.fbLink:
            return {
                'name': self.name,
                'domain': self.domain,
                'follower': self.getfbFollower(),
                'talkingAbout': self.getfbTalkingAbout(),
                'getFbTotalRating': self.getfbTotalRating(),
                'getVerificationType': self.getVerificationType(),
                'getStartDate': self.getStartDate(),
                'getEndDate': self.getStartYear()
            }
        else:
            None


import re
def extract_facebook_handle(facebook_link, obj=None):
    pattern = '(?:https?:\\/\\/)?(?:[\\w\\-]+\\.)?' \
              'facebook\\.com\\/(?:(?:\\w)*#!\\/)?(?:pages\\/)?' \
              '(?:[\\w\\-]*\\/)*([\\w\\-\\.]*)/?'
    start = 0
    facebook_link = facebook_link[start:]
    facebook_link = facebook_link.replace("'", "").replace('"', "").replace(')', "").replace('(', "")
    facebook_handle = None
    try:
        matches = re.match(pattern, facebook_link.strip('/'))
        facebook_handle = matches.group(1)
    except:
        pass
    return facebook_handle


