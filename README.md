# tweetcoherence
Tools to measure coherence in a stream of tweets. 
 
Processing is conducted serially with very low memory footprint.

If you use the default and keep only the English tweets then you should be aware that langdetect is quite slow and somewhat idiosyncratic on small snippets of text. To speed this up I suggest splitting the document into multiple smaller files and  running these in parallel. The split_csv.py script is provided to do this. By  default it takes a hug csv and splits it into multiple 100,000 row csvs. 

    ./split_csv.py infile outfile_basename

Our process for this is to split the file, process and clean, and compute term 
frequencies for each sub-corpus. 

    for file in outfile_basename_*; do processTTV2 $file ${file:0:-4}_clean.csv; done
    for file in outfile_basename_*_clean.csv; do ComputeTF $file ${file:0:-9}_tf.cs

Then we combine all term frequency files to get one universal term frequency file.

    ./CombineTF outfile_basename_* _tf.csv outfile_basename_tf.csv 

Cohesion values can then be computed for each sub-corpus by using the combined 
corpus term frequency document. 

    for file in outfile_basename_*_clean.csv; do ProcessTTV2.py $file ${file:0:-9}_coherence.csv --corpus_tf_file outfile_basename_tf.csv; done

If using disjoint windows then the same split can be used. If using sliding windows  then then the clean tweet files should be combined and resplit using the sliding window option. This ensures that no windows are missed.  

If using the disjoint windows option then it is best if the sub-corpora are chosen 
to be multiples of the window length. If using sliding windows then, in order to avoid missing blocks, sub-corpora should overlap by overlap by window length -1 tweets but overall length is not important.

Care should be taken not to compute term frequencies from overlapping sub-corpora. 

We provide a simple (but slow) countCsvRows to count the number of rows in a CSV  file. This is much slower than wc -l but handles csvs where rows contain text cells that contain embedded newlines. We also provide a file to combine CSVs. This can be done using the command line but the python utility allows different fields to be present in the different CSVs and handles 'extra' unlabel fields gracefully (unlableled fields from different files are assumed distinct by default).

