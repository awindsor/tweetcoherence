#! /usr/local/bin/python3
'''
Quick and dirty sorting of large CSV files which cannot be handled in Excel. Currently
the implementation works for files which can be memory resident. I will add an 
xternal mergesort option for larger files. 
'''
import csv
import argparse

parser = argparse.ArgumentParser(description='Sort rows in a csv file using column key')
parser.add_argument('in-file')
parser.add_argument('out-file')
parser.add_argument('key')
parser.add_argument('--no-header', dest="header", action = "store_false")
parser.add_argument('--subfile-size', help = "subdivide large file into files of subfile-size rows for files "
                        "which are too large to be memory resident")



args = vars(parser.parse_args())
with open(args['in-file'],'r') as in_file:
    in_csv = csv.DictReader(in_file)
    fields = in_csv.fieldnames
    in_data = list(in_csv)
key_fun = lambda row : row[args['key']]
in_data.sort(key = key_fun)
with open(args['out-file'],'w') as out_file:
    out_csv = csv.DictWriter(out_file, fields)
    out_csv.writeheader()
    out_csv.writerows(in_data)
