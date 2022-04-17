import re
import requests
from isbn_resolver.resolver import ISBNResolver, NoBookDataError, MissingDataError


class OpenLibraryResolver(ISBNResolver):

    def get_author(self, isbn) -> list:
        book_data = self.get_book_data(isbn)

        # Don't have it locally and couldn't successfully query
        if not book_data:
            raise NoBookDataError

        results = []

        try:
            authors = book_data[isbn]['details']['authors']
        except KeyError:
            raise MissingDataError('No author data for isbn {}'.format(isbn))

        for a in authors:
            results.append(a['name'])

        return results

    def get_year(self, isbn) -> int:
        book_data = self.get_book_data(isbn)

        # Don't have it locally and couldn't successfully query
        if not book_data:
            raise NoBookDataError

        try:
            date = book_data['details']['publish_date']
        except KeyError:
            raise MissingDataError('No publication date for isbn {}'.format(isbn))

        # Quick and dirty check to see if we're getting formats other than just year from OpenLibrary
        assert re.match('[1-9]([0-9]){3}', date)

        return int(date)

    def get_page_count(self, isbn) -> int:
        book_data = self.get_book_data(isbn)

        # Don't have it locally and couldn't successfully query
        if not book_data:
            raise NoBookDataError

        try:
            num_pages = book_data['details']['number_of_pages']
        except KeyError:
            raise MissingDataError('No page count data for isbn {}'.format(isbn))

        return int(num_pages)


    def _get_query_request(self, isbn: str) -> requests.Request:
        u = 'https://openlibrary.org/api/books?bibkeys=ISBN:{}&jscmd=details&format=json'.format(isbn)
        return requests.Request('GET', url=u)

    def _parse_response(self, isbn: str, book_data_response: requests.Response) -> dict:
        book_json = book_data_response.json()

        # Expecting only one entry, but double-check
        assert len(book_json) == 1

        book_data = next(iter(book_json.items()))[1]
        return {isbn: book_data}
