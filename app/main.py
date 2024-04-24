from gsheets_service import GoogleSheetsService
from telderi_parser import TelderiParser
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = '1xkhXmZlNsyCYC4qiMrwywcVJl-EhZ_2IqD5xOvMzVmw'
WORKSHEET = 'Рабочий лист Георгий'
URLS_COL = 10


def main():
    sheets_service = GoogleSheetsService(SHEET_ID, WORKSHEET)
    all_urls = sheets_service.get_all_urls(URLS_COL)

    parser = TelderiParser()
    telderi_data = parser.get_sites_data(predicate=lambda url: url not in all_urls)
    # telderi_data = parser.get_sites_data()
    sheets_service.set_telderi_rows(telderi_data)
    print('Success!')


if __name__ == '__main__':
    main()
