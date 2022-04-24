import csv
import sys
from pprint import pprint
from isbn_resolver.resolver import MissingDataError, NoBookDataError, ISBNResolver
from isbn_resolver.openlibrary import OpenLibraryResolver
from isbn_resolver.isbndb import ISBNDBResolver


def get_or_return_none(isbn: str, resolver_method):
    try:
        return resolver_method(isbn)
    except NoBookDataError:
        return None
    except MissingDataError:
        return None


if __name__ == '__main__':

    OPEN_LIBRARY_DB = 'openlibrary_db.txt'
    ISBNDB_DB = 'isbndb_db.txt'
    INPUT_FILE = 'isbn_list.txt'
    OUTPUT_FILE = 'book_list.csv'

    if len(sys.argv) < 2:
        print('No API key specified for ISBN DB', file=sys.stderr)
        sys.exit(-1)
    ISBNDB_API_KEY = sys.argv[1]

    open_library = OpenLibraryResolver(OPEN_LIBRARY_DB)
    isbn_db = ISBNDBResolver(ISBNDB_DB, ISBNDB_API_KEY)

    bad_isbns = []
    with open(INPUT_FILE) as infile, open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as outfile:
        csv_outfile = csv.writer(outfile)
        heading = ['isbn', 'ol_title', 'idb_title', 'ol_author', 'idb_author', 'ol_contributor', 'ol_by',
                   'ol_publisher', 'idb_publisher', 'ol_location', 'ol_year', 'idb_year', 'ol_pages',
                   'idb_pages', 'idb_msrp']
        csv_outfile.writerow(heading)
        for line in infile:
            isbn = line.rstrip()

            ol_title = get_or_return_none(isbn, open_library.get_title)
            idb_title = get_or_return_none(isbn, isbn_db.get_title)

            # Quit if we don't have a title from either one
            if not ol_title and not idb_title:
                bad_isbns.append(isbn)
                continue

            book_data = [isbn, ol_title, idb_title]

            # Order: titles x2, author x2, OL contributor, OL by_statement, publisher x2, OL location, year x2,
            #          page_count x2, ISBNDB msrp
            queries = [
                open_library.get_author,
                isbn_db.get_author,
                open_library.get_contributors,
                open_library.get_by_statement,
                open_library.get_publisher,
                isbn_db.get_publisher,
                open_library.get_location,
                open_library.get_year,
                isbn_db.get_year,
                open_library.get_page_count,
                isbn_db.get_page_count,
                isbn_db.get_msrp
            ]

            for q in queries:
                book_data.append(get_or_return_none(isbn, q))

            csv_outfile.writerow(book_data)
