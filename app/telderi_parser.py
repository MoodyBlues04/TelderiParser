import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from typing import Callable
from selenium.common.exceptions import StaleElementReferenceException

class TelderiParser:
    TELDERI_URL = 'https://www.telderi.ru/ru/search/website'
    LINK_XPATH = '//*[@id="__next"]/div[2]/div/div[2]/div[6]/div/div/a'
    NEXT_PAGE_XPATH = '//*[@id="__next"]/div[2]/div/div[2]/div[4]/div[2]/nav/ul/li[9]/button'
    PAGES_COUNT = 122

    def __init__(self):
        self.__browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def get_sites_data(self, predicate: Callable[[str], bool] | None = None) -> list:
        sites_data = []

        if predicate is None:
            predicate = lambda el: True

        self.__browser.get(self.TELDERI_URL)
        self.__browser.maximize_window()

        for page_idx in range(self.PAGES_COUNT):
            print(f'Parsing telderi page: {page_idx+1}/{self.PAGES_COUNT}. Total parsed: {len(sites_data)}')

            sites_elements = self.__browser.find_elements(By.XPATH, self.LINK_XPATH)
            for site_el in sites_elements:
                telderi_url = site_el.get_attribute('href')
                if not predicate(telderi_url):
                    continue

                sites_data.append(self.__get_site_data(site_el, telderi_url))

            self.__browser.find_element(By.XPATH, self.NEXT_PAGE_XPATH).click()
            time.sleep(3)

        return sites_data

    def __get_site_data(self, site_el: WebElement, telderi_url: str) -> list:
        site_urls = site_el.find_elements(By.XPATH, "./div/div[2]/div/div[2]/div[1]/a")
        site_url = site_urls[0].get_attribute('href') if len(site_urls) else None

        traffic_el = site_el.find_element(By.XPATH, './div/div[2]/div/div[2]/div[2]/div/div[1]/p')
        traffic = traffic_el.text[8:].replace(' ', '')

        iks_el = site_el.find_element(By.XPATH, './div/div[2]/div/div[2]/div[2]/div/div[2]/p')
        iks = iks_el.text[4:].replace(' ', '')

        remaining_time_el = site_el.find_element(By.XPATH, './div/div[4]/p')
        remaining_time = remaining_time_el.text

        return [(site_url if site_url else ''), '', '', traffic, iks, telderi_url, remaining_time]

    def _find(self, by: str, identifier: str) -> WebElement:
        return self.__browser.find_element(by, identifier)
