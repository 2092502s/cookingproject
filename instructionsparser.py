#import nltk
from difflib import SequenceMatcher

def listingredients():
	ing_list = []
	with open('ingredients.txt', 'r') as f:
		for line in f:
			linelist = line.split(':',1)
			ing_list.append(linelist[0])
			#print(linelist[0])
	return ing_list

def collectinstructions( recipefilename ):
    #this dictionary is file-specific...
    ingredients = {}
    equipment = ""
    with open('baking_recipes/' + recipefilename,'r') as f:
        start = False
        instructions = []
        par_count = -1       #paragraph-count
        for line in f:
            if start is False:
                if "PREPARATION" not in line:
                    continue
                else:
                    start = True
                    continue
            ##Ignore any blank lines
            line = line.strip()
            if not line:
                par_count += 1  #Increment paragraph-count
                instructions.append("")
                instructions[par_count] += line
                continue
            else:
                instructions[par_count] += line

    f.close()
    return instructions       #a list

def splitParagraphIntoSentences(paragraph):

    import re
    # to split by multile characters
    #   regular expressions are easiest (and fastest)
    sentenceEnders = re.compile('[.!?]')
    sentenceList = sentenceEnders.split(paragraph)
    return sentenceList


def parseintosentences( instructions ):

    paragraphs = {}
    for i in range(0,len(instructions)):    #loop over the nr of paragraphs
        paragraphs[i] = splitParagraphIntoSentences( instructions[i] )
    return paragraphs


##################### MAIN SECTION ###############################

ing_list = listingredients()

instructions = collectinstructions( "best_cocoa_brownies.txt" )
paragraphs = parseintosentences( instructions )

firstwords = [] * len(paragraphs.keys())

for key in range(0,len(paragraphs.keys())):
    for sent in paragraphs[i]:
        words = sent.split()
        if len(words) >= 1:
            firstwords[i].append(words[0])

print(firstwords)
#print the first word
#print(paragraphs)

#Make a method: which ingredients are mentioned?
for par in paragraphs.keys():
    sentence_list = paragraphs[par]
    for sentence in sentence_list:
        words = sentence.split()
        for word in words:
            for keyword in ing_list:
                keyw = keyword.split()
                for w in keyw:
                    sim_ratio = SequenceMatcher(None, word, w).ratio()



#text = nltk.word_tokenize( paragraphs[0][0] )
#print(nltk.pos_tag(text))
