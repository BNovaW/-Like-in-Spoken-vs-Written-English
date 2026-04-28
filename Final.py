'''
Final project for LING 493 Corpus linguistics
Author: Brooke Watson
Description:
Analysis of the usage of the word "like" in english in spoken vs written language. 
'''

import re
import operator
import glob
import math
import os
import random
from collections import Counter

#==========COLLOCATION==========

def tokenize(input_string): #input_string = text string
	tokenized = [] #empty list that will be returned

	#these are the punctuation marks in the Brown corpus + '"'
	punct_list = ['-',',','.',"'",'&','`','?','!',';','(',')','$','/','%','*','+','[',']','{','}','"', "”"]

	#this is a sample (but potentially incomplete) list of items to replace with spaces
	replace_list = ["\n","\t"]

	#This is a sample (but potentially incomplete) list of items to ignore
	ignore_list = [""]

	#iterate through the punctuation list and delete each item
	for x in punct_list:
		input_string = input_string.replace(x, "") #instead of adding a space before punctuation marks, we will delete them (by replacing with nothing)

	#iterate through the replace list and replace it with a space
	for x in replace_list:
		input_string = input_string.replace(x," ")

	#our examples will be in English, so for now we will lower them
	#this is, of course optional
	input_string = input_string.lower()
	#then we split the string into a list
	input_list = input_string[19:].split(" ")

	for x in input_list:
		try:
			float(x)
			continue
		except ValueError:
			pass
		
		if x not in ignore_list: #if item is not in the ignore list
			tokenized.append(x) #add it to the list "tokenized"
	
	return(tokenized)

#fxn to update frequency 
def freq_update(tok_list,freq_dict): #this takes a list (tok_list) and a dictionary (freq_dict) as arguments
	for x in tok_list: #for x in list
		if x not in freq_dict: #if x not in dictionary
			freq_dict[x] = 1 #create new entry
		else: #else: add one to entry
			freq_dict[x] += 1
			
def corpus_context_freq(dir_name,target,nleft = 5,nright = 5, ending=".txt"): #if we wanted to add lemmatization, we would need to add an argument for a lemma dictinoary
	left_freq = {} #frequency of items to the left
	right_freq = {} #frequency of items occuring to the right
	combined_freq = {} #combined left and right frequency
	target_freq = {} #frequency dictionary for all target hits
	corp_freq = {} #total frequency for all words

	#create a list that includes all files in the dir_name folder that end in ".txt"
	filenames = glob.glob(os.path.join(dir_name, "**", "*"+ending), recursive=True)
	#iterate through each file:
	for filename in filenames:
		#open the file as a string
		text = open(filename, errors = "ignore").read()
		#tokenize text using our tokenize() function
		tok_list = tokenize(text)

		#if we wanted to lemmatize our text, we would use the lemmatize function here

		for idx, x in enumerate(tok_list): #iterate through token list using the enumerate function. idx = list index, x = list item
			freq_update([x],corp_freq) #here we update the corpus frequency for all words. Note that we put x in a one-item list [x] to conform with the freq_update() parameters (it takes as list as an argument)

			hit = False #set Boolean value to False - this will allow us to use a list or a regular expression as a search term
			if type(target) == str and re.compile(target).match(x) != None: #If the target is a string (i.e., a regular expression) and the regular expression finds a match in the string (the slightly strange syntax here literally means "if it doesn't not find a match")
				hit = True #then we have a search hit
			elif type(target) == list and x in target: #if the target is a list and the current word (x) is in the list
				hit = True #then we have a search hit

			if hit == True: #if we have a search hit:

				if idx < nleft: #deal with left context if search term comes early in a text
					left = tok_list[:idx] #get x number of words before the current one (based on nleft)
					freq_update(left,left_freq) #update frequency dictionary for the left context
					freq_update(left,combined_freq) #update frequency dictionary for the all contexts
				else:
					left = tok_list[idx-nleft:idx] #get x number of words before the current one (based on nleft)
					freq_update(left,left_freq) #update frequency dictionary for the left context
					freq_update(left,combined_freq) #update frequency dictionary for the all contexts
				t = x
				freq_update([t],target_freq) #update frequency dictionary for target hits; Note that we put x in a one-item list [x] to conform with the freq_update() parameters (it takes as list as an argument)

				right = tok_list[idx+1:idx+nright+1] #get x number of words after the current one (based on nright)
				freq_update(right,right_freq) #update frequency dictionary for the right context
				freq_update(right,combined_freq) #update frequency dictionary for the all contexts

	output_dict = {"left_freq" : left_freq,"right_freq" : right_freq, "combined_freq" : combined_freq, "target_freq" : target_freq, "corp_freq" : corp_freq}
	return(output_dict)

