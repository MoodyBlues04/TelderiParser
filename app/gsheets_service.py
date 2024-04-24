import time

from google_sheets_api import GoogleSheetsApi


class GoogleSheetsService:
    def __init__(self, sheet_id: str, worksheet_title: str) -> None:
        self.__sheet_id = sheet_id
        self.__worksheet = worksheet_title
        self.__api = GoogleSheetsApi(sheet_id, worksheet_title)

    def set_telderi_rows(self, telderi_data: list[list]) -> None:
        self.__api.set_worksheet(self.__worksheet)
        self.__api.add_rows(telderi_data)

    def get_all_urls(self, urls_col: int, log: bool = True) -> set[str]:
        worksheets = self.__api.all_worksheets()
        all_urls = set()
        for worksheet_idx, worksheet_title in enumerate(worksheets):
            if log:
                print(f"Worksheet: {worksheet_idx + 1}/{len(worksheets)}. "
                      f"Title: {worksheet_title}. Parsed: {len(all_urls)}")

            self.__api.set_worksheet(worksheet_title)
            urls_column = self.__api.get_col(urls_col)
            if len(urls_column):
                all_urls = all_urls.union(set(urls_column[1:]))

            if worksheet_idx % 10 == 0:
                time.sleep(5)

        return all_urls
