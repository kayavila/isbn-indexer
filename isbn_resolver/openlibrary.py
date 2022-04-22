import re
import requests
from isbn_resolver.resolver import ISBNResolver, NoBookDataError, MissingDataError


class OpenLibraryResolver(ISBNResolver):

    def _get_query_request(self, isbn: str) -> requests.Request:
        u = 'https://openlibrary.org/api/books?bibkeys=ISBN:{}&jscmd=details&format=json'.format(isbn)
        return requests.Request('GET', url=u)

    def _parse_response(self, isbn: str, book_data_response: requests.Response) -> dict:
        book_json = book_data_response.json()

        # Expecting only one entry, but double-check
        assert len(book_json) == 1

        book_data = next(iter(book_json.items()))[1]
        return book_data

    def get_title(self, isbn):
        return self._get_data_or_error(isbn, ('details', 'title'), 'title')

    def get_author(self, isbn) -> list:
        authors = self._get_data_or_error(isbn, ('details', 'authors'), 'author')

        results = []
        for a in authors:
            results.append(a['name'])

        return results

    def get_year(self, isbn) -> int:
        date = self._get_data_or_error(isbn, ('details', 'publish_date'), 'publication date')
        return self.parse_date(date)

    def get_page_count(self, isbn) -> int:
        num_pages = self._get_data_or_error(isbn, ('details', 'number_of_ages'), 'publication date')
        return int(num_pages)

    def get_publisher(self, isbn) -> int:
        return self._get_data_or_error(isbn, ('details', 'publishers'), 'publisher')

    def get_location(self, isbn) -> int:
        return self._get_data_or_error(isbn, ('details', 'publish_places'), 'publication location')

