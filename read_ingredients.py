import re
from nltk.parse.stanford import StanfordDependencyParser
path_to_jar = r'C:\Users\Lovisa\Downloads\stanford-corenlp-full-2016-10-31\stanford-corenlp-full-2016-10-31\stanford-corenlp-3.7.0.jar'
path_to_models_jar = r'C:\Users\Lovisa\Downloads\stanford-corenlp-full-2016-10-31\stanford-corenlp-full-2016-10-31\stanford-corenlp-3.7.0-models.jar'
dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)
from nltk.tag import StanfordPOSTagger
st = StanfordPOSTagger('english-bidirectional-distsim.tagger')
from nltk import word_tokenize

from nltk.stem import WordNetLemmatizer
wl = WordNetLemmatizer()

def read_ingredients( filename, ing_list , new_ingredients):
    ingredients = {}
    section = None
    with open('baking_recipes/' + filename,'r') as f:
        for line in f:
            if "INGREDIENTS" in line:
                continue
            if "PREPARATION" in line:
                break
            ##Ignore any blank lines
            line = line.strip()
            if not line:
                continue
            
            if line.endswith(":"):  #structural assumption: sections end with colon
                section = line
                continue
            ############### remove bracketed information
            line = re.sub("[\(\[].*?[\)\]]", "", line)
            ############
            
            wordlist = line.split()
 
            line = line.replace("/", "//")
            original = line                     #thus original wont be a "true original"
            line = line.replace("  ", " ")
            line = line.replace(" ,", ",")
            #print(line)
            result = dependency_parser.raw_parse(line)
            dep = result.__next__()
            triplet_list = list(dep.triples())
            #print(triplet_list)
            ###### Handle quantities and measures first ######
            quantity = None
            measure = None
            if wordlist[1][0].isdigit(): #If second word is a number too ( e.g. "1 1/4" )
                quantity = ' '.join(wordlist[:2])
                measure = wordlist[2]
            elif wordlist[0][0].isdigit() and not wordlist[1][0].isdigit():
                quantity = wordlist[0]
                measure = wordlist[1] 
            else:
                quantity = ""               # I should handle this differently.

            #print("Quantity is " + quantity)
            #print("Measure is " + str( measure))
            ####################
            adjectives = []
            nouns = []
            for triplet in triplet_list:
                    
                if (triplet[0][1].startswith('NN')) and triplet[0][0] not in nouns and (triplet[0][0] != measure):
                    word = triplet[0][0]
                    #Check for compounds
                    added = False
                    for triplet in triplet_list:        
                        if (triplet[0][0] == word or triplet[2][0] == word) and triplet[2][0] != measure and (triplet[1] == 'compound' or triplet[1] == 'amod' or triplet[1] == 'dobj'): #and (triplet[0][0] not in adjectives) and (triplet[2][0] not in adjectives):
                            if triplet[1] == 'dobj':
                                nouns.append( triplet[0][0] + " " + triplet[2][0] )
                            else:
                                nouns.append( triplet[2][0] + " " + triplet[0][0] )
                            added = True                    
                    if not added:
                        nouns.append( word )
                elif (triplet[2][1].startswith('NN')) and triplet[2][0] not in nouns and (triplet[2][0] != measure):
                    word = triplet[2][0]
                    #Check for compounds
                    added = False
                    for triplet in triplet_list:        
                        if (triplet[0][0] == word or triplet[2][0] == word) and triplet[2][0] != measure and (triplet[1] == 'compound' or triplet[1] == 'amod' or triplet[1] == 'dobj'): #and (triplet[0][0] not in adjectives) and (triplet[2][0] not in adjectives):
                            if triplet[1] == 'dobj':
                                nouns.append( triplet[0][0] + " " + triplet[2][0] )
                            else:
                                nouns.append( triplet[2][0] + " " + triplet[0][0] )
                            added = True                    
                    if not added:
                        nouns.append( word )
                else:
                    continue

            for triplet in triplet_list:
                if (triplet[0][1] == 'JJ' or triplet[0][1].startswith('VB')) and triplet[0][0] not in nouns:
                    adjectives.append(triplet[0][0])
                    #print(triplet[0][0])
                if (triplet[2][1] == 'JJ' or triplet[2][1].startswith('VB')) and triplet[2][0] not in nouns:
                    adjectives.append(triplet[2][0])
                    #print(triplet[2][0])

            ###here I need to select from nouns somehow
            nouns = list(set(nouns))
            #print("INITIAL NOUNS: " + str(nouns))
            adjectives = list(set(adjectives))
            #print("INITIAL ADJS: " + str(adjectives))

            #collecting individual words so that compounds don't pose problems later.
            nounwords = []
            for n in nouns:
                wds = n.split()
                if len(wds)==2:
                    nounwords.append( wds[0] )
                    nounwords.append( wds[1] )
                else:
                    nounwords.append( wds[0] )
            ###CHECKING WITH THE OTHER PARSER
            tagged = st.tag(word_tokenize(line))
            #print(tagged)
            for tuple in tagged:
                if tuple[0].isdigit() or tuple[0] == measure: #Ignore any initial quantity/measure specs
                    continue
                elif tuple[1].startswith('NN'):# and tuple[0]: #not in nounwords: #uncaptured nouns
                    nouns.append(tuple[0])
                    if tuple[0] in adjectives:          #nouns that have been incorrectly captured as adjective
                        adjectives.remove( tuple[0])
                        
                    continue
                elif tuple[1].startswith('VB') or tuple[1] == 'JJ': #and tuple[0] not in adjectives: 
                    adjectives.append(tuple[0])

                    toberemoved = []
                    for i in range(len(nouns)):
                        if tuple[0] in nouns[i]:        #adjective incorrectly captured as noun
                            toberemoved.append(nouns[i])
                    for t in toberemoved:
                        nouns.remove(t)
                    continue
                else:
                    continue
                
