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

    def get_book_data(self, isbn: str, verbose: bool = False):
        """
        Return raw information about the related book, either from locally saved information
        (if available), or otherwise queries the backend service.

        :param isbn: A 10-digit or 13-digit ISBN
        :param verbose: Whether to print debugging information
        :return:
        """
        # Simply return if we have it already
        if isbn in self.data:
            return self.data[isbn]

        # Otherwise, query for it
        book_data = self._query_service(isbn, verbose)
        with open(self.data_file, 'a') as output_file:  # Save it to the disk for later
            json.dump(book_data, output_file)
            output_file.write('\n')
        self.data[isbn] = book_data

        # May or may not have an answer, that may or may not be None
        if isbn in self.data:
            return self.data[isbn]
        else:
            return None

    def get_book_author(self, isbn) -> list:
        """
        Return a list of authors of a book

        :param isbn: A 10-digit or 13-digit ISBN
        :return: A list of authors, potentially empty
        """
        pass

    def _get_query_request(self, isbn) -> str:
        """
        Generates the appropriate query for the backend service

        :param isbn:
        :return: A URL query string
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

    def _query_service(self, isbn: str, verbose: bool = False):
        """
        Queries a backend service for data about the related book

        :param isbn: A 10-digit or 13-digit ISBN
        :param verbose: Whether to print debugging information
        :return: Information about the book
        """
        url = self._get_query_request(isbn)

        # Only try three times before giving up
        attempts_left = 3
        response = None
        while attempts_left > 0 and response is None:
            try:
                response = requests.get(url)
            except (ConnectionError, ConnectTimeout):
                if verbose:
                    stderr.write('Encountered error attempting to access {}.  Retrying in 5 seconds...\n'.format(url))
                attempts_left -= 1
                sleep(5)

        if attempts_left == 0:  # If we were unable to ever query successfully...
            if verbose:
                stderr.write('Unable to access {}.  Giving up after three attempts.'.format(url))
            raise QueryFailedError('Unable to access URL {}\n'.format(url))

        elif response.status_code == 404 or not response.text:  # 404 error indicates that there's no data, stop trying
            if verbose:
                stderr.write('No data received for URL {}\n'.format(url))
            return None

        elif response.status_code != 200:  # Otherwise, there's some sort of issue, and it should be retried later
            if verbose:
                stderr.write('Received HTTP status code {} when attempting to access {}\n'.format(response.status_code,
                                                                                                  url))
            raise QueryFailedError(
                'Received status code {} accessing URL {}'.format(response.status_code, url))

        return self._parse_response(isbn, response)
