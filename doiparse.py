#! /usr/bin/env python
"""Run in same working directory as files. See README.md for usage examples."""
from argparse import ArgumentParser
import sys
import csv
from csvparse import csvparse


def doiparse(newdir):
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
            fh.write('datacite.publisher: Cornell University Library' + '\n')
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
    parser.add_argument("datafile", help="eCommons metadata worked from.")

    args = parser.parse_args()

    if not len(sys.argv) > 0:
        parser.print_help()
        parser.exit()

    workingdir = csvparse(args.datafile, args.date)
    doiparse(workingdir)
    print('ANVL files available in: ' + workingdir)

if __name__ == '__main__':
    # eventually add tests?
    main()
