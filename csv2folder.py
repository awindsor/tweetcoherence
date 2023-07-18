#! /usr/local/bin/python3

# This has worked for all my CSVs. If there are issues we can consider adding a sniffer for
# the CSV dialect. 

import csv
import os
import argparse

def extract_files(filename,out_directory, key_field, text_field, overwrite = False,):
    assert os.path.isdir(out_directory), f'{out_directory} is not a valid destination directory.'
    with open(filename,'r') as input_file:
        input_csv = csv.DictReader(input_file)
        input_fields = input_csv.fieldnames
        assert key_field in input_fields, f'Field {key_field} does not appear in header row of file {filename}.'
        assert text_field in input_fields, f'Field {text_field} does not appear in header row of file {filename}.'
        for row in input_csv:
            out_path = os.path.join(out_directory,row[key_field]+'.txt')
            if not overwrite:
                assert not os.path.exists(out_path), f'Writing {key_field+".txt"} would result in overwriting.'
            with open(out_path,'w') as out_file:
                out_file.write(row[text_field])
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Takes a csv file with a header and names for key and text '
                'columns and produces 1 file per row with name from the key column and contents from the text')
    parser.add_argument('in_file', help = 'Name of input .csv file. '
        'CSV files are expected to have a header row. Empty cells in the header '
        'row are ignored. Cells in columns with empty header cells are recorded as extra fields.')
    parser.add_argument('out_directory', help = 'Output drectory. Must exist.')
    parser.add_argument('key_field', help = 'Column from csv header that uniquely indentifies rows.')
    parser.add_argument('text_field', help = 'Column from csv header that contains text files.')
    parser.add_argument('--overwrite', help = 'By default the program will not overwrite an existing file.', action = 'store_true')
    args = vars(parser.parse_args())
    print(args)
    extract_files(args['in_file'],args['out_directory'], args['key_field'], args['text_field'],args['overwrite'])



