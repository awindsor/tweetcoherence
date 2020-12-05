#!  /usr/local/bin/python3
import csv
import logging
import langdetect
import re

logger = logging.getLogger('ProcessTTV2')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('ProcessTTV2.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
logger.addHandler(fh)
logger.addHandler(ch)


ttv2fields = [
    'tweet_id',
    'created_at',
    'text',
    'lon,lat',
    'place_id',
    'place_str',
    'in_reply_to_status_id',
    'in_reply_to_screen_name',
    'retweet_id',
    'retweet_count',
    'user.screen_name',
    'user.id',
    'user.created_at',
    'user.name',
    'user.description',
    'user.location',
    'user.url',
    'user.statuses_count',
    'user.followers_count',
    'user.friends_count',
    'user.favourites_count',
    'user.geo_enabled',
    'user.default_profile',
    'user.time_zone',
    'user.lang',
    'user.utc_offset']

def urlQ(word):
    # matches the original but missed https
    return word.startswith("http://")

def mentionQ(word):
    # matches the original
    return word.startswith('@') and word.endswith(':')

exclude = [mentionQ , urlQ]

def clean_tweet(text):
    words = text.strip().split(' ')
    for filter in exclude:
        words = [word for word in words if not filter(word)]
    if text.strip().lower().startswith('rt'):
        words = [word for word in words if word.lower()!='rt']
    words = [re.sub(r"[^A-Za-z']", "", word) for word in words]
    words = [word for word in words if word != '']
    return ' '.join(words)

def englishQ(twt):
    try:
        return langdetect.detect(twt) == 'en'
    except langdetect.lang_detect_exception.LangDetectException as exc:
        logger.debug(f'LangDetectException processing {twt}')
        logger.debug(exc)
        return False


def readTTV2(filename,out_filename, fields = None, keep_retweets = True, english_only = True, clean = True):

    if not fields: # catch empty list and None
        fields = ttv2fields
    # if filter_fun is None:
    #     filter_fun = lambda text : True 
    logger.debug(fields)
    if not set(ttv2fields).issuperset(fields):
        raise ValueError(f'The fields parameter must be a list of elements from {ttv2fields}.')
    if filename[-4:] != '.ttv' and filename[-5:]!= '.ttv2' and filename[-4:] != '.csv':
        raise ValueError('The input filename must end in .csv, .ttv, or .ttv2')
    if out_filename[-4:] != '.csv':
        raise ValueError('The output filename must end in .csv')
    with open(filename,'r') as infile, \
            open(out_filename,'w') as outfile:
        if filename[-4:] == '.ttv' or filename[-5:] == '.ttv2':
            logger.debug('Loading {filename} using tab delimited')
            ttv = csv.DictReader((line.replace('\0','') for line in infile), 
                    fieldnames = ttv2fields, restval = '', delimiter = '\t')
        else:
            logger.debug(f'Loading {filename} using comma delimited')
            ttv = csv.DictReader((line.replace('\0','') for line in infile), 
                    fieldnames = ttv2fields, restval = '')
        if not keep_retweets:
            logger.debug('Adding retweet stripper to pipeline')
            ttv = ( tweet for tweet in ttv if tweet['retweet_id'].strip() != '' )
        if english_only:
            logger.debug('Adding English language detection to pipeline')
            ttv = ( tweet for tweet in ttv if englishQ(tweet['text']) )
        tweet_file = csv.DictWriter(outfile,fieldnames = fields,extrasaction='ignore')
        tweet_file.writeheader()
        for num, tweet in enumerate(ttv,start=1):
            date_stamp = tweet['created_at']
            month = month = date_stamp[4:6]
            day = date_stamp[6:8]
            if month == '03' and day < '30':
                continue
            if clean:
                tweet['text']= clean_tweet(tweet['text'])
            if tweet['text'].strip() == '':
                continue
            tweet_file.writerow(tweet)
            if num % 1000 == 0:
                logger.info(f"Processing tweet number {num} with tweet_id {tweet['tweet_id']} created on {tweet['created_at']}") 
            # if num % 5000 == 0:
            #     outfile.flush()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract ttv2 file to csv cleaning up null characters.')
    parser.add_argument('in_file', help = 'Input .ttv2 file')
    parser.add_argument('out_file', help = 'Output .csv file')
    parser.add_argument('--no-rt', help = 'Skip retweets. Default is to keep retweets.',
        dest='keep_retweets',action = 'store_false')    
    parser.add_argument('--foreign', help = 'Allow Non-English tweets. Default is to remove.',
        dest='english_only', action = 'store_false')    
    parser.add_argument('--no-clean', help='Do not clean text. Default is to clean text',
        dest='clean_text', action='store_false')
    parser.add_argument('--v', help = 'Give verbose output to the console',
        dest='verbose',action = 'store_true')
    parser.add_argument('--fields', nargs = '*', help = 'List of fields to keep')

    args = vars(parser.parse_args())
    logger.debug(f'ProcessTTV2 called as script with arguments {args}')
    if args['verbose']:
        logger.handlers[1].setLevel(logging.INFO)

    readTTV2(args['in_file'],args['out_file'], keep_retweets=args['keep_retweets'], 
            fields = args['fields'], english_only = args['english_only'], clean = args['clean_text'])
            



            




  
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
    
