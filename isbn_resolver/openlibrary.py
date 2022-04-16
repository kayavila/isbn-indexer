import requests
from isbn_resolver.resolver import ISBNResolver


class OpenLibraryResolver(ISBNResolver):

    def _get_query_request(self, isbn: str):
        return 'https://openlibrary.org/api/books?bibkeys=ISBN:{}&jscmd=details&format=json'.format(isbn)

    def _parse_response(self, isbn: str, book_data_response: requests.Response) -> dict:
        book_json = book_data_response.json()

        # Expecting only one entry, but double-check
        assert len(book_json) == 1

        book_data = next(iter(book_json.items()))[1]
        return {isbn: book_data}