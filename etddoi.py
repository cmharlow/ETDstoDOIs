#! /usr/bin/env python

# Run in same working directory as files. See README.md for usage examples.
from argparse import ArgumentParser
import sys


def main():
    """main operation of script."""
    parser = ArgumentParser(usage='%(prog)s [options] ecommonsMetadata.csv')
    parser.add_argument("-t", "--test", dest="store_true",
                        help="run on sandbox DOI")
    parser.add_argument("-d", "--date", dest="date",
                        help="Date on or after that an ETD was published for \
                        creating DOIs. Put in format YYYY-MM")
    parser.add_argument("datafile", help="eCommons metadata worked from.")

    args = parser.parse_args()

    if not len(sys.argv) > 0:
        parser.print_help()
        parser.exit()




if __name__ == '__main__':
    # eventually add tests?
    main()
