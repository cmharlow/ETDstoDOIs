#! /usr/bin/env python
"""Run in same working directory as files. See README.md for usage examples."""
from argparse import ArgumentParser
import sys
import csv
import time
import os
import re
from datetime import datetime
year_re = re.compile("^[0-9]{4}\-+.+$")
unneeded = ['dc.contributor.chair', 'dc.contributor.chair[]',
            'dc.contributor.chair[en_US]', 'dc.contributor.coChair[]',
            'dc.contributor.coChair[en_US]', 'dc.contributor.committeeMember',
            'dc.contributor.committeeMember[]',
            'dc.contributor.committeeMember[en_US]',
            'dc.description', 'dc.description.abstract',
            'dc.description.abstract[]', 'dc.description.abstract[en]',
            'dc.description.abstract[en_US]', 'dc.description.embargo',
            'dc.description.embargo[]', 'dc.description.embargo[en]',
            'dc.description.embargo[en_US]', 'dc.description.sponsorship',
            'dc.description.sponsorship[en]',
            'dc.description.sponsorship[en_US]', 'dc.description[en]',
            'dc.description[en_US]', 'dc.format.extent', 'dc.format.mimetype',
            'dc.identifier.citation[en]', 'dc.identifier.citation[en_US]',
            'dc.identifier.isbn', 'dc.identifier.issn', 'dc.language.iso',
            'dc.language.iso[]', 'dc.language.iso[en]',
            'dc.language.iso[en_US]', 'dc.relation.hasversion[en_US]',
            'dc.relation.ispartofseries', 'dc.relation.ispartofseries[en]',
            'dc.relation.ispartofseries[en_US]', 'dc.subject', 'dc.subject[]',
            'dc.subject[en]', 'dc.subject[en_US]', 'dc.title.alternative[en]',
            'dc.title.alternative[en_US]', 'dc.type[]', 'dc.type[en]',
            'dc.type[en_US]', 'thesis.degree.discipline',
            'thesis.degree.discipline[]', 'thesis.degree.discipline[en_US]',
            'thesis.degree.grantor', 'thesis.degree.grantor[]',
            'thesis.degree.grantor[en_US]', 'thesis.degree.level',
            'thesis.degree.level[]', 'thesis.degree.level[en_US]',
            'thesis.degree.name', 'thesis.degree.name[]',
            'thesis.degree.name[en_US]']


def testDate(ECdata, dateAfter):
    """Remove from ECdata all records not after date given."""
    givendate = datetime(int(dateAfter[:4]), int(dateAfter[5:7]), 1)
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
                pass

        # If there is a date, check it against the provided, write to newdata.
        if recdate:
            founddate = datetime(int(recdate[:4]), int(recdate[5:7]), 1)
            if founddate >= givendate:
                newdata.append(record)
    return(newdata)


def checkDOI(olddata):
    """Check to see if a DOI already exists for the eCommon item."""
    newdata = []
    for record in olddata:
        # See if DOI is already there.
        try:
            if not record['dc.identifier.doi'] and not record['dc.identifier.doi[]'] and not record['dc.identifier.doi[en_US]']:
                newdata.append(record)
        except KeyError:
            newdata.append(record)
    return(newdata)


def slimECdata(olddata):
    """Remove fields not needed for DOI generation or eCommons."""
    newdata = olddata
    for record in newdata:
        for field in unneeded:
            try:
                del record[field]
            except KeyError:
                pass
    return(newdata)


def csvparse(datafile, dateAfter, skipDOItest=False):
    """Take eCommons CSV, rewrite for our needs (workflow step 2)."""
    with open(datafile, 'r') as ECfile:
        ECreader = csv.DictReader(ECfile)
        ECdata = [x for x in ECreader]
        print("Records in the collection: " + str(len(ECdata)))
    # delete fields we don't need
    ECdataSlim = slimECdata(ECdata)
    # delete records for items issued after date provided
    ECdataDate = testDate(ECdataSlim, dateAfter)
    if not skipDOItest:
        data = checkDOI(ECdataDate)
        print("Records to be updated with DOIs: " + str(len(data)))
    else:
        data = ECdataDate
        print("Records to be altered: " + str(len(data)))
    # Create working directory for this job
    now = time.localtime()[0:6]
    dirfmt = "data/%4d%02d%02d_%02d%02d%02d/"
    dirname = dirfmt % now
    os.mkdir(dirname)
    # Put in CSV file with needed fields
    with open(dirname + "EC.csv", 'w') as csvfile:
        keys = set()
        for rec in data:
            for key in rec.keys():
                keys.add(key)
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    return(dirname)


def main():
    """main operation of script."""
    parser = ArgumentParser(usage='%(prog)s [options] ecommonsMetadata.csv')
    parser.add_argument("-d", "--date", dest="date",
                        help="Date on or after that an ETD was published for \
                        creating DOIs. Put in format YYYY-MM")
    parser.add_argument("datafile", help="eCommons metadata worked from.")

    args = parser.parse_args()

    if not len(sys.argv) > 0:
        parser.print_help()
        parser.exit()

    workingdir = csvparse(args.datafile, args.date)
    print("Working directory created: " + workingdir)


if __name__ == '__main__':
    # eventually add tests?
    main()
