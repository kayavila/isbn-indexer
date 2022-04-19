import requests
from isbn_resolver.resolver import ISBNResolver, NoBookDataError


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
        return {isbn: book_data}

    def get_msrp(self, isbn) -> list:
        pass

    def get_author(self, isbn) -> list:
        pass

    def get_year(self, isbn) -> int:
        pass

    def get_page_count(self, isbn) -> int:
        pass

    def get_publisher(self, isbn) -> int:
        pass

    def get_location(self, isbn) -> int:
        pass


