import requests
from isbn_resolver.resolver import ISBNResolver, NoBookDataError


class ISBNDBResolver(ISBNResolver):

    def __init__(self, data_file: str, api_key: str):
        self.api_key = api_key
        super().__init__(data_file)

    def get_query_request(self, isbn: str) -> requests.Request:
        h = {'Authorization': self.api_key}
        u = 'https://api2.isbndb.com/book/{}'.format(isbn)

        return requests.Request(url=u, headers=h)
