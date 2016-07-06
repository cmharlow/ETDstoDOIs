#! /usr/bin/env python

# Run in same working directory as files. See README.md for usage examples.
from argparse import ArgumentParser
import sys
import csv
import re
import time
import os
import subprocess
import pprint

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


def mintDOIs(data, workingdir, args):
    """Call ezid.py to generate DOIs for handles with metadata as ANVL."""
    for record in data:
        recID = record['id']
        # Run python ezid.py username:password mint doi:shoulder @ ANVLfile.txt
        unpw = args.username + ":" + args.password
        doish = 'doi:' + args.shoulder
        meta = workingdir + recID + '.txt'
        proc = ['python', 'ezid.py', unpw, 'mint', doish, '@', meta]
        EZIDout = subprocess.check_output(proc)
        doiURL = EZIDout.split(' | ')[0].replace('success: doi:', 'http://dx.doi.org/')
        print(recID, doiURL)
        with open(meta, 'a') as fh:
            fh.write(doiURL)
        record['dc.identifier.doi'] = doiURL
    print('finished minting DOIs.')
    with open(workingdir + "EC.csv", 'w') as csvfile:
        keys = set()
        for rec in data:
            for key in rec.keys():
                keys.add(key)
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print('finished creating eCommons update CSV in ' + workingdir)


def csvParse(datafile, dateAfter):
    """Take eCommons CSV, rewrite for our needs (workflow step 2)."""
    with open(datafile, 'r') as ECfile:
        ECreader = csv.DictReader(ECfile)
        ECdata = [x for x in ECreader]
        print("Records in the collection: " + str(len(ECdata)))
    # delete fields we don't need
    ECdataSlim = slimECdata(ECdata)
    # delete records for items issued after date provided
    ECdataDate = testDate(ECdataSlim, dateAfter)
    data = checkDOI(ECdataDate)
    print("Records to be updated with DOIs: " + str(len(data)))
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


def doiParse(newdir):
    """take each eCommons record and generate ANVL txt files."""
    with open(newdir + 'EC.csv', 'r') as ECdata:
        reader = csv.DictReader(ECdata)
        data = [x for x in reader]
    print("creating ANVL files in " + newdir)
    for record in data:
        dirid = record['id']
        with open(newdir + dirid + '.txt', 'a') as fh:
            # Note field
            fh.write('# ' + '\n')
            # Handle
            fh.write('datacite.ObjectLocationURL: ' + 'http://hdl.handle.net/' + record['id'] + '\n')
            # Author
            if record['dc.contributor.author[]']:
                fh.write('datacite.creator: ' + record['dc.contributor.author[]'] + '\n')
            elif record['dc.contributor.author']:
                fh.write('datacite.creator: ' + record['dc.contributor.author'] + '\n')
            elif record['dc.contributor.author[en_US]']:
                fh.write('datacite.creator: ' + record['dc.contributor.author[en_US]'] + '\n')
            else:
                fh.write('datacite.creator: None')
                with open(newdir + 'noauthsETDs.txt', 'a') as fh:
                    fh.write(record['id'])
                    fh.write('\n')
            # Title
            if record['dc.title[en_US]']:
                fh.write('datacite.title: ' + record['dc.title[en_US]'] + '\n')
            elif record['dc.title[en]']:
                fh.write('datacite.title: ' + record['dc.title[en]'] + '\n')
            elif record['dc.title[]']:
                fh.write('datacite.title: ' + record['dc.title[]'] + '\n')
            elif record['dc.title']:
                fh.write('datacite.title: ' + record['dc.title'] + '\n')
            else:
                fh.write('datacite.title: None')
                with open(newdir + 'notitlesETDs.txt', 'a') as fh:
                    fh.write(record['id'])
                    fh.write('\n')
            # Publisher
            fh.write('datacite.publisher: Cornell University Library'+ '\n')
            # Publication Year
            if record['dc.date.issued[en_US]']:
                fh.write('datacite.publicationyear: ' + record['dc.date.issued[en_US]'][:4] + '\n')
            elif record['dc.date.issued[]']:
                fh.write('datacite.publicationyear: ' + record['dc.date.issued[]'][:4] + '\n')
            elif record['dc.date.issued']:
                fh.write('datacite.publicationyear: ' + record['dc.date.issued'][:4] + '\n')
            else:
                fh.write('datacite.publicationyear: None')
                with open(newdir + 'noyearsETDs.txt', 'a') as fh:
                    fh.write(record['id'])
                    fh.write('\n')
            # Resource Type
            fh.write('datacite.resourcetype: Text \n')
    print('ANVL txt files created.')
    return(data)


def main():
    """main operation of script."""
    parser = ArgumentParser(usage='%(prog)s [options] ecommonsMetadata.csv')
    parser.add_argument("-d", "--date", dest="date",
                        help="Date on or after that an ETD was published for \
                        creating DOIs. Put in format YYYY-MM")
    parser.add_argument("-u", "--username", dest="username",
                        help="EZID creation username")
    parser.add_argument("-p", "--password", dest="password",
                        help="EZID creation password.")
    parser.add_argument("-s", "--shoulder", dest="shoulder", default="10.5072/FK2",
                        help="DOI shoulder to use. Format 10.5072/FK2.")
    parser.add_argument("datafile", help="eCommons metadata worked from.")

    args = parser.parse_args()

    if not len(sys.argv) > 0:
        parser.print_help()
        parser.exit()

    workingdir = csvParse(args.datafile, args.date)
    output = doiParse(workingdir)
    mintDOIs(output, workingdir, args)


if __name__ == '__main__':
    # eventually add tests?
    main()
