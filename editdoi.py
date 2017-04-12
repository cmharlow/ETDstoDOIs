#! /usr/bin/env python
"""Run in same working directory as files. See README.md for usage examples."""
from argparse import ArgumentParser
import sys
import csv
import subprocess
import csvparse
import doiparse


def editdoi(data, workingdir, args):
    """Call ezid.py to edit DOIs for handles with metadata as ANVL."""
    for record in data:
        recID = record['id']
        handle = record['dc.identifier.uri']
        try:
            existing_doiURL = record['dc.identifier.doi']
            print(existing_doiURL)
        except IndexError as e:
            print("Record %s doesn't have DOI currently to edit." % str(recID))
            pass
        unpw = args.username + ":" + args.password
        doish = 'doi:' + existing_doiURL.replace('http://doi.org/', '')
        meta = workingdir + recID + '.txt'
        # Run python ezid.py username:password update doi:doi-id _target http://newhandle-targetURL.com
        target_update_proc = ['python', 'ezid.py', unpw, 'update', doish, ' _target ', handle]
        try:
            subprocess.check_output(target_update_proc)
        except:
            print('Error with EZID script (ezid.py). Check messages above.')
            exit()
        # Run python ezid.py username:password update doi:doi-id datacite @ANVLfile.txt
        meta_update_proc = ['python', 'ezid.py', unpw, 'update', doish, ' datacite @', meta]
        try:
            subprocess.check_output(meta_update_proc)
        except:
            print('Error with EZID script (ezid.py). Check messages above.')
            exit()
        print("Finished updating " + existing_doiURL)
    print('finished updating DOIs.')
    with open(workingdir + "EC_updateReview.csv", 'w') as csvfile:
        keys = set()
        for rec in data:
            for key in rec.keys():
                keys.add(key)
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


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
    parser.add_argument("datafile", help="eCommons metadata worked from.")

    args = parser.parse_args()

    if not len(sys.argv) > 0:
        parser.print_help()
        parser.exit()

    skipDOItest = True
    workingdir = csvparse.csvparse(args.datafile, args.date, skipDOItest)
    output = doiparse.doiparse(workingdir)
    editdoi(output, workingdir, args)


if __name__ == '__main__':
    # eventually add tests?
    main()
