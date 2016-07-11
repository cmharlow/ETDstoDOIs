#! /usr/bin/env python
"""Run in same working directory as files. See README.md for usage examples."""
from argparse import ArgumentParser
import sys
import csv
import subprocess


def mintdoi(data, workingdir, args):
    """Call ezid.py to generate DOIs for handles with metadata as ANVL."""
    for record in data:
        recID = record['id']
        # Run python ezid.py username:password mint doi:shoulder @ ANVLfile.txt
        unpw = args.username + ":" + args.password
        doish = 'doi:' + args.shoulder
        meta = workingdir + recID + '.txt'
        proc = ['python', 'ezid.py', unpw, 'mint', doish, '@', meta]
        EZIDout = subprocess.check_output(proc)
        doiURL = EZIDout.split(' | ')[0].replace('success: doi:',
                                                 'http://dx.doi.org/')
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


def main():
    """main operation of script."""
    parser = ArgumentParser(usage='%(prog)s [options] ecommonsMetadata.csv')
    parser.add_argument("-u", "--username", dest="username",
                        help="EZID creation username")
    parser.add_argument("-p", "--password", dest="password",
                        help="EZID creation password.")
    parser.add_argument("-s", "--shoulder", dest="shoulder",
                        default="10.5072/FK2",
                        help="DOI shoulder to use. Format 10.5072/FK2.")
    parser.add_argument("workingdir", help="Working directory containing ready \
                        ANVL files.")

    args = parser.parse_args()

    if not len(sys.argv) > 0:
        parser.print_help()
        parser.exit()

    with open(args.workingdir + 'EC.csv', 'r') as ECdata:
        reader = csv.DictReader(ECdata)
        data = [x for x in reader]
    mintdoi(data, args.workingdir, args)


if __name__ == '__main__':
    # eventually add tests?
    main()
