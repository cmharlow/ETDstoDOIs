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
        output = open(newdir + dirid + '.txt', 'a')
        handle = record['dc.identifier.uri']
        # Target URL field
        output.write('_target: ' + handle + '\n')
        # Datacite Schema
        output.write('_profile: datacite \n')
        # Handle
        output.write('datacite.ObjectLocationURL: ' + handle + '\n')

        # Author
        if 'dc.contributor.author[]' in record:
            output.write('datacite.creator: ' + record['dc.contributor.author[]'] + '\n')
        elif 'dc.contributor.author' in record:
            output.write('datacite.creator: ' + record['dc.contributor.author'] + '\n')
        elif 'dc.contributor.author[en_US]' in record:
            output.write('datacite.creator: ' + record['dc.contributor.author[en_US]'] + '\n')

        # Title
        try:
            if 'dc.title[en_US]' in record:
                output.write('datacite.title: ' + record['dc.title[en_US]'].split(':')[0] + '\n')
            elif 'dc.title[en]' in record:
                output.write('datacite.title: ' + record['dc.title[en]'].split(':')[0] + '\n')
            elif 'dc.title[]' in record:
                output.write('datacite.title: ' + record['dc.title[]'].split(':')[0] + '\n')
            elif 'dc.title' in record:
               output.write('datacite.title: ' + record['dc.title'].split(':')[0] + '\n')
            else:
                output.write('datacite.title: None')
                with open(newdir + 'notitlesETDs.txt', 'a') as fother:
                    fother.write(record['id'])
                    fother.write('\n')
        except KeyError:
            pass

        # Publisher
        output.write('datacite.publisher: IUPUI University Library' + '\n')

        # Publication Year
        if 'dc.date.issued' in record:
            output.write('datacite.publicationyear: ' + record['dc.date.issued'][:4] + '\n')
        elif 'dc.date.issued[en_US]' in record:
            output.write('datacite.publicationyear: ' + record['dc.date.issued[en_US]'][:4] + '\n')
        elif 'dc.date.issued[]' in record:
            output.write('datacite.publicationyear: ' + record['dc.date.issued[]'][:4] + '\n')
        else:
            output.write('datacite.publicationyear: None')
            with open(newdir + 'noyearsETDs.txt', 'a') as fyrother:
                fyrother.write(record['id'])
                fyrother.write('\n')

        # Resource Type
        output.write('datacite.resourcetype: Text \n')
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
