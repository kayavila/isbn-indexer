import requests
from isbn_resolver.resolver import ISBNResolver, NoBookDataError


class OpenLibraryResolver(ISBNResolver):

    def get_book_author(self, isbn) -> list:
        book_data = self.get_book_data(isbn)

        # Don't have it locally and couldn't successfully query
        if not book_data:
            raise NoBookDataError

        results = []
        for a in book_data[isbn]['details']['authors']:
            results.append(a['name'])

        return results

    def _get_query_request(self, isbn: str) -> requests.Request:
        u = 'https://openlibrary.org/api/books?bibkeys=ISBN:{}&jscmd=details&format=json'.format(isbn)
        return requests.Request(url=u)

    def _parse_response(self, isbn: str, book_data_response: requests.Response) -> dict:
        book_json = book_data_response.json()

        # Expecting only one entry, but double-check
        assert len(book_json) == 1

        book_data = next(iter(book_json.items()))[1]
        return {isbn: book_data}
