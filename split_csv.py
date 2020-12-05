#!  /usr/local/bin/python3
import csv
import math
from contextlib import ExitStack
from collections import deque

""" logger = logging.getLogger('CleanTweetCSV')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('CleanTweetCSV.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
logger.addHandler(fh)
logger.addHandler(ch) """


def split_csv (filename,out_filename,file_rows = 100000,window_length=1,padding_width = None):
    if filename[-4:] != '.csv':
        raise ValueError('The input filename must end in .csv')
    
    num_rows = 0

    if padding_width is None:
        with open(filename, 'r') as in_file:
            in_csv = csv.DictReader(in_file)
            for row in in_csv:
                num_rows += 1
        padding_width = len(str(num_files))
        
    num_files = math.ceil(float(num_rows)/file_rows)
    
    with open(filename, 'r') as in_file,\
            ExitStack() as stack:
        file_num = 1
        in_csv = csv.DictReader(in_file)
        fields = in_csv.fieldnames
        window = deque([], window_length-1)
        for num, row in enumerate(in_csv):
            if num%file_rows == 0:
                stack.close()
                out_file = stack.enter_context(
                        open(f'{out_filename}_{file_num:0{padding_width}}.csv','w'))
                file_num += 1
                out_csv = csv.DictWriter(out_file,fieldnames=fields)
                out_csv.writeheader()
                out_csv.writerows(window)
            out_csv.writerow(row)
            window.append(row)
                        
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Split .csv file into multiple smaller csv files.')
    parser.add_argument('in_file', help = 'Input .csv file')
    parser.add_argument('out_file', help = 'The basename for output .csv file. You do not need to add .csv. '
            'Filenames will be  basename + _ + number + .csv.')
    parser.add_argument('file_rows', help = 'Number of rows before splitting. '
            'If disjoint windows are to be used to process this should be a multiple of the window width. '
            'Default is 100,000 rows.', type = int, default = 100000)    
    parser.add_argument('--window', help = 'Length of window for sliding window. '
            'Default is 1, which means no sliding window.',  type=int,default = 1)
    parser.add_argument('--padding-width', help = 'Width to pad the number to when .',  type=int,default = None)
    args = vars(parser.parse_args())

    split_csv(args['in_file'],args['out_file'], args['file_rows'], args['window'],args['padding-width'])
            



            




  
#  if resume:
#             file_mode = 'a'
#             final_tweet_rows = get_last_n_lines(out_filename,5)
#             final_tweet_rows = [row for row in final_tweet_rows if row != '']
#             final_tweet_csv = csv.reader([final_tweet_rows[-1]])
#             final_tweet = final_tweet_csv.__next__()
#             if len(final_tweet) == 2:
#                 # Old version no tweet id. Fall back on timestamp. 
#                 old_version = True
#                 last_date ,_ = final_tweet
#                 with tempfile.NamedTemporaryFile(mode='w',delete=False) as temp_outfile, \
#                     open(out_filename,'r') as temp_infile:
#                     temp_outfile_pathname = temp_outfile.name
#                     temp_outcsv = csv.writer(temp_outfile.file)
#                     temp_incsv = csv.reader(temp_infile)
#                     for row in temp_incsv:
#                         date,tweet = row
#                         if date < last_date:
#                             temp_outcsv.writerow(row)
#                         else:
#                             break
#                 os.rename(out_filename,out_filename+'.old')
#                 print(temp_outfile_pathname)
#                 shutil.move(temp_outfile_pathname,out_filename)
#                 while True:
#                     tweet = ttv.__next__()
#                     if tweet[1] == last_date:
#                         break
#             else:
#                 # New version. 
#                 old_version = False
#                 last_tweet_id, last_date ,_ = final_tweet
#                 while True:
#                     tweet = ttv.__next__()
#                     if tweet[1] == last_date and tweet[0] == last_tweet_id:
#                         tweet = ttv.__next__()
#                         break
#         else:
#             old_version = False
#             file_mode = 'w'
#             tweet = tweet = ttv.__next__() 
            
#     def _process_tweet(tweet,keep_retweets, filter_fun):
        
#         retweet = tweet[8].strip()
#         if retweet == "" or keep_retweets:
#             text = " ".join(clean_tweet(text)).strip()
#             if text != "" and filter_fun(text):
#                 out_row = [id,created,text] if not old_version else [created,text]
#                 tweet_file.writerow(out_row)            
            
# def englishQ(twt):
#     try:
#         return langdetect.detect(twt) == 'en'
#     except langdetect.lang_detect_exception.LangDetectException as exc:
#         print(f'LangDetectException processing {twt}')
#         print(exc)
#         print('Skipping tweet')
#         return False
    
# def computeSimilaritySlidingWindow(corpus,window_length):
    
