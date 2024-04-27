from gsheets_service import GoogleSheetsService
from telderi_parser import TelderiParser
from dotenv import load_dotenv
from datetime import date

load_dotenv()

SHEET_ID = '1xkhXmZlNsyCYC4qiMrwywcVJl-EhZ_2IqD5xOvMzVmw'


def main():
    sheets_service = GoogleSheetsService(SHEET_ID, date.today().strftime('%d.%m.%Y'))

    # all_urls = sheets_service.get_all_urls()
    all_urls = set(map(lambda line: line.strip(), open('urls.txt').readlines()))

    def predicate(url):
        r = url not in all_urls
        if r: print(f"'{url}' {r}")
        return r

    parser = TelderiParser(sheets_service)
    parser.parse_sites_data(predicate=predicate)
    print('Success!')


if __name__ == '__main__':
    main()
