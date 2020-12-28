#! /usr/local/bin/python3
import csv
import argparse
import pickle
from collections import Counter , deque
import math
import datetime
import logging
from itertools import islice


logger = logging.getLogger('ComputeTweetCohesion')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('ComputeTweetCohesion.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
logger.addHandler(fh)
logger.addHandler(ch)



def segment(it,length):
    # returns a generator that iterates over it in steps of windows of length length 
    seg = iter(it)
    return iter(lambda :list(islice(seg,length)),[])

def compute_cohesion(count1, count2, corpus):
    def weight(term):
        return math.log(combined[term]+1)/math.log(corpus[term]+1)
    common = set(count1.keys()).intersection(count2.keys())
    combined = count1 + count2
    scores = {term : weight(term) for term in combined}    
    num = sum(scores[term] for term in common)
    denom = sum(scores[term] for term in combined)
    return num/denom

def tweetdatetime(str):
    year = int(str[:4])
    month= int(str[4:6])
    day = int(str[6:8])
    hour = int(str[9:11])
    minute = int(str[11:13])
    second = int(str[13:15])
    return datetime.datetime(year,month,day,hour,minute,second)

def compute_cohesion_file(filename, out_filename, size, tf_filename = None, sliding = False):
    #Sliding is not yet thoroughly tested!
    if tf_filename is None:
        logger.info('Computing Term Frequency for Corpus')
        corpus_freq = Counter()
        with open(filename,'r') as in_file:
            in_csv = csv.DictReader(in_file)
            for i, row in enumerate(in_csv):
                if  i % 10000 == 0:
                    logger.info(f'Processing Tweet {i}')
                corpus_freq.update(row['text'].lower().split())
                """ with open('check_file.csv', 'w') as o:
                    o_csv = csv.writer(o)
                    o_csv.writerows(corpus_freq.items()) """
    elif tf_filename[-4:]=='.csv':
        logger.info(f"Loading Term Frequency for Corpus from {tf_filename}")
        # assume that header is present
        with open(tf_filename,'r') as in_file:
            corpus_freq = Counter()
            in_csv = csv.reader(in_file)
            in_csv.__next__() # consume header
            for i, row in enumerate(in_csv):
                if  i % 10000 == 0:
                    logger.info(f'Processing Term {i}, {row[0]}')
                corpus_freq[row[0]] = int(row[1])

    with open(out_filename,'w') as out_file, \
                open(filename,'r') as in_file:
        in_csv = csv.DictReader(in_file)
        out_csv = csv.writer(out_file)
        out_csv.writerow(['Start Time','End Time','Start Day','Start Month',
                'Duration (s)', 'Cohesion (avg)','Number'] 
                + [f'Cohesion Pair {i+1}' for i in range(size*(size-1)//2)]
                )
        if not sliding:
            logger.info(f'Computing coherence using disjoint windows.')
            for i, block in enumerate(segment(in_csv,size)):
                start_time = tweetdatetime(block[0]['created_at'])
                start_fmt = start_time.strftime('%a %b %d %H:%M:%S %Z %Y')
                end_time = tweetdatetime(block[-1]['created_at'])
                end_fmt = end_time.strftime('%a %b %d %H:%M:%S %Z %Y')
                if  i % 10000 == 0:
                        logger.info(f'Processing Block {i} with with tweets starting at {start_fmt} and ending at {end_fmt}.')
                duration = (end_time - start_time).total_seconds()
                if duration < 0:
                    logger.error(f'Negative duration block detected.')
                    logger.error(block)
                counter_block = list(map(lambda x: Counter(x['text'].lower().split()),block))
                counter_pairs = [(count1, count2) for i, count1 in enumerate(
                        counter_block[:-1]) for count2 in counter_block[i+1:]]
                cohesion = list(map(lambda x : compute_cohesion(x[0],x[1], corpus_freq), 
                        counter_pairs))
                avg_cohesion = sum(cohesion)/len(cohesion)
                day = start_time.day
                month = start_time.month
                out_row = [start_fmt,end_fmt, day, month,duration, avg_cohesion, 
                        len(cohesion)] + cohesion 
                out_csv.writerow(out_row)
        else:
            logger.info(f'Computing coherence using a sliding window.')
            block = deque([tweet for i, tweet in zip(range(size),in_csv)],size)
            start_time = tweetdatetime(block[0]['created_at'])
            start_fmt = start_time.strftime('%a %b %d %H:%M:%S %Z %Y')
            end_time = tweetdatetime(block[-1]['created_at'])
            end_fmt = end_time.strftime('%a %b %d %H:%M:%S %Z %Y')
            day = start_time.day
            month = start_time.month
            duration = (end_time - start_time).total_seconds()
            counter_deque = deque(map(lambda x: Counter(x['text'].lower().split()),block),size)
            cohesion_matrix = deque([
                [compute_cohesion(counter_deque[i],counter_deque[j], corpus_freq) for j in range(i+1,len(block))]
                for i in range(len(block)-1)
                ],len(block)-1)
            cohesion_flat = [ c for row in cohesion_matrix for c in row]     
            avg_cohesion = sum(cohesion_flat)/len(cohesion_flat)
            out_row = [start_fmt,end_fmt, day, month,duration, avg_cohesion, 
                len(cohesion_flat)] + cohesion_flat
            out_csv.writerow(out_row)
            for i, tweet in enumerate(in_csv,start=2):
                # if we get here all blocks are of length size
                block.append(tweet)
                start_time = tweetdatetime(block[0]['created_at'])
                start_fmt = start_time.strftime('%a %b %d %H:%M:%S %Z %Y')
                end_time = tweetdatetime(block[-1]['created_at'])
                end_fmt = end_time.strftime('%a %b %d %H:%M:%S %Z %Y')
                day = start_time.day
                month = start_time.month
                duration = (end_time - start_time).total_seconds()
                if  i % 10000 == 0:
                        logger.info(f'Processing Block {i} with with tweets starting at {start_fmt} and ending at {end_fmt}.')
                counter_deque.append(Counter(tweet['text'].lower().split()))
                cohesion_matrix.append([])
                for j in range(size-1):
                    cohesion_matrix[j].append(compute_cohesion(counter_deque[j],counter_deque[size-1], corpus_freq))
                # both of the following could be computed more efficienly from
                # previous values. Is the additional complexity worth it?
                cohesion_flat = [ c for row in cohesion_matrix for c in row]     
                avg_cohesion = sum(cohesion_flat)/len(cohesion_flat)
                out_row = [start_fmt,end_fmt, day, month,duration, avg_cohesion, 
                    len(cohesion_flat)] + cohesion_flat
                out_csv.writerow(out_row)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute average similarity amongst pairs in a window of texts. ')
    parser.add_argument('in_file',  )
    parser.add_argument('out_file')
    parser.add_argument('size',type=int)
    parser.add_argument('--sliding', action='store_true')
    parser.add_argument('--corpus_tf_file')

    args = vars(parser.parse_args())
    logger.debug(f'ComputeTweetCohesion called as script with arguments {args}')
    compute_cohesion_file(args['in_file'],args['out_file'],args['size'],args['corpus_tf_file'],args['sliding'])