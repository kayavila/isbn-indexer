import re
import copy
import json
import requests
from sys import stderr
from time import sleep
from pathlib import Path
from typing import Union
from requests.exceptions import ConnectionError, ConnectTimeout


class QueryFailedError(Exception):
    pass


class NoBookDataError(Exception):
    pass


class MissingDataError(Exception):
    pass


class ISBNResolver:
    def __init__(self, data_file: str):
        self.data_file = Path(data_file)
        self.data = {}

        # Load the contents of an existing data file, if present
        try:
            with open(self.data_file) as input_file:
                for line in input_file:
                    self.data.update(json.loads(line))

        except FileNotFoundError:
            self.data_file.touch()

    def get_book_data(self, isbn: str, verbose: bool = False) -> Union[dict, None]:
        """
        Return raw information about the related book, either from locally saved information
        (if available), or otherwise queries the backend service.

        :param isbn: A 10-digit or 13-digit ISBN
        :param verbose: Whether to print debugging information
        :return:
        """
        # Ensure isbns are always strings
        isbn = str(isbn)

        # Simply return if we have it already
        if isbn in self.data:
            return self.data[isbn]

        # Otherwise, query for it
        book_data = self._query_service(isbn, verbose)
        with open(self.data_file, 'a') as output_file:  # Save it to the disk for later
            json.dump(book_data, output_file)
            output_file.write('\n')
        self.data[isbn] = book_data

        return book_data

    @staticmethod
    def _parse_date(date_string: str) -> int:
        matches = re.findall('[12][0-9]{3}', str(date_string))

        # Should only match one year
        assert len(matches) == 1

        return int(matches[0])

    @staticmethod
    def _unlist_if_singular(some_list: list) -> Union[list, object]:
        if len(some_list) == 1:
            return some_list[0]
        elif len(some_list) == 0:
            return ''
        else:
            return some_list

    def get_author(self, isbn) -> list:
        """
        Return a list of authors of a book

        :param isbn: A 10-digit or 13-digit ISBN
        :return: A list of authors, potentially empty
        """
        pass

    def get_title(self, isbn) -> list:
        """
        Return the title of a book

        :param isbn: A 10-digit or 13-digit ISBN
        :return: A list of authors, potentially empty
        """
        pass

    def get_year(self, isbn) -> int:
        """
        Return the original publication year of a book

        :param isbn: A 10-digit or 13-digit ISBN
        :return: An integer value for year
        """

    def get_page_count(self, isbn) -> int:
        """
        Return the number of pages for a book

        :param isbn: A 10-digit or 13-digit ISBN
        :return: An integer value for number of pages
        """

    def get_publisher(self, isbn) -> int:
        """
        Return the number of pages for a book

        :param isbn: A 10-digit or 13-digit ISBN
        :return: A list of publishers, potentially empty
        """

    def _get_query_request(self, isbn) -> requests.Request:
        """
        Generates the appropriate query for the backend service

        :param isbn: A 10-digit or 13-digit ISBN
        :return: The requests Request to be executed
        """
        pass

    def _parse_response(self, isbn: str, book_data_response) -> dict:
        """
        Takes the response from the backend service and returns it re-structured,
        into a standardized format

        :param isbn: A 10-digit or 13-digit ISBN
        :param book_data_response: The response from the backend service
        :return: A dictionary structured as {isbn: book_data}
        """
        pass

    def _get_data_or_error(self, isbn: str, path: tuple, error_msg_type: str):
        """
        Used to either get book data or throw an error

        :param isbn: A 10-digit or 13-digit isbn
        :param path: The path inside the stored book data to traverse
        :param error_msg_type: The type of data, to be included in any error messages
        :return: The data requested in the path
        """
        # Ensure isbns are always strings
        isbn = str(isbn)

        book_data = self.get_book_data(isbn)

        # Keep trying to go down one level at a time
        selected_data = copy.deepcopy(book_data)
        try:
            for p in path:
                selected_data = selected_data[p]
        except KeyError:
            raise MissingDataError('No {} data for isbn {}'.format(error_msg_type, isbn))

        return selected_data

    def _query_service(self, isbn: str, verbose: bool = False):
        """
        Queries a backend service for data about the related book

        :param isbn: A 10-digit or 13-digit ISBN
        :param verbose: Whether to print debugging information
        :return: Information about the book
        """
        req = self._get_query_request(isbn)
        url = req.url
        prepped_req = req.prepare()
        session = requests.Session()

        # Only try three times before giving up
        attempts_left = 3
        response = None
        while attempts_left > 0 and response is None:
            try:
                response = session.send(prepped_req)
            except (ConnectionError, ConnectTimeout):
                if verbose:
                    stderr.write('Encountered error attempting to access {}.  Retrying in 5 seconds...\n'.format(url))
                attempts_left -= 1
                sleep(5)

        if attempts_left == 0:  # If we were unable to ever query successfully...
            if verbose:
                stderr.write('Unable to access {}.  Giving up after three attempts.'.format(url))
            raise QueryFailedError('Unable to access URL {}\n'.format(url))

        # 404 error indicates that there's no data, stop trying
        elif response.status_code == 404 or not response.text:
            if verbose:
                stderr.write('No data received for URL {}\n'.format(url))
            raise NoBookDataError

        # Sometimes we get JSON, but it's empty
        elif response.json() == {}:
            if verbose:
                stderr.write('Empty data received for URL {}\n'.format(url))
            raise NoBookDataError

        elif response.status_code != 200:  # Otherwise, there's some sort of issue, and it should be retried later
            if verbose:
                stderr.write('Received HTTP status code {} when attempting to access {}\n'.format(response.status_code,
                                                                                                  url))
            raise QueryFailedError(
                'Received status code {} accessing URL {}'.format(response.status_code, url))

        return self._parse_response(isbn, response)
