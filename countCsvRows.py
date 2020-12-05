#! /usr/local/bin/python3
import csv
import argparse
import pickle

parser = argparse.ArgumentParser(description='count rows in csv file')
parser.add_argument('in_file')

args = vars(parser.parse_args())
with open(args['in_file'],'r') as in_file:
    in_csv = csv.reader(in_file)
    for num, row in enumerate(in_csv,start=1):
        pass
    print(num)