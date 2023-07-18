#! /usr/local/bin/python3
import csv
import argparse
import pickle

parser = argparse.ArgumentParser(description='Combine term frequency dictionaries')
parser.add_argument('in_files',nargs='+', help = 'List of input .csv or .pickle files. If .csv then '
        'first row must be column labels and there must be columns named "Term" and "Freq"')
parser.add_argument('out_file', help = 'Output .pickle or .csv file.')
args = vars(parser.parse_args())
for filename in args['in_file']:
    if filename[-4:] != '.csv' and filename[-7:] != '.pickle':
        raise ValueError(f'Input files must be .csv or .pickle files. Filename {filename} is not recognized.')
doc_freq ={}
print(f"Combining {args['in_files']} into {args['out_file']}")

for filename in args['in_files']:
    if filename[-4:] != '.csv':
        with open(filename,'r') as infile:
            in_csv = csv.DictReader(in_file)
            for row in in_csv:
                term = row['Term']
                doc_freq[term] = row['Freq'] + doc_freq.get(term,0)
    else:
        with open(filename,'rb') as infile: 
            doc_freq_file = pickle.load(infile)
            for term in doc_freq_file:
                doc_freq[term] = doc_freq_file[term] + doc_freq.get(term,0)
        
if args['out_file'][-7:] == '.pickle':
    with open(args['out_file'],'wb') as out_file:
        pickle.dump(doc_freq,out_file)
else:
    with open(args['out_file'],'w') as out_file:
        out_csv = csv.writer(out_file)
        out_csv.writerow(['Term','Freq'])
        out_csv.writerows( (term, freq) for term, freq in doc_freq.items())
    