def soa(freq_dict,cut_off = 5):
	mi = {}
	tscore = {}
	faith_coll_cue = {}
	faith_target_cue = {}
	deltap_coll_cue = {}
	deltap_target_cue = {}

	corpus_size = sum(freq_dict["corp_freq"].values()) #get the size of the corpus by summing the frequency of all words . This will stay consistent for all iterations below
	target_freq = sum(freq_dict["target_freq"].values()) #get the total number of corpus hits for all forms of the target item. This will stay consistent for all iterations below
	#print(freq_dict["combined_freq"])
	#iterate through context hits
	for collocate in freq_dict["combined_freq"]:
		observed = freq_dict["combined_freq"][collocate] #frequency of target coocurring with collocate
		collocate_freq = freq_dict["corp_freq"][collocate] #Total frequency of collocate in corpus

		if freq_dict["combined_freq"][collocate]  >= cut_off: #check to make sure that the collocate occurs frequently enough to surpass the threshold
			expected = ((target_freq * collocate_freq)/corpus_size)

			mi[collocate] =  math.log2(observed/expected) #calculate MI score and add it to dict


			tscore[collocate] = (observed-expected)/(math.sqrt(observed)) #calcuate T score and add it to dict

			#	 y  -y
			#	_______
			# x | a | b
			#	 ___|___
			# -x| c | d
			#
			# deltap P(outcome|cue) - P(outcome|-cue)
			# delta P(y|x) = (a/(a+b)) - (c/(c+d))
			# delta P(x|y) = (a/(a+c)) - (b/(b+d))
			#x = collocate
			#y = target
			a = observed
			b = collocate_freq - a
			c = target_freq - a
			d = corpus_size - (a+b+c)

			#finish this!
			faith_coll_cue[collocate] = (a/(a+b)) #P(target | collocate)
			faith_target_cue[collocate] = (a/(a+c)) ##P(collocate | target)

			deltap_coll_cue[collocate] = (a/(a+b)) - (c/(c+d)) #P(target | collocate) - P(target | -collocate)
			deltap_target_cue[collocate] = (a/(a+c)) - (b/(b+d)) #P(collcate | target) - P(collocate | -target)

	#create output dictionary:
	output_dict = {"mi" : mi,"tscore" : tscore, "faith_coll_cue" : faith_coll_cue, "faith_target_cue" : faith_target_cue, "deltap_coll_cue" : deltap_coll_cue, "deltap_target_cue" : deltap_target_cue}
	return(output_dict)



# ================= CONCORDANCE =======================
#CONCORD PY08
def concord_regex(tok_list,target_regex,nleft,nright):
	hits = [] #empty list for search hits

	for idx, x in enumerate(tok_list): #iterate through token list using the enumerate function. idx = list index, x = list item
		if re.compile(target_regex).match(x) != None: #If the target regular expression finds a match in the string 
			                                            #(the slightly strange syntax here literally means "if it doesn't not find a match")

			if idx < nleft: #deal with left context if search term comes early in a text
				left = tok_list[:idx] #get x number of words before the current one (based on nleft)
			else:
				left = tok_list[idx-nleft:idx] #get x number of words before the current one (based on nleft)

			t = x #set t as the item
			right = tok_list[idx+1:idx+nright+1] #get x number of words after the current one (based on nright)
			hits.append([left,t,right]) #append a list consisting of a list of left words, the target word, and a list of right words

	return(hits)
