from gsheets_service import GoogleSheetsService
from telderi_parser import TelderiParser
from dotenv import load_dotenv
from datetime import date
import argparse

load_dotenv()

SITES_SHEET_ID = '1xkhXmZlNsyCYC4qiMrwywcVJl-EhZ_2IqD5xOvMzVmw'
DOMAINS_SHEET_ID = '1Z3zhcQkPHKcHapGCOC2-b88hdy8MX6mcrxOK1L8fzQM'
TYPES = {'site': SITES_SHEET_ID, 'domain': DOMAINS_SHEET_ID}


def __parse_data(type: str, sheet_id: str):
    sheets_service = GoogleSheetsService(sheet_id, date.today().strftime('%d.%m.%Y'))

    all_urls = sheets_service.get_all_urls()

    def predicate(url):
        r = url not in all_urls
        if r: print(f"'{url}' {r}")
        return r

    parser = TelderiParser(sheets_service)
    if type == 'site':
        parser.parse_sites_data(predicate=predicate)
    else:
        parser.parse_domains_data(predicate=predicate)
    print('Success!')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', default="site", type=str, help='type of parsing. valid: `site`, `domain`')
    args = parser.parse_args()

    if args.type not in TYPES.keys():
        raise Exception('Invalid parsing type')

    __parse_data(args.type, TYPES[args.type])


if __name__ == '__main__':
    main()
