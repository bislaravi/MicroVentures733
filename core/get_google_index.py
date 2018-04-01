import time
from .domain_manager import DomainManager

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def get_google_index(url,
                     search_term=None,
                     num_of_pages=5):

    data = []
    google_page_index, google_position_index = None, None
    domain = DomainManager.extract_domain(url)


    if search_term is None:
        search_term = domain

    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
    )

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = user_agent

    driver = webdriver.PhantomJS()
    driver.set_window_size(1024, 768)
    driver.get('www.google.com')

    driver.find_element_by_name('q').send_keys(search_term)
    count = 1
    found = False

    for i in range(1, num_of_pages+1):
        for btn in driver.find_elements_by_tag_name('input'):
            if btn.get_attribute('type') == 'submit':
                btn.click()
                break
        for item in driver.find_elements_by_class_name('g'):
            try:
                link = item.find_element_by_tag_name('cite').text
            except Exception as e:
                print("Exception while getting google index: %s"%e)
                continue

            if domain.lower() in DomainManager.extract_domain(link).lower():
                data.append({
                    'text': item.find_element_by_tag_name('h3').text,
                    'link': link,
                    'page_no': i,
                    'position': count
                    })
                return i, count
                found = True
                break
            count += 1
        time.sleep(5)
        if found:
            break

        footer = driver.find_element_by_id('foot')
        tds = footer.find_elements_by_tag_name('td')
        td = tds[len(tds)-1]
        td.find_element_by_tag_name('a').click()

    driver.quit()

    return None, None