def corp_conc_regex(corp_folder,target,nhits,nleft,nright, ending=".txt"):
	hits = []

	filenames = glob.glob(os.path.join(corp_folder, "**", "*"+ending), recursive=True) #make a list of all .txt file in corp_folder
	for filename in filenames: #iterate through filename
		text = tokenize(open(filename, encoding='utf-8', errors="ignore").read())
		#add concordance hits for each text to corpus-level list:
		for x in concord_regex(text,target,nleft,nright): #here we use the concord() function to generate concordance lines
			hits.append(x)

	# now we generate the random sample
	if len(hits) <= nhits: #if the number of search hits are less than or equal to the requested sample:
		print("Search returned " + str(len(hits)) + " hits.\n Returning all " + str(len(hits)) + " hits")
		return(hits) #return entire hit list
	else:
		print("Search returned " + str(len(hits)) + " hits.\n Returning a random sample of " + str(nhits) + " hits")
		return(random.sample(hits,nhits)) #return the random sample
def count_concord_targets(concord_list):
    """
    Takes the output of corp_conc_regex() (a list of [left, target, right] lists)
    and returns a dictionary of counts for each distinct target word.
    """
    targets = [x[1] for x in concord_list]  # extract the middle (target) word
    counts = Counter(targets)
    return dict(counts)


#============================KEYNESS====================

def key_tokenize(input_string,gram_size=1, separator = " "): #input_string = text string

	tokenized = [] #empty list that will be returned

	#these are the punctuation marks in the Brown corpus + '"'
	punct_list = ['-',',','.',"'",'&','`','?','!',';',':','(',')','$','/','%','*','+','[',']','{','}','"']

	#this is a sample (but potentially incomplete) list of items to replace with spaces
	replace_list = ["\n","\t"]

	#This is a sample (but potentially incomplete) list if items to ignore
	ignore_list = [""]

	#iterate through the punctuation list and delete each item
	for x in punct_list:
		input_string = input_string.replace(x, "") #instead of adding a space before punctuation marks, we will delete them (by replacing with nothing)

	#iterate through the replace list and replace it with a space
	for x in replace_list:
		input_string = input_string.replace(x," ")

	#our examples will be in English, so for now we will lower them
	#this is, of course optional
	input_string = input_string.lower()

	#then we split the string into a list
	input_list = input_string.split(" ")

	for x in input_list:
		if x not in ignore_list: #if item is not in the ignore list
			tokenized.append(x) #add it to the list "tokenized"

	if gram_size == 1: #if we are looking at single words, simply return tokenized
		return(tokenized)

	else: #otherwise, return n-gram text, using the ngrammer() function
		return(ngrammer(tokenized,gram_size,separator))

def ngrammer(token_list, gram_size, separator = " "):
	ngrammed = [] #empty list for n-grams

	for idx, x in enumerate(token_list): #iterate through the token list using enumerate()

		ngram = token_list[idx:idx+gram_size] #get current word token_list plus words n-words after (this is a list)

		if len(ngram) == gram_size: #don't include shorter ngrams that we would get at the end of a text
			ngrammed.append(separator.join(ngram)) # join the list of ngram items using the separator (by default this is a space), add to ngrammed list

	return(ngrammed) #return list of ngrams

