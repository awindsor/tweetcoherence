#! /usr/local/bin/python3

# This has worked for all my CSVs. If there are issues we can consider adding a sniffer for
# the CSV dialect. 

import csv
from contextlib import ExitStack 
import argparse

def combine_csv_files(filenames,outfilename, ignore = False, combine = False):
    with ExitStack() as stack:
        files = [stack.enter_context(open(filename,'r')) for filename in filenames]
        fields = {}
        combined_fields = []
        for file in files:
            fields[file] = [field for field in csv.DictReader(file).fieldnames if field != '']
            combined_fields += [ field for field in fields[file] if field not in combined_fields ]
        if ignore:
            readers = [csv.DictReader(file,fields[file]) for file in files]
        else:
            readers = [csv.DictReader(file,fields[file], restkey = 'extra', restval = '') for file in files]
        with open(outfilename,'w') as out_file:
            out_csv = csv.writer(out_file)
            extra_fields = 0
            out_csv.writerow(combined_fields)
            for reader in readers:
                max_extra = 0
                padding = [] if combine else ['']*extra_fields 
                for row in reader:
                    write_row = [row.get(field,'') for field in combined_fields]+padding+row.get('extra',[])
                    max_extra = max(max_extra, len(row.get('extra',[])))
                    out_csv.writerow(write_row)
                extra_fields += max_extra
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine CSV files')
    parser.add_argument('in_files',nargs='+', help = 'List of input .csv files. '
        'CSV files are expected to have a header row. Empty cells in the header '
        'row are ignored. Cells in columns with empty header cells are recorded as extra fields.')
    parser.add_argument('out_file', help = 'Output .csv file.')
    parser.add_argument('--combine', help = 'Do not separate extra fields from different files. '
        'Extra fields will begin in the column after named fields.', action = 'store_true')
    parser.add_argument('--ignore', help = 'Ignore extra fields.', action='store_true')
    args = vars(parser.parse_args())
    combine_csv_files(args['in_files'],args['out_file'], args['ignore'],args['combine'])



