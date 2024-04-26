from gsheets_service import GoogleSheetsService
from telderi_parser import TelderiParser
from dotenv import load_dotenv
from datetime import date

load_dotenv()

SHEET_ID = '1xkhXmZlNsyCYC4qiMrwywcVJl-EhZ_2IqD5xOvMzVmw'


def main():
    sheets_service = GoogleSheetsService(SHEET_ID, date.today().strftime('%d.%m.%Y'))

    all_urls = sheets_service.get_all_urls()
    parser = TelderiParser(sheets_service)
    parser.parse_sites_data(predicate=lambda url: url not in all_urls)
    # parser.parse_sites_data()
    # sheets_service.add_telderi_rows(telderi_data)
    print('Success!')


if __name__ == '__main__':
    main()