def corpus_freq(dir_name,gram_size = 1,separator = " ", ending = ".txt"):
	freq = {} #create an empty dictionary to store the word : frequency pairs

	#create a list that includes all files in the dir_name folder that end in ".txt"
	filenames = glob.glob(os.path.join(dir_name, "**", "*"+ending), recursive=True)
	#filenames = glob.glob(dir_name + "/*.txt")

	#iterate through each file:
	for filename in filenames:
		#open the file as a string
		text = open(filename, errors = "ignore").read()
		#tokenize text using our tokenize() function
		tokenized = key_tokenize(text,gram_size,separator) #use tokenizer indicated in function argument (e.g., "tokenize()" or "ngramizer()")

		#iterate through the tokenized text and add words to the frequency dictionary
		for x in tokenized:
			#the first time we see a particular word we create a key:value pair
			if x not in freq:
				freq[x] = 1
			#when we see a word subsequent times, we add (+=) one to the frequency count
			else:
				freq[x] += 1

	return(freq) #return frequency dictionary

def keyness(freq_dict1,freq_dict2): #this assumes that raw frequencies were used. effect options = "log-ratio", "%diff", "odds-ratio"
	keyness_dict = {"log-ratio": {},"%diff" : {},"odds-ratio" : {}, "c1_only" : {}, "c2_only":{}}

	#first, we need to determine the size of our corpora:
	size1 = sum(freq_dict1.values()) #calculate corpus size by adding all of the values in the frequency dictionary
	size2 = sum(freq_dict2.values()) #calculate corpus size by adding all of the values in the frequency dictionary

	#How to calculate three measures of keyness:
	def log_ratio(freq1,size1,freq2,size2):  #see Gabrielatos (2018); Hardie (2014)
		freq1_norm = freq1/size1 * 1000000 #norm per million words
		freq2_norm = freq2/size2 * 1000000 #norm per million words
		index = math.log2(freq1_norm/freq2_norm) #calculate log ratio
		return(index)

	def perc_diff(freq1,size1,freq2,size2): #see Gabrielatos (2018); Gabrielatos and Marchi (2011)
		freq1_norm = freq1/size1 * 1000000 #norm per million words
		freq2_norm = freq2/size2 * 1000000 #norm per million words
		index = ((freq1_norm-freq2_norm) * 100)/freq2_norm #calculate perc_diff
		return(index)

	def odds_ratio(freq1,size1,freq2,size2): #see Gabrielatos (2018); Everitt (2002)
		index = (freq1/(size1-freq1))/(freq2/(size2-freq2))
		return(index)


	#make a list that combines the keys from each frequency dictionary:
	all_words = set(list(freq_dict1.keys()) + list(freq_dict2.keys())) #set() creates a set object that includes only unique items

	#if our items only occur in one corpus, we will add them to our "c1_only" or "c2_only" dictionaries, and then ignore them
	for item in all_words:
		if item not in freq_dict1:
			keyness_dict["c2_only"][item] = freq_dict2[item]/size2 * 1000000 #add normalized frequency (per million words) to c2_only dictionary
			continue #move to next item in the list
		if item not in freq_dict2:
			keyness_dict["c1_only"][item] = freq_dict1[item]/size1 * 1000000 #add normalized frequency (per million words) to c1_only dictionary
			continue #move to next item on the list

		keyness_dict["log-ratio"][item] = log_ratio(freq_dict1[item],size1,freq_dict2[item],size2) #calculate keyness using log-ratio

		keyness_dict["%diff"][item] = perc_diff(freq_dict1[item],size1,freq_dict2[item],size2) #calculate keyness using %diff

		keyness_dict["odds-ratio"][item] = odds_ratio(freq_dict1[item],size1,freq_dict2[item],size2) #calculate keyness using odds-ratio

	return(keyness_dict) #return dictionary of dictionaries



#Print outputs
def head(stat_dict,hits = 20,hsort = True,output = False,filename = None, sep = "\t"):
	#first, create sorted list. Presumes that operator has been imported
	sorted_list = sorted(stat_dict.items(),key=operator.itemgetter(1),reverse = hsort)[:hits]

	if output == False and filename == None: #if we aren't writing a file or returning a list
		for x in sorted_list: #iterate through the output
			print(x[0] + "\t" + str(x[1])) #print the sorted list in a nice format

	elif filename is not None: #if a filename was provided
		outf = open(filename,"w") #create a blank file in the working directory using the filename
		outf.write("item\tstatistic") #write header
		for x in sorted_list: #iterate through list
			outf.write("\n" + x[0] + sep + str(x[1])) #write each line to a file using the separator
		outf.flush() #flush the file buffer
		outf.close() #close the file

	if output == True: #if output is true
		return(sorted_list) #return the sorted list
	
