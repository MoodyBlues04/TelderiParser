import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from typing import Callable
from gsheets_service import GoogleSheetsService
from selenium.webdriver.chrome.options import Options
from os import getenv


class TelderiParser:
    TELDERI_URL = 'https://www.telderi.ru/ru/search/website'
    LINK_XPATH = '//*[@id="__next"]/div[2]/div/div[2]/div[6]/div/div/a'
    NEXT_PAGE_XPATH = '//*[@id="__next"]/div[2]/div/div[2]/div[4]/div[2]/nav/ul/li[9]/button'
    TRAFFIC_ELS_XPATH = '/html/body/div[1]/div/div[2]/div[4]/div/div/div/div/div[1]/div/div[3]/div[1]/div[10]/div[1]/div[11]/div/div[1]/div'

    PAGES_COUNT = 122
    MAX_BATCH_SIZE = 40

    __browser: webdriver

    def __init__(self, gsheets_service: GoogleSheetsService):
        if getenv('CHROME_PATH'):
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            self.__browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        else:
            self.__browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        self.__gsheets_service = gsheets_service

    # def __del__(self):
    #     self.__browser.close()
    #     self.__browser.quit()

    def parse_sites_data(self, predicate: Callable[[str], bool] | None = None) -> None:
        if predicate is None:
            predicate = lambda el: True

        sites_data = []

        self.__browser.get(self.TELDERI_URL)
        self.__browser.maximize_window()

        for page_idx in range(self.PAGES_COUNT):
            print(f'Parsing telderi page: {page_idx+1}/{self.PAGES_COUNT}. Total parsed: {len(sites_data)}')

            if len(sites_data) >= self.MAX_BATCH_SIZE:
                self.__gsheets_service.add_telderi_rows(sites_data)
                print(f'Telderi sites set to sheet. Rows added: {len(sites_data)}')
                sites_data.clear()

            sites_elements = self.__browser.find_elements(By.XPATH, self.LINK_XPATH)
            for site_el in sites_elements:
                telderi_url = site_el.get_attribute('href')
                if not predicate(telderi_url):
                    continue

                sites_data.append(self.__get_site_data(site_el, telderi_url))

            self.__browser.find_element(By.XPATH, self.NEXT_PAGE_XPATH).click()
            time.sleep(4)

        if len(sites_data) > 0:
            self.__gsheets_service.add_telderi_rows(sites_data)
            print(f'Telderi sites set to sheet. Rows added: {len(sites_data)}')

    def __get_site_data(self, site_el: WebElement, telderi_url: str) -> list:
        site_urls = site_el.find_elements(By.XPATH, "./div/div[2]/div/div[2]/div[1]/a")
        site_url = site_urls[0].get_attribute('href') if len(site_urls) else None

        traffic_el = site_el.find_element(By.XPATH, './div/div[2]/div/div[2]/div[2]/div/div[1]/p')
        traffic = traffic_el.text[8:].replace(' ', '')

        iks_el = site_el.find_element(By.XPATH, './div/div[2]/div/div[2]/div[2]/div/div[2]/p')
        iks = iks_el.text[4:].replace(' ', '')

        remaining_time_el = site_el.find_element(By.XPATH, './div/div[4]/p')
        remaining_time = remaining_time_el.text

        self.__browser.execute_script(f'''window.open("{telderi_url}","_blank");''')
        tabs = self.__browser.window_handles
        self.__browser.switch_to.window(tabs[1])
        time.sleep(1)
        google_traffic, yandex_traffic = self.__get_traffic_by_key('Google', 'Яндекс')
        self.__browser.close()
        self.__browser.switch_to.window(tabs[0])
        time.sleep(3)

        return [(site_url if site_url else ''), '', '', traffic, google_traffic, yandex_traffic, remaining_time, iks, telderi_url]

    def __get_traffic_by_key(self, *keys: str) -> list:
        from selenium.common.exceptions import NoSuchElementException

        traffic = [None] * len(keys)
        for i in range(1, 10):
            try:
                traffic_el = self.__browser.find_element(By.XPATH, self.TRAFFIC_ELS_XPATH + f'[{i}]')
            except NoSuchElementException:
                continue
            if traffic_el is None:
                continue

            lines = traffic_el.text.splitlines()
            if len(lines) != 2:
                continue

            title, value = lines
            for key_i, key in enumerate(keys):
                if title == key:
                    traffic[key_i] = value.split(' / ')[1]
                    continue
        return traffic

    def _find(self, by: str, identifier: str) -> WebElement:
        return self.__browser.find_element(by, identifier)
