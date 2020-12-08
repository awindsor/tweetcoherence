# tweetcoherence
Tools to measure coherence in a stream of tweets. 
 
Processing is conducted serially with very low memory footprint.

If you use the default and keep only the English tweets then you should be aware that langdetect is quite slow and somewhat idiosyncratic on small snippets of text. To speed this up I suggest splitting the document into multiple smaller files and running these in parallel. The split_csv.py script is provided to do this. By default it takes a hug csv and splits it into multiple 100,000 row csvs. 

./split_csv.py 

Our process for this is to split the file, process and clean, and compute term frequencies for each sub-corpus. 



Then we combine all term frequency files to get one universal term frequency file.

Cohesion values can then be computed for each sub-corpus by using the combined corpus term frequency document. 

If using disjoint windows then the same split can be used. If using sliding windows then then the corpora need to be combined and resplit using the sliding
window option.  

If using the disjoint windows option then it is best if the sub-corpora are chosen to be multiples of the window length. 

If using sliding windows then, in order to avoid missing blocks, sub-corpora should overlap by overlap by window length -1 tweets.

Care should be taken not to compute term frequencies from overlapping sub-corpora. 
