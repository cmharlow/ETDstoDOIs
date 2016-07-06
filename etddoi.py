#! /usr/bin/env python

# Run in same working directory as files. See README.md for usage examples.
from argparse import ArgumentParser
import sys
import csv
import re
import pprint

year_re = re.compile("^[0-9]{4}\-+.+$")


def testDate(ECdata, dateAfter):
    """Remove from ECdata all records not after date given."""
    recdate = ''
    newdata = []
    for record in ECdata:
        # Grab dates from variety of places EC stores.
        if record['dc.date.issued']:
            if year_re.match(record['dc.date.issued']):
                recdate = record['dc.date.issued']
        elif record['dc.date.issued[]']:
            if year_re.match(record['dc.date.issued[]']):
                recdate = record['dc.date.issued[]']
        elif record['dc.date.issued[en_US]']:
            if year_re.match(record['dc.date.issued[en_US]']):
                recdate = record['dc.date.issued[en_US]']
        else:
            with open('nodateETDs.txt', 'a') as fh:
                fh.write(record['id'])
                fh.write('\n')

        # If there is a date, check it against the provided, write to newdata.
        if recdate:
            recyear = recdate[:4]
            recmonth = recdate[5:7]
            afteryear = dateAfter[:4]
            aftermonth = dateAfter[5:7]
            if recyear >= afteryear and recmonth >= aftermonth:
                newdata.append(record)
    return(newdata)


def checkDOI(olddata):
    newdata = []
    for record in olddata:
        # See if DOI is already there.
        try:
            if not record['dc.identifier.doi'] and not record['dc.identifier.doi[]'] and not record['dc.identifier.doi[en_US]']:
                newdata.append(record)
        except KeyError:
            newdata.append(record)
    return(newdata)


def csvParse(datafile, dateAfter):
    """Take eCommons CSV, rewrite for our needs (workflow step 2)."""
    with open(datafile, 'r') as ECfile:
        ECreader = csv.DictReader(ECfile)
        ECdata = [x for x in ECreader]
        print(len(ECdata))
    # delete records for items issued after date provided
    ECdataDate = testDate(ECdata, dateAfter)
    data = checkDOI(ECdataDate)
    print(len(data))


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

    csvParse(args.datafile, args.date)


if __name__ == '__main__':
    # eventually add tests?
    main()
