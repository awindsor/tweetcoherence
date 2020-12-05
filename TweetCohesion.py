# Two Stage IDF Weighting Code

# Basic. Split on white space. No stemming. 

import langdetect
import os
import shutil
import re
import csv
import tempfile
import logging
langdetect.DetectorFactory.seed = 0

# Since our vectors are sparse we represent them as dictionaries
# either word : weight or word: freq
'''
public static String clean(String tweetTxt) {
		String[] w = tweetTxt.trim().split(" ");
		StringBuffer sb = new StringBuffer();
		for (String word : w) {
			if (word.startsWith("@") && word.endsWith(":")) {
				continue;
			}
			if (word.startsWith("http://")) {
				continue;
			}
			if (tweetTxt.trim().startsWith("RT") && word.equalsIgnoreCase("RT")) {
				continue;
			}
			word = word.replaceAll("[^A-Za-z']", "");
			sb.append(word + " ");
		}
		return sb.toString().trim();
'''
def get_last_n_lines(file_name, N):
    list_of_lines = []
    with open(file_name, 'rb') as read_obj:
        read_obj.seek(0, os.SEEK_END)
        buffer = bytearray()
        pointer_location = read_obj.tell()
        while pointer_location >= 0:
            read_obj.seek(pointer_location)
            pointer_location = pointer_location -1
            new_byte = read_obj.read(1)
            if new_byte == b'\n':
                if len(list_of_lines) >0 or len(buffer) > 0: list_of_lines.append(buffer.decode()[::-1])
                if len(list_of_lines) == N:
                    return [line.rstrip() for line in reversed(list_of_lines)]
                buffer = bytearray()
            else:
                # If last read character is not eol then add it in buffer
                buffer.extend(new_byte)
 
        # As file is read completely, if there is still data in buffer, then its first line.
        if len(buffer) > 0:
            list_of_lines.append(buffer.decode()[::-1])


def urlQ(word):
    # matches the original but missed https
    return word.startswith("http://")

def mentionQ(word):
    # matches the original
    return word.startswith('@') and word.endswith(':')

exclude = [mentionQ , urlQ]

def clean_tweet(tweet):
    words = tweet.split(' ')
    for filter in exclude:
        words = [word for word in words if not filter(word)]
    words = [re.sub(r"[^A-Za-z']", "", word) for word in words]
    words = [word for word in words if word != '']
    return words

def computeDF(corpus):
    # corpus should be an iterable returning strings
    # returns term document frequencies in dictionary 
    df = {}
    for tweet in corpus:
        for word in set(clean_tweet(tweet)):
            df[word] = df.get(word,0)+1
    return df

def computeTFIDF(corpus, df = None, ifun = None ):
    if df is None:
        ifun = lambda word: 1
    elif ifun is None: 
        ifun = lambda word : df[word] 


def readTTV2(filename,out_filename, filter = None, resume = True, keep_retweets = True):
    def _process_tweet(tweet,filter):
        id = tweet[0]
        created = tweet[1]
        text = tweet[2]
        retweet = tweet[8].strip()
        if retweet == "":
            text = " ".join(clean_tweet(text)).strip()
            if text != "" and filter(text):
                out_row = [id,created,text] if not old_version else [created,text]
                tweet_file.writerow(out_row)
    if filter is None:
        filter = lambda text : True
    with open(filename,'r') as infile:
        ttv = csv.reader((line.replace('\0','') for line in infile), delimiter = '\t')
        if resume:
            file_mode = 'a'
            final_tweet_rows = get_last_n_lines(out_filename,5)
            final_tweet_rows = [row for row in final_tweet_rows if row != '']
            final_tweet_csv = csv.reader([final_tweet_rows[-1]])
            final_tweet = final_tweet_csv.__next__()
            if len(final_tweet) == 2:
                # Old version no tweet id. Fall back on timestamp. 
                old_version = True
                last_date ,_ = final_tweet
                with tempfile.NamedTemporaryFile(mode='w',delete=False) as temp_outfile, \
                    open(out_filename,'r') as temp_infile:
                    temp_outfile_pathname = temp_outfile.name
                    temp_outcsv = csv.writer(temp_outfile.file)
                    temp_incsv = csv.reader(temp_infile)
                    for row in temp_incsv:
                        date,tweet = row
                        if date < last_date:
                            temp_outcsv.writerow(row)
                        else:
                            break
                os.rename(out_filename,out_filename+'.old')
                print(temp_outfile_pathname)
                shutil.move(temp_outfile_pathname,out_filename)
                while True:
                    tweet = ttv.__next__()
                    if tweet[1] == last_date:
                        break
            else:
                # New version. 
                old_version = False
                last_tweet_id, last_date ,_ = final_tweet
                while True:
                    tweet = ttv.__next__()
                    if tweet[1] == last_date and tweet[0] == last_tweet_id:
                        tweet = ttv.__next__()
                        break
        else:
            old_version = False
            file_mode = 'w'
            tweet = tweet = ttv.__next__()
        
        with open(out_filename,file_mode) as outfile:
            tweet_file = csv.writer(outfile)
            _process_tweet(tweet,filter)
            if not resume: 
                tweet_file.writerow(['Tweet ID','Created','Text'])
            for num, tweet in enumerate(ttv,start=1):
                if num % 1000 == 0:
                    print(f'Date {tweet[1]}') 
                if num % 5000 == 0:
                    outfile.flush()
                _process_tweet(tweet,filter)
            

os.chdir('/Users/awindsor/OneDrive - The University of Memphis/Documents/Research/Leah/')

def englishQ(twt):
    try:
        return langdetect.detect(twt) == 'en'
    except langdetect.lang_detect_exception.LangDetectException as exc:
        print(f'LangDetectException processing {twt}')
        print(exc)
        print('Skipping tweet')
        return False
readTTV2('/Users/awindsor/Downloads/syria2012-03-03to2012-06-15.ttv2','syria_en_tweet.csv',englishQ)
    
#def computeSimilaritySlidingWindow(corpus,window_length):
    

            




