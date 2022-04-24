import requests
from typing import Union
from isbn_resolver.resolver import ISBNResolver


class ISBNDBResolver(ISBNResolver):

    def __init__(self, data_file: str, api_key: str):
        self.api_key = api_key
        super().__init__(data_file)

    def _get_query_request(self, isbn: str) -> requests.Request:
        h = {'Authorization': self.api_key}
        u = 'https://api2.isbndb.com/book/{}'.format(isbn)

        return requests.Request('GET', url=u, headers=h)

    def _parse_response(self, isbn: str, book_data_response: requests.Response) -> dict:
        book_json = book_data_response.json()

        # Expecting only one entry, but double-check
        assert len(book_json) == 1

        book_data = book_json['book']
        return book_data

    def get_msrp(self, isbn) -> float:
        return float(self._get_data_or_error(isbn, ('msrp',), 'msrp'))

    def get_author(self, isbn) -> Union[str, list[str]]:
        authors = self._get_data_or_error(isbn, ('authors',), 'author')
        return ISBNResolver._unlist_if_singular(authors)

    def get_title(self, isbn):
        return self._get_data_or_error(isbn, ('title',), 'title')

    def get_year(self, isbn) -> int:
        date = self._get_data_or_error(isbn, ('date_published',), 'publication date')
        return ISBNResolver._parse_date(date)

    def get_page_count(self, isbn) -> int:
        page_count = self._get_data_or_error(isbn, ('pages',), 'page count')
        return int(page_count)

    def get_publisher(self, isbn) -> int:
        return self._get_data_or_error(isbn, ('publisher',), 'publisher')