#===================ANALYSIS=================
#frequency RQ 2
forms = ("like", "liked", "likes", "liking", "likely")

SB_left_right = corpus_context_freq("SBCorpus","like",nleft = 5,nright = 5, ending=".trn")
#print("Most frequest words in SB")
#head(SB_left_right["corp_freq"], hits=10)
SB_like = {f: SB_left_right["corp_freq"].get(f, 0) for f in forms}
#print(f"Frequency of like: {SB_like}")
SB_values = sum(SB_left_right["corp_freq"].values())
#print("SB total words:", SB_values)
#print(f"like parts per 100,000 in SB: {(sum(SB_like.values()) / SB_values)*100000}")

MASC_left_right = corpus_context_freq("MASC_written", "like", nleft=5, nright=5, ending=".txt")
#print("10 Most frequent words in MASC")
#head(MASC_left_right["corp_freq"], hits=10)
MASC_like = {f: MASC_left_right["corp_freq"].get(f, 0) for f in forms}
#print(f"Frequency of like: {MASC_like}")
MASC_values = sum(MASC_left_right["corp_freq"].values())
#print("MASC total words:", MASC_values)
#print(f"Like parts per 100,000 in MASC: {(sum(MASC_like.values()) / MASC_values)*100000}")


#-------------Collocation-----------
left_right_soa = soa(SB_left_right, cut_off=5)
#head(left_right_soa["faith_target_cue"], hits=10)

SB_left = corpus_context_freq("SBCorpus","like",nleft = 5,nright = 0, ending=".trn")
left_soa = soa(SB_left)
#head(left_soa["faith_target_cue"], hits=10)

SB_right = corpus_context_freq("SBCorpus","like",nleft = 0,nright = 5, ending=".trn")
right_soa = soa(SB_right)
#head(right_soa["faith_target_cue"], hits=10)

#Collocation for MASC
MASC_left_right_soa = soa(MASC_left_right, cut_off=5)
#head(MASC_left_right_soa["faith_target_cue"], hits=10)

MASC_left = corpus_context_freq("MASC_written", "like", nleft=5, nright=0, ending=".txt")
MASC_left_soa = soa(MASC_left, cut_off=5)
#head(MASC_left_soa["faith_target_cue"], hits=10)

MASC_right = corpus_context_freq("MASC_written", "like", nleft=0, nright=5, ending=".txt")
MASC_right_soa = soa(MASC_right, cut_off=5)
#head(MASC_right_soa["faith_target_cue"], hits=10)

#--------------KEYNESS------------
#SB
sb = corpus_freq("SBCorpus", gram_size=2, ending=".trn")
#Filtering for only analysis that have "like"
sb_like = {x: sb[x] for x in sb if "like" in x}

#MASC
masc = corpus_freq("MASC_written", gram_size=2, ending=".txt")
#Filtering for only analysis that have "like"
masc_like = {x: masc[x] for x in masc if "like" in x}

key = keyness(sb_like,masc_like)
#head(key["%diff"], hits=10)
#head(key["c1_only"], hits=10)
#print("C2")
#head(key["c2_only"], hits=10)

#--------CONCORDANCE---------
SB_conc = corp_conc_regex("SBCorpus", "like", 50, 5, 5, ending=".trn")
print(SB_conc)
#SB_conc_count = count_concord_targets(SB_conc)
#print(SB_conc_count)

MASC_conc = corp_conc_regex("MASC_written", "like", 50, 5, 5, ending=".txt")
print(MASC_conc)
#MASC_conc_count = count_concord_targets(MASC_conc)
#print(MASC_conc_count)