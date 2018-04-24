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
original_unneeded = [
    'dc.contributor.chair', 'dc.contributor.chair[]',
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
additional_unneeded = [
    'collection',
    'atmire.cua.enabled[]',
    'dc.contributor.advisor',
    'dc.contributor.advisor[]',
    'dc.contributor.advisor[en _US]',
    'dc.contributor.advisor[en-US]',
    'dc.contributor.advisor[en]',
    'dc.contributor.advisor[en_UD]',
    'dc.contributor.advisor[en_US]',
    'dc.date[]',
    'dc.date[en]',
    'dc.date[en_US]',
    'dc.degree.date[]',
    'dc.degree.date[en-US]',
    'dc.degree.date[en]',
    'dc.degree.date[en_US]',
    'dc.degree.discipline',
    'dc.degree.discipline[]',
    'dc.degree.discipline[en-US]',
    'dc.degree.discipline[en]',
    'dc.degree.discipline[en_US]',
    'dc.degree.grantor[]',
    'dc.degree.grantor[en-US]',
    'dc.degree.grantor[en]',
    'dc.degree.grantor[en_US]',
    'dc.degree.level[]',
    'dc.degree.level[en]',
    'dc.degree.level[en_US]',
    'dc.description.abstract[en-US]',
    'dc.description.abstract[es]',
    'dc.description.uri[]',
    'dc.description.version[en_US]',
    'dc.description[]',
    'dc.embargo.lift',
    'dc.embargo.lift[]',
    'dc.embargo[]',
    'dc.embargo[en]',
    'dc.embargo[en_US]',
    'dc.format.extent[]',
    'dc.format.mimetype[]',
    'dc.identifier',
    'dc.identifier.issn[]',
    'dc.identifier.other',
    'dc.identifier.other[]',
    'dc.identifier[]',
    'dc.language.iso[en-US]',
    'dc.language[]',
    'dc.relation.haspart[en_us]',
    'dc.relation.ispartofseries[]',
    'dc.rights.uri[*]',
    'dc.rights.uri[]',
    'dc.rights[*]',
    'dc.rights[]',
    'dc.subject.lcsh',
    'dc.subject.lcsh[]',
    'dc.subject.lcsh[en]',
    'dc.subject.lcsh[en_US]',
    'dc.subject.mesh[]',
    'dc.subject.mesh[en -- US]',
    'dc.subject.mesh[en-US]',
    'dc.subject.mesh[en]',
    'dc.subject.mesh[en_US]',
    'dc.subject[en-US]',
    'dc.subject[es]',
    'dc.type',
    'dc.type[en-US]',
    'dcterms.subject[]',
    'thesis.degree.discipline[en]',
    'thesis.degree.grantor[en]']
unneeded = original_unneeded + additional_unneeded

def testDate(ECdata, dateAfter):
    """Remove from ECdata all records not after date given."""
    givendate = datetime(int(dateAfter[:4]), int(dateAfter[5:7]), 1)
    recdate = ''
    newdata = []
    for record in ECdata:
        # Grab dates from variety of places EC stores.
        if 'dc.date.issued' in record:
            if year_re.match(record['dc.date.issued']):
                recdate = record['dc.date.issued']
        elif 'dc.date.issued[]' in record:
            if year_re.match(record['dc.date.issued[]']):
                recdate = record['dc.date.issued[]']
        elif 'dc.date.issued[en_US]' in record:
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
