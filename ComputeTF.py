#! /usr/local/bin/python3
import csv
import argparse
import pickle
from collections import Counter

parser = argparse.ArgumentParser(description='Compute term frequency dictionary '
        'across whole corpus. No cleaning is done. Text is split on whitespace and everythings is lowercased.')
parser.add_argument('in_file', help = 'Input .csv file. First row must be column labels. Should have a column labeled "text".')
parser.add_argument('out_file', help = 'Output .pickle or .csv file. In the csv file the header row is "term" and "freq".')
parser.add_argument('--doc', help = 'Compute number of rows that that the term '
        'appears in rather than overall frequency of the term.', 
        action = 'store_true')
args = vars(parser.parse_args())

if args['in_file'][-4:] != '.csv':
    raise ValueError('Input file must be a .csv file')
if args['out_file'][-7:] != '.pickle' and args['out_file'][-4:] != '.csv':
    raise ValueError('Output file must be either a .pickle or .csv file')

doc_freq = Counter()

with open(args['in_file'],'r') as in_file:
    in_csv = csv.DictReader(in_file)
    if args['doc']:     
        doc_stream = (set(row['text'].lower().split()) for row in in_csv)
    else:
        doc_stream = (row['text'].lower().split() for row in in_csv)
    for doc in doc_stream:
        doc_freq.update(doc)

if args['out_file'][-7:] == '.pickle':
    with open(args['out_file'],'wb') as out_file:
        pickle.dump(doc_freq,out_file)
else:
    with open(args['out_file'],'w') as out_file:
        out_csv = csv.writer(out_file)
        out_csv.writerow(['term','freq'])
        out_csv.writerows( (term, freq) for term, freq in doc_freq.items())

