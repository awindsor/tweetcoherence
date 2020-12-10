#! /usr/local/bin/python3

import csv
from contextlib import ExitStack 
import argparse


def combine_csv_files(filenames,outfilename):
    with ExitStack() as stack:
        files = [stack.enter_context(open(filename,'r')) for filename in filenames]
        fields = {}
        combined_fields = []
        for file in files:
            fields[file] = [field for field in csv.DictReader(file).fieldnames if field != '']
            combined_fields += [ field for field in fields[file] if field not in combined_fields ]
        readers = [csv.DictReader(file,fields[file], restkey = 'extra', restval = '') for file in files]
        with open(outfilename,'w') as out_file:
            out_csv = csv.writer(out_file)
            print(combined_fields)
            extra_fields = 0
            out_csv.writerow(combined_fields)
            for reader in readers:
                max_extra = 0
                for row in reader:
                    print(row)
                    write_row = [row.get(field,'') for field in combined_fields]+['']*extra_fields+row.get('extra',[])
                    print(write_row)
                    max_extra = max(max_extra, len(row.get('extra',[])))
                    out_csv.writerow(write_row)
                extra_fields += max_extra
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine CSV files')
    parser.add_argument('in_files',nargs='+', help = 'List of input .csv files. CSV files are expected to have a header row.')
    parser.add_argument('out_file', help = 'Output .csv file.')
    args = vars(parser.parse_args())
    combine_csv_files(args['in_files'],args['out_file'])



