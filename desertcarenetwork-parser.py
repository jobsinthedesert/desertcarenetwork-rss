import rsswriter
import time
import argparse
import bs4 as bs
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def open_browser(url):
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(firefox_options=options, executable_path=r'geckodriver')
    browser.get(url)
    time.sleep(3)
    return browser

def check_pagination(browser):
    try:
        browser.find_element_by_xpath('//*[@id="pagination-bottom"]/div[3]/a')
        return True
    except:
        return False

def search_jobs(url, path):
    browser = open_browser(url)

    jobs_list = []

    if check_pagination(browser) == True:
        browser.find_element_by_xpath('//*[@id="pagination-bottom"]/div[3]/a').click()
        time.sleep(3)

    soup = bs.BeautifulSoup(browser.page_source, 'lxml')
    browser.quit()
    jobs_section = soup.find('section', {'id': 'search-results-list'})
    jobs_soup = jobs_section.find_all('a')

    for job in jobs(jobs_soup, path):
        jobs_list.append(job)

    return jobs_list

def jobs(soup, path):
    for job in soup:
        if job.has_attr('data-job-id'):
            link = urljoin('%s' % path, job.get('href'))
            title = job.find('h2').text
            yield link, title

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-url', required=True, help="tenethealth url")
    parser.add_argument('-output', required=True, help="name of rss file ex: feed.xml")
    parser.add_argument('-title', required=True, help="name in RSS feed <title> tag")
    parser.add_argument('-link', required=True, help="location in RSS feed <link> tag")

    args = parser.parse_args()

    jobs = search_jobs(args.url, 'https://jobs.tenethealth.com/')
    rss_feed = rsswriter.format_rss(jobs, args.title, args.link)

    with open(args.output, 'w+') as f:
        f.write(rss_feed)

if __name__ == '__main__':
    main()
