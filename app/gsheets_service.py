from google_sheets_api import GoogleSheetsApi


class GoogleSheetsService:
    URLS_COL_HEADER = 'Ссылка на аукцион'

    def __init__(self, sheet_id: str, worksheet_title: str) -> None:
        self.__sheet_id = sheet_id
        self.__worksheet = worksheet_title
        self.__api = GoogleSheetsApi(sheet_id, worksheet_title)

    def add_telderi_rows(self, telderi_data: list[list], telderi_sheet: str | None = None) -> None:
        self.__api.set_worksheet(telderi_sheet if telderi_sheet else self.__worksheet)
        self.__api.add_values(telderi_data)

    def get_all_urls(self, urls_col_header: str = URLS_COL_HEADER, log: bool = True) -> set[str]:
        worksheets = self.__api.all_worksheets()
        all_urls = set()
        for worksheet_idx, worksheet_title in enumerate(worksheets):
            self.__api.set_worksheet(worksheet_title)
            headers = list(self.__api.get_row(1))
            if not urls_col_header in headers:
                continue

            col_index = headers.index(urls_col_header) + 1
            urls_column = self.__api.get_col(col_index)

            if len(urls_column):
                all_urls = all_urls.union(set(urls_column))

            if log:
                print(f"Worksheet: {worksheet_idx + 1}/{len(worksheets)}. "
                      f"Title: {worksheet_title}. Parsed: {len(all_urls)}. Urls in col {col_index}")

        return all_urls