##            tagged_adj = st.tag(adjectives)                         #These can ruin
##            for item in tagged_adj:
##                if item[1].startswith('NN'):
##                    adjectives.remove(item[0])
            nouns = list(set(nouns))
            adjectives = list(set(adjectives))

            #print("ADJECTIVES ARE" + str(adjectives))

##            tagged_noun = st.tag(nouns)                             #These can ruin
##            for item in tagged_noun: 
##                if not item[1].startswith('NN'):
##                        nouns.remove(item[0])

            key = nouns[0]      #default so that it never is None
            ###ugly hack
            compoundwd = False
            if len(nouns) > 1:
                for n in nouns:
                    if n == '/':
                        nouns.remove(n)
                        continue
                                 #temporary key variable
                    splitted = n.split()
                    if len(splitted) == 2:
                        key = n
                        compoundwd = True
                        break
                        
##                        key_t = n  
##                        print("DOUBLE WORD: " + n)
##                        for m in nouns:
##                            if n[0]== m:
##                                compoundwd = True
##                                break
##                    if compoundwd:
##                        break
            if not compoundwd:
                key = ' '.join(nouns)
                            
            #print("NOUNS ARE" + str(nouns))
            #print(key)
            ingredients[ key ] = {}
            ingredients[ key ]["Quantity"] = quantity
            ingredients[ key ]["Measure"] = measure
            lemma = wl.lemmatize(key).lower()       #immediately search ontology????? COMPOUNDS????
            lemmal = lemma.split()
            ingredients[ key ]["Lemma"] = lemma
            ingredients[key]["Image"] = ["None"]
            found = False
            for w in lemmal:
                if w in ing_list:
                    ingredients[key]["Image"] = w
                    found = True
                    break
            if not found:
                new_ingredients.append(lemma)
            ingredients[ key ]["Adjectives"] = adjectives       
            ingredients[ key ]["Original"] = original
            ingredients[ key ]["Section"] = section
            #print(ingredients[ key])

            ####
    all_lemmas = []
    with open('current_recipe_ings.txt','w') as fi:
        for k in ingredients.keys():
            cur_lemma = ingredients[ k ]["Lemma"]
            all_lemmas.append(cur_lemma.split())
            fi.write(cur_lemma + "\n")
    fi.close()

    return ingredients, new_ingredients, all_lemmas
