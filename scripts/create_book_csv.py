import sys
from isbn_resolver.resolver import MissingDataError, NoBookDataError
from isbn_resolver.openlibrary import OpenLibraryResolver
from isbn_resolver.isbndb import ISBNDBResolver

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

    with open(INPUT_FILE) as infile:
        for line in infile:
            isbn = line.rstrip()

    