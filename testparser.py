###################################################################

#for pythonanywhere deployment? 
#os.environ["JAVA_PATH"]
#os.environ["CLASSPATH"]
#os.environ["STANFORD_MODELS"]

import nltk
from nltk.tag import StanfordPOSTagger
st = StanfordPOSTagger('english-bidirectional-distsim.tagger')

import nltk.data
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

import re

from nltk.stem import WordNetLemmatizer
wl = WordNetLemmatizer()

from nltk.parse.stanford import StanfordDependencyParser
#Not quite sure how to deal with this upon migrating....
path_to_jar = r'C:\Users\Lovisa\Downloads\stanford-corenlp-full-2016-10-31\stanford-corenlp-full-2016-10-31\stanford-corenlp-3.7.0.jar'
path_to_models_jar = r'C:\Users\Lovisa\Downloads\stanford-corenlp-full-2016-10-31\stanford-corenlp-full-2016-10-31\stanford-corenlp-3.7.0-models.jar'
dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)


########## FILE-HANDLING ######################################################


file_names = [ 'apricot_almond_layer_cake.txt',
               'best_cocoa_brownies.txt',
               'chewy_coconut_chocolate_chip_cookies.txt',
               'chocolate_chip_coffee_cake.txt',
               'chocolate_cream_cheese_cupcakes.txt',
               'chocolate_peanut_butter_cake.txt',
               'danish_pastry_bread.txt',
               'fresh_coconut_layer_cake.txt',
               'frozen_passion_fruit_meringue_cake.txt',
               'lemon_blossom_cupcakes.txt',
               'mascarpone_filled_cake_with_sherried_berries.txt',
               'mile_high_chocolate_cake.txt',
               'persian_love_cake.txt',
               'rich_chocolate_cake.txt',
               'rum_scented_marble_cake.txt',
               'strawberry_and_chocolate_baked_alaska.txt',
               'sunshine_cake.txt',
               'white_chocolate_espresso_torte.txt',
               'yogurt_cake_with_currant_raspberry_sauce.txt'
            ]

new_ingredients = [ ]       ### I GUESS THIS SHOULD BE WRITTEN TO A FILE????

def read_instructions( filename ):  #meant to simply return a list of sentences
    readstart = False
    inst_string = ""
    with open('baking_recipes/' + filename, 'r') as f:
        for line in f:
            if "PREPARATION" in line:
                readstart = True
                continue            
            if not readstart:
                continue
            #line = line.strip()        #I think the Stanford parser handles this
            #if not line:
            #    continue
            inst_string += line
    return inst_string

############## Sketchpad
            

######################################################

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
            tagged = st.tag(nltk.word_tokenize(line))
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
            lemma = lemma.split()
            ingredients[key]["Image"] = ["None"]
            found = False
            for w in lemma:
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
    return ingredients, new_ingredients                
                
         
########################################################################
def listingredients():
	ing_list = []
	with open('ingredients.txt', 'r') as f:
		for line in f:
			linelist = line.split(':',1)
			ing_list.append(linelist[0])    #Should I lemmatise every single word here?
			#print(linelist[0])
	return ing_list


def par_into_sent(text):                ###Imagine text coming in as a single string via the web-app
    testsents = sent_detector.tokenize( text.strip() ) #Parse the 
    for s in testsents:
        testsents[testsents.index(s)] = s.strip('\n')
        match = re.match( "(1|2|3|4|5|6|7|8|9)+.",s)           #Match() checks for a match only in the beginning
        if match:
            #testsents[testsents.index(s)] = s[match.start():]   #sent
            testsents.remove(s)                 #Not sure if I can remove it dynamically
            continue
        twosome = s.split(':',1)
        if len(twosome) == 2:
            index = testsents.index(s)
            testsents[index] = twosome[0] + ":"
            testsents.insert(index+1, twosome[1] )

    sentence_dict = { }
    i = 1
    for s in testsents:
        sentence_dict[i] = {}
        sentence_dict[i]["original"] = s
        sentence_dict[i]["orig"] = s            #will always remain unmodified
        i += 1
    #print( sentence_dict )
    return sentence_dict

def find_all_ingr_from_dep(triplet_list):
    action_dict = { }
    for triplet in triplet_list:
        if triplet[1] == 'dobj'or triplet[1] == 'nsubj':### You have identified a verb and noun dependency
            #print("Verb identified: " + triplet[0][0])
            #print("Noun identified: " + triplet[2][0])
            verb = triplet[0][0]
            noun = triplet[2][0]
            noun_conjs = []
            ### CHECK IF IT IS A COMPOUND
            added = False
            for tr in triplet_list:
                if tr[0][0] == noun and (tr[1] == 'compound' or tr[1] == 'amod'):
                    noun_conjs.append(tr[2][0] + " " + tr[0][0])
            if not added:
                noun_conjs.append(noun)
            #CHECK FOR COMPOUNDS
                
            for trip in triplet_list:
                dep = trip[0][0]
                if dep == noun and trip[1] == 'conj':       ###Conjunct found for the noun
                    dep2 = trip[2][0]   #the thing it is AND-chained to 
                    #print("Conjunct identified: "+ trip[2][0])
                    #noun_conjs.append(dep2)
                    addedcomp = False
                    for t in triplet_list:
                        if (t[0][0] == dep2 and (t[1] == 'compound' or t[1] == 'amod')):
                            #print("Compound identified: " + t[2][0] + t[0][0])
                            noun_conjs.append(t[2][0] + " " + t[0][0] )
                            addedcomp = True
                    if not addedcomp:
                            noun_conjs.append(dep2)
            
            action_dict[ verb ] = noun_conjs

    #### I want to give dobj-dependencies preference
    for triplet in triplet_list:
        if (triplet[1] == 'nmod' and triplet[0][1].startswith('VB') and triplet[0][0] not in action_dict.keys()):                ### You have identified a verb and noun dependency
            #print("Verb identified: " + triplet[0][0])
            #print("Noun identified: " + triplet[2][0])
            verb = triplet[0][0]
            noun = triplet[2][0]
            noun_conjs = []
            ### CHECK IF IT IS A COMPOUND
            added = False
            for tr in triplet_list:
                if tr[0][0] == noun and (tr[1] == 'compound' or tr[1] == 'amod'):
                    noun_conjs.append(tr[2][0] + " " + tr[0][0])
            if not added:
                noun_conjs.append(noun)
            #CHECK FOR COMPOUNDS
            for trip in triplet_list:
                dep = trip[0][0]
                if dep == noun and trip[1] == 'conj':       ###Conjunct found for the noun
                    dep2 = trip[2][0]   #the thing it is AND-chained to 
                    #print("Conjunct identified: "+ trip[2][0])
                    #noun_conjs.append(dep2)
                    addedcomp = False
                    for t in triplet_list:
                        if (t[0][0] == dep2 and (t[1] == 'compound' or t[1] == 'amod')):
                            #print("Compound identified: " + t[2][0] + t[0][0])
                            noun_conjs.append(t[2][0] + " " + t[0][0] )
                            addedcomp = True
                    if not addedcomp:
                            noun_conjs.append(dep2)
            
            action_dict[ verb ] = noun_conjs    

    #FETCH ALL REMAINING VERBS            
    for triplet in triplet_list:
        #### IT REACHES HERE AFTER IT HAS PROCESSED ALL DOBJ-DEPENDENCIES
        if (triplet[0][1].startswith('VB') and triplet[0][0] not in action_dict.keys()):
            action_dict[ triplet[0][0] ] = []
            
        if (triplet[2][1].startswith('VB')) and triplet[2][0] not in action_dict.keys():
            action_dict[ triplet[2][0] ] = []

    action_dict["verbless"] = []
    allnouns = []
    for ls in action_dict.values():
        for l in ls:
            allnouns.append(l)
            
    for triplet in triplet_list:           
        if triplet[0][1].startswith('NN') and triplet[0][0] not in allnouns:
            word = triplet[0][0]
            addedcomp = False
            #Again, check for compounds
            for t in triplet_list:      
                if ((t[0][0] == word or t[2][0] == word) and (t[1] == 'compound' or t[1] == 'amod')):

                    action_dict["verbless"].append(t[2][0] + " " + t[0][0] )
                    addedcomp = True
            if not addedcomp:
                action_dict["verbless"].append(word)
        elif triplet[2][1].startswith('NN') and triplet[2][0] not in allnouns:
            word = triplet[2][0]
            addedcomp = False
            for t in triplet_list:
                if ((t[0][0] == word or t[2][0] == word) and (t[1] == 'compound' or t[1] == 'amod')):

                    action_dict["verbless"].append(t[2][0] + " " + t[0][0] )
                    addedcomp = True
            if not addedcomp:
                action_dict["verbless"].append(word)
            
    action_dict["verbless"] = list(set(action_dict["verbless"]))
    return action_dict

def extract_cardinals(triplet_list):

    acts_with_numbers = { }
    acts_with_numbers[ 'verbless' ] = []
    found_cardinals = []
    for triplet in triplet_list:            #Look for a cardinal number
        which = 1
        other = 1
        if triplet[0][1] == 'CD' and triplet[0][0] not in found_cardinals: #We don't want to relaunch search on same number
            which = 0
            other = 2
        if triplet[2][1] == 'CD' and triplet[2][0] not in found_cardinals:
            which = 2
            other = 0
        if which is not 1:                  #A new cardinal number has been found...
            #print("found cd: " + triplet[which][0])
            found_cardinals.append ( triplet[which][0] )
            
            otherword = triplet[other][0]

            #Is the other one a verb? If so, add it as key to dict and move immediately forward.
            if triplet[other][1].startswith('VB')  or triplet[other][0].lower() in action_list:       #e.g. preheat + 325F                
                acts_with_numbers[ otherword ] = triplet[which][0]
                #print("Found verb immediately! " + otherword)
                
            else:
                unit = ""                       
                foundverb = False
                if triplet[1] == 'nummod' or triplet[1] == 'nmod' or triplet[1] == 'compound': #These usually indicate units, e.g.('one', 'CD'), 'nmod', ('time', 'NN') ('hour', 'NN'), 'compound', ('1', 'CD')
                    unit = otherword
                    ## TODO:check if unit is in ingredients-list,
                    # so that it is not something useless like "one time"           #Note: Im not sure if it's exhaustive
                i = 0
                length = len(triplet_list)
                verb_cand = otherword
                #print("first cand is " + verb_cand)
                visited = []        #save indices of explored triples
                verbs = []
                while i < length:                #Do at most one search per triple

                    #Firstly, do a check if any is accompanied by a verb (best case scenario)
                    for trip in triplet_list:
                        if triplet_list.index(trip) in visited:     #dont explore visited ones any further. This wont ever be entered.
                            continue
                        if ( trip[2][0] == verb_cand and (trip[0][1].startswith('VB') or trip[0][0].lower() in action_list)):
                            acts_with_numbers[ trip[0][0] ] = triplet[which][0] + " " + unit
                            foundverb = True
                            verbs.append( trip[0][0] ) 
                            #print("Found verb! " + trip[0][0])
                            continue
                        if (trip[0][0] == verb_cand and (trip[2][1].startswith('VB')  or trip[2][0].lower() in action_list)):                          
                            acts_with_numbers[ trip[2][0] ] = triplet[which][0] + " " + unit
                            foundverb = True
                            verbs.append( trip[0][0] ) 
                            #print("Found verb! " + trip[2][0])
                            continue  #break out of for-loop
                        
                    if foundverb:   #once verb has been found, we can break while-loop as well
                        break
                    #If first search was successful, this won't be entered, so check for any instance of candidate
                    j = 0

                    #FOR-LOOP MEANT FOR CHANGING CANDIDATE WORD
                    for trip in triplet_list:
                        if triplet_list.index(trip) in visited:     #dont explore visited ones any further
                            continue
                        if (trip[0][0] == verb_cand):     #verb not found yet, so re-launch search on the other one
                            verb_cand = trip[2][0] #look up the other word
                            visited.append( triplet_list.index(trip) )     #pop the triple just visited
                            i += 1
                            #print("changed candidate to " + trip[2][0])
                            break
                            
                        elif (trip[2][0] == verb_cand):
                            verb_cand = trip[0][0]
                            visited.append( triplet_list.index(trip) )     ##pop the triple just visited
                            i += 1
                            #print("changed candidate to " + trip[0][0])
                            break
                        else:                               #no more instance of current search word found
                            j += 1
                            continue
                        
                    if j == len(triplet_list):  #dead-end with verb_cand, no point in continuing
                        break

                        
                if foundverb == False:
                    acts_with_numbers[ 'verbless' ].append( triplet[which][0] + " " + unit)


    return acts_with_numbers #requires post-processing to associate the action
                            #keys with those gathered in the action-extraction



##########################################################################################################
text = '''
Make Cake:
Position a rack in the lower third of the oven and preheat the oven to 325F. Line the bottom and sides of the baking pan with parchment paper or foil, leaving an overhang on two opposite sides. Combine the butter, sugar, cocoa, and salt in a medium heatproof bowl and set the bowl in a wide skillet of barely simmering water. Stir from time to time until the butter is melted and the mixture is smooth and hot enough that you want to remove your finger fairly quickly after dipping it in to test. Remove the bowl from the skillet and set aside briefly until the mixture is only warm, not hot.
Stir in the vanilla with a wooden spoon. Add the eggs one at a time, stirring vigorously after each one. When the batter looks thick, shiny, and well blended, add the flour and stir until you cannot see it any longer, then beat vigorously for 40 strokes with the wooden spoon or a rubber spatula. Stir in the nuts, if using. Spread evenly in the lined pan.
Bake until a toothpick plunged into the center emerges slightly moist with batter, 20 to 25 minutes. Let cool completely on a rack.
Lift up the ends of the parchment or foil liSetner, and transfer the brownies to a cutting board. Cut into 16 or 25 squares.

'''

text2 = '''
Make Cake:
1. Position a rack in the lower third of the oven and preheat the oven to 325F. 2. Line the bottom and sides of the baking pan with parchment paper or foil, leaving an overhang on two opposite sides.
3. Combine the butter, sugar, cocoa, and salt in a medium heatproof bowl and set the bowl in a wide skillet of barely simmering water. 4. Stir from time to time until the butter is melted and the mixture is smooth and hot enough that you want to remove your finger fairly quickly after dipping it in to test. 5. Remove the bowl from the skillet and set aside briefly until the mixture is only warm, not hot.
6. Stir in the vanilla with a wooden spoon. 7. Add the eggs one at a time, stirring vigorously after each one. 8. When the batter looks thick, shiny, and well blended, add the flour and stir until you cannot see it any longer, then beat vigorously for 40 strokes with the wooden spoon or a rubber spatula. 9. Stir in the nuts, if using. 10. Spread evenly in the lined pan.
12. Bake until a toothpick plunged into the center emerges slightly moist with batter, 20 to 25 minutes. 13. Let cool completely on a rack.
14. Lift up the ends of the parchment or foil liSetner, and transfer the brownies to a cutting board. Cut into 16 or 25 squares.

'''

action_list = ['sift','stir','transfer','beat','add','heat','cook','pulse','divide','smooth','bake','preheat','cool','reserve','spread','top',\
               'sprinkle','line','combine','remove','set','cut','cream','whisk','cover','refridgerate','roll','scoop','mix','drizzle','spray',\
               'fold', 'place', 'chill', 'buffer', 'dust','bake']

new_actions = []

aggregates = ['mixture','batter','round','compote','cupcake','muffin','cake']

equipment = ['bowl','mixer','parchment paper','sheet','foil','oven','skillet','platter','rack','beater','spoon','fork','knife','spatula','cutting board', 'plastic wrap', 'pan',\
             'tube pan', 'muffin pan', 'paper liner', 'cake pan']

new_nouns = []
########################################################################     MAIN SECTION !!!!!!!!!!!!!!!!!!!!!      
ing_list = listingredients()          
ingredients, new_ingredients = read_ingredients(file_names[0], ing_list, new_ingredients)   #Handle new_ingredients correctly
#print(ingredients)
inst_str = read_instructions( file_names[0] )
#print(inst_str)
sentence_dict = par_into_sent( inst_str )

for key in sentence_dict.keys():
    original = sentence_dict[key]["original"]
    original = original.replace("/", "//")
    tokenized = st.tag(original.split())

    # MODIFY SLIGHTLY TO ALLOW IMPERATIVES TO BE PROPERLY TAGGED
    if (tokenized[0][1] == 'NN') or (tokenized[0][1] == 'NNP') or (tokenized[0][1] == 'VB'):    #VB since st tagger returns it as VB 
        changed = "We " + original[0].lower() + original[1:]
        sentence_dict[key]["original"] = changed
        original = changed
        

    print( "-----------------------------------------------------------------------------")
    print("ORIGINAL INSTRUCTION: " + original)
    print( "-----------------------------------------------------------------------------")
    #print(st.tag(sentence_dict[key]["original"].split()))
    #print( sentence_dict[key]["verbs"] )
    
    result = dependency_parser.raw_parse(original)
    dep = result.__next__()
    triplet_list = list(dep.triples())
    #print(triplet_list)
    action_dict = find_all_ingr_from_dep(triplet_list)              #What's the format?
    acts_with_numbers = extract_cardinals(triplet_list)             #What's the format?
    print( "Action dictionary ------------------------------------------------------------")
    print(action_dict)
    print( "Actions with associated numbers ----------------------------------------------")
    print (acts_with_numbers)
    print('END----------------------------------------------------------------------------')
    ### FINAL PROCESSING STEPS...
    #
    #  Scan for extra keywords that may have been missed




#text = text.lower()



def extract_verbs(sentence_dict):

    for s in sentence_dict.keys():
        original = sentence_dict[s]["original"]
        tokenized = st.tag(original.split())
        if (tokenized[0][1] == 'NN') or (tokenized[0][1] == 'NNP'):
            sentence_dict[s]["original"] = "We " + original[0].lower() + original[1:]   #we don't modify "orig"
        tokenized = st.tag(original.split())
        sentence_dict[s]["verbs"] = { }
        #print(tokenized)
        for tupl in tokenized:
            sentence_dict[s]["verbs"][verb] = { }
            if tupl[1].startswith('VB'):
                verb = tupl[0]
                #print(verb)
                
                verb_lc = verb.lower()
                if verb_lc in action_list:
                    sentence_dict[s]["verbs"][verb]["picture"] = verb_lc      #Possibly I am better off similarity-matching?
                else:
                    sentence_dict[s]["verbs"][verb]["picture"] = "None"        #No picture of it
                    new_actions.append( verb_lc )

    return sentence_dict

#sentence_dict = par_into_sent(text2)
##sentence_dict = extract_verbs( sentence_dict )
##
##for i in sentence_dict.keys():
##    print( sentence_dict[i]["original"] )
##    for vb in sentence_dict[i]["verbs"].keys():
##        print(vb)

#teststring = "Sift together cake flour, baking powder, baking soda, and salt."
#tokenized = teststring.split()
#print(  st.tag(tokenized) )
#for s in sentence_dict:

#orig = sentence_dict[s]["Sift together cake flour, baking powder, baking soda, and salt."]
#print("ORIGINAL")
#print(orig)
#orig = "Sift together cake flour, baking powder, baking soda, and salt."
text3 = " Position rack in center of oven and preheat to 350F. Butter and flour 10-inch-diameter tube pan, \
then spray with nonstick spray. Mix egg whites, brown sugar, and salt in bowl. Mix in walnuts and 1/4 cup chocolate chips. \
Whisk flour, salt, baking powder, and baking soda in medium bowl. Using electric mixer, beat sugar and butter in large bowl to blend. \
Beat in eggs 1 at a time. Stir in flour mixture in 4 additions alternately with sour cream in 3 additions, \
beginning and ending with flour mixture. Stir in 1 cup chocolate chips. Transfer batter to pan; smooth top. \
Spoon walnut mixture evenly over. Bake cake until tester inserted near center comes out clean, about 1 hour. \
Cool in pan on rack 10 minutes. Turn cake out onto rack; invert onto second rack (walnuts should be on top). Cool. (Can be made 1 day ahead. Wrap in plastic.)"




#####BASICALLY, HAVE WE MISSED SOMETHING
#
#       HAVEN'T ACTUALLY TESTED THIS LOL
#
# 
##def scan_for_additional_words(sentence, action_dict, allnouns, all_ings, recipe_ings, recipe_eq):
##    tokens = nltk.word_tokenize(sentence)
##    action_dict['equipment'] = []
##    for tok in tokens:
##        lemma = wl.lemmatize(tok)
##        lemma.lower()
##        if lemma in actions_list:
##            if tok not in action_dict.values():
##                action_dict[tok] = []
##        if  lemma in equipment or lemma in recipe_eq:
##            if tok not in allnouns:
##                action_dict['equipment'].append(tok)
##        if lemma in all_ings or lemma in recipe_ings:
##            if not in allnouns:
##                action_dict['verbless'].append(tok)
##    return action_dict

######## MAIN SECTION



##sentence_dict = par_into_sent(text3)
##for key in sentence_dict.keys():
##    orig = sentence_dict[key]["original"]
##    result = dependency_parser.raw_parse(orig)
##    dep = result.__next__()
##    triplet_list = list(dep.triples())
##    print( "SENTENCE: " + orig)
##    print(triplet_list)
##    awn = extract_cardinals(triplet_list)
##    print(awn)
