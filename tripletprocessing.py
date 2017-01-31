from actions import action_list
from nltk import word_tokenize
from extract_cardinals import extract_cardinals
from ontologyhandler import is_it_in_actions, is_it_in_recipe_ings, is_it_in_ing_ont, is_it_in_equip, is_it_in_aggs, is_it_in_nouns
#ingredient_list = ['eggs']              # JUST A DUMMIE
#equipment_list = ['mixer']
#agg_list = ['batter']
#all_nouns = equipment_list + ingredient_list + agg_list

def find_compound( triplet_list, first, forced_tags, word_list ):    #you have to force tags yourself
    compound = first
    for t in triplet_list:
        if (t[0][0] == first and (t[1] == 'compound' or t[1] == 'amod')):  # TODO: control concatenation order
            compound = t[2][0] + " " + compound
            index = word_list.index( t[0][0] )
            forced_tags[index] = 'a'
            
    return [compound, forced_tags]




def check_conjuncts( allverbs, verb, noun, triplet_list, forced_tags, word_list ):
    
    for tri in triplet_list:
        if tri[0][0] == noun and tri[1] == 'conj':  #SHOULD I CHECK TYPE OF THE OTHER COMPOUND? yeah, (('egg', 'NN'), 'conj', ('beat', 'NN')).
            other = tri[2][0]
            cmpnd = other
            cmpnd, ft = find_compound( triplet_list, other, forced_tags, word_list )
            forced_tags = ft

            #add noun conjunct
            allverbs[ verb ]['nouns'].append( cmpnd )
            index = word_list.index( other )
            forced_tags[index] = 'n'
    return [allverbs, forced_tags]




def find_closest_verb(forced_tags, word_list, tag_list, tupl):
    # BEGIN BY SEARCHING LEFTWARDS
    closest_verb = None
    noun_cursor = tag_list.index(tupl)
    while noun_cursor >= 0:
        if forced_tags[noun_cursor] == 'v':
            closest_verb = tag_list[ noun_cursor ][0]
            break
        noun_cursor = noun_cursor - 1

    # IF NO MATCH, SEARCH RIGHTWARDS
    if not closest_verb:
        noun_cursor = tag_list.index(tupl)
        while noun_cursor < len(tag_list):
            if forced_tags[noun_cursor] == 'v':
                closest_verb = tag_list[ noun_cursor ][0]
                break
            noun_cursor = noun_cursor + 1
            
    return closest_verb, forced_tags

                        
def find_nltk_tag(word, tag_list):
    nltk_pos = None
    for p in tag_list:
        if p[0] == word:
            nltk_pos=p[1]
    return nltk_pos



# NOTE TO SELF: ANY ONTOLOGY LOOK-UPS SHOULD BE DONE BY DECOMPOSING FULL VERB COMPOUND -> MATCH FOR 'LET STAND' ETC.

def find_objects( triplet_list, verb, forced_tags, word_list, allverbs, search_for):
    for trip in triplet_list:
        if (trip[1] in ('dobj','iobj')) and trip[2][1].startswith('NN') and trip[0][0] == search_for:

            noun = trip[2][0]
            compound = noun

            # check that it does not occur in a nummod-relation        NOTE: BETTER TO CHECK NOT IN MEASURE-ONTOLOGY!!!                 
            is_a_measure = False
            for tri in triplet_list:
                if tri[1]== 'nummod' and (tri[0][0]==noun or tri[2][0]==noun):
                    is_a_measure = True
                    
            ##Check if it is a compound
            compound, forced_tags = find_compound( triplet_list, noun, forced_tags, word_list )
                    
            # Associate these nouns with the verb
            if not is_a_measure:
                allverbs[ verb ]['nouns'].append( compound )
                index = word_list.index( noun )
                forced_tags[index] = 'n'

            ########## Find conjuncts and their compounds
            allverbs, forced_tags = check_conjuncts( allverbs, verb, noun, triplet_list, forced_tags, word_list)

    return [forced_tags, allverbs]


def check_for_all_nmods(triplet_list, verb, forced_tags, word_list, allverbs, search_for ):
    covered_triplets = []
    search_key = search_for             #begin by looking for argument
    while search_key is not None:
        new_key_found = False
        for trip in triplet_list:  #loop over triplets to check if it forms part of nmod(search-key, noun)
            if (trip[1] in ('nmod')) and (trip[2][1].startswith('NN')) and (trip not in covered_triplets) and trip[0][0] == search_key:  #This fetches nmods of verbs and nmods of nmods, but the latter is not exhaustive!
                
                nmod = trip[2][0]   #the word is part of a nmod-relationship!
                covered_triplets.append(trip)   #don't revisit old triplets
                compound = nmod
                
                # check that it does not occur in a nummod-relation        NOTE: BETTER TO CHECK NOT IN MEASURE-ONTOLOGY!!!                 
                is_a_measure = False
                for tri in triplet_list:
                    if tri[1]== 'nummod' and (tri[0][0]==nmod or tri[2][0]==nmod):
                        is_a_measure = True
                        break
                if is_a_measure:
                    break

                ##Check if it is a compound
                compound, forced_tags = find_compound( triplet_list, nmod, forced_tags, word_list )
                
                # Associate these nouns with the verb
                allverbs[ verb ]['nouns'].append( compound )    #will either be nmod or nmod as part of compound
                index = word_list.index( nmod )
                forced_tags[index] = 'n'
                ########## Find conjuncts and their compounds
                #allverbs, forced_tags = check_conjuncts( allverbs, noun, triplet_list, forced_tags, word_list) #will probably mislead
                search_key = nmod
                new_key_found = True
                break

        if not new_key_found:
            search_key = None
    return [forced_tags, allverbs]

def check_for_in_using_patterns(tag_list, triplet_list, original, forced_tags, allverbs, word_list):
        #####
        # check for 'Using [electric mixer], [beat] [sugar]' pattern
        # and DO NOT include 'Using' but include beat
    if tag_list[0][0] in ('In','in','Using','using'):       
        comma_index = original.find(', ')                #Find index of comma
        remainder = original[comma_index + 2 , : ]
        first_space = remainder.find(' ')
        word_after_comma = original[ comma_index + 2 : comma_index + 2 + first_space ]
        index = word_list.index( word_after_comma )
        forced_tags[index] = 'v'    #tag it as a verb
        allverbs[ word_after_comma ] = { }     #and do whatever processing you mean to do
        allverbs[ word_after_comma ]['index'] = index
        allverbs[ word_after_comma ]['nouns'] = [ ]
        verb = word_after_comma

        ####### attach nouns etc. as appropriate (tools or such mentioned in first clause)
        forced_tags, allverbs = find_objects(triplet_list, verb, forced_tags, word_list, allverbs)      #not sure if this is necessary/misleading
        # note that pre-nouns of first clause will be picked up in 'neglected nouns'                

        #exclude 'Using' from actual verb-list
        forced_tags[0] = 'x'

    return [forced_tags, allverbs]
               


    ###########################################################################################################################################
def findverbs(original, tag_list, triplet_list, recipe_ings, ingredient_list, equipment_list, agg_list, action_list):                     
    #all_nouns = equipment_list + ingredient_list + agg_list
    allverbs = { }
    word_list = word_tokenize(original) #.split() #make sure tokenization corresponds to pos-tagger

##    print("FOR COMPARISON PURPOSES ------------------------------------")    
##    print(tag_list)
##    print("------------------------------------------------------------")
##    print(triplet_list)
##    #print(word_list)
##    print("------------------------------------------------------------")
##    
    ### Let the x entry hold annotations for what you've done with them.
    forced_tags = [None] * len(tag_list)
    
    ########## "In a bowl, whisk together" pattern
    forced_tags, allverbs = check_for_in_using_patterns(tag_list, triplet_list, original, forced_tags, allverbs, word_list)
    #marked first as 'x' and the first-verb-after-comma as 'v'
    
    for triplet in triplet_list:            #VERB-FINDING LOOP
        
        #the two kinds of parsers don't parse numbers the same
        if triplet[0][0]=='/' or triplet[2][0]=='/' or triplet[0][0][0].isdigit() or triplet[2][0][0].isdigit(): #This step could be moved one step down.
            continue
        
        for i in [0,2]:

            #for comparison-purposes, find the pos tag to the triplet-word
            nltk_pos = find_nltk_tag(triplet[i][0], tag_list)
            index = word_list.index( triplet[i][0] )
            tag = forced_tags[index]


            #we additionally check a word has not already been annotated 
            if triplet[i][1] in ('VB','VBP','VBG') and tag is None:     #simplest scenario: dep-parser tags it as verb

                verb = triplet[i][0]         #potential verb
                
                ############ PERFORM TESTS TO CHECK VERB-NESS ########################################################

                # CHECK
                if is_it_in_nouns(verb,recipe_ings,ingredient_list,equipment_list,agg_list) != "" and is_it_in_actions(verb, action_list) == "":       #sometimes the latter is wrong!!
                    forced_tags[index] = 'n'
                    continue

                # CHECK
                if verb is 'are':
                    forced_tags[index] = 'x'
                    continue

                # CHECK "just before serving" and "if using" issue
                if triplet[i][1] == 'VBG' and index > 0 and word_list[index - 1] not in ('Before','before','If','if'): #'after' should be ok
                    forced_tags[index] = 'x'
                    continue                    

                # CHECK
                #### Loop through list to check if this verb occurs in a relation of type ('want', 'VBP'), 'nsubj', ('you', 'PRP')).
                # if so, ignore! 
                for trip in triplet_list:
                    if trip[0][0] == verb and trip[1] == 'nsubj' and trip[2][0] == 'you':
                        forced_tags[index] = 'x'        #tag to ignore
                        # ALSO REMOVE ANY VERBS LINKED TO IT (through some kind of relation, e.g. xcomp or whatever #POTENTIALLY ALLOW CONJUNCTS???
                        for t in triplet_list:
                            if t[0][0] == verb and t[2][1].startswith('VB'):
                                ind = word_list.index(t[2][0])
                                forced_tags[ind] = 'x'
                            if t[2][0] == verb and t[0][1].startswith('VB'):
                                ind = word_list.index(t[0][0])
                                forced_tags[ind] = 'x'
                        continue

                # CHECK if "bring to simmer, boil", if so, ignore "bring"
                ## append triplet[1][0] because it is either 'simmer' or 'boil'
                ##(('bring', 'VBP'), 'advcl', ('simmer', 'VB')), (('simmer', 'VB'), 'mark', ('to', 'TO')).
                #if triplet[i][0] not in ('bring','Bring') and triplet[1]=='advcl':   #only consider first?                 # TO DO!!!!!!!!!!!!!!!!!!
                    ### do something


                #################################################### Settle for that it is a verb and make a dictionary entry                
                forced_tags[index] = 'v'
                allverbs[ verb ] = { }     
                allverbs[ verb ]['index'] = index
                allverbs[ verb ]['nouns'] = [ ]
                allverbs[ verb ]['full'] = None
                
                ####################### Check if it is a complex verb ###############################
                second_word = None
                for trip in triplet_list:
                    #first check for verb + particle
                    if trip[1]=='compound:prt' and trip[0][0] == verb and trip[2][1] == 'RP':
                        allverbs[ verb ]['full'] = verb + " " + trip[2][0]
                        idx = word_list.index(trip[2][0])
                        forced_tags[idx]='w'                    #changed from 'v'
                        second_word = trip[2][0]
                        break                           #might as well break immediately
                        
                    # protect against false positives  
                    if (trip[1]=='ccomp' or trip[1]=='xcomp') and trip[0][0] == verb and trip[2][1]=='VB': #false pos?

                        #check if nltk-tags agree that it is a verb otherwise break
                        false_positive = False      
                        for tpl in tag_list:
                            if tpl[0] == trip[2][0] and tpl[1] is not 'VB':
                                false_positive = True
                                break
                        if false_positive:
                            break

                        #false positives checked for, now check if we are to put " to " in between... mark(blend, to)?
                        for t in triplet_list:
                            if t[1]=='mark' and t[0][0] == trip[2][0] and t[2][0]=='to':
                                allverbs[ verb ]['full'] = verb + " to " + trip[2][0] #"Beat to blend"
                            else:   
                                allverbs[ verb ]['full'] = verb + " " + trip[2][0]
                                
                        idx = word_list.index(trip[2][0])
                        forced_tags[idx] = 'w'              #changed from 'v'
                        second_word = trip[2][0]
                        
                        break                           #might as well break immediately

                ##################################################### find objects (make more efficient later)
                forced_tags, allverbs = find_objects( triplet_list, verb, forced_tags, word_list, allverbs, verb )
                forced_tags, allverbs = check_for_all_nmods( triplet_list, verb, forced_tags, word_list, allverbs, verb )
                
                # pursue other verb-component
                if second_word:
                    forced_tags, allverbs = find_objects(triplet_list, verb, forced_tags, word_list, allverbs, second_word)
                    forced_tags, allverbs = check_for_all_nmods(triplet_list, verb, forced_tags, word_list, allverbs, second_word )
                

            elif is_it_in_actions(triplet[i][0], action_list) != "" and is_it_in_nouns(triplet[i][0],recipe_ings, ingredient_list, equipment_list, agg_list) == ""  and tag is None:     #If in action-list but not in list of nouns, regard it as verb
                
                verb = triplet[i][0]         #potential verb
                
                #################################################### Make a dictionary entry                
                forced_tags[ index ] = 'v'
                allverbs[ verb ] = { }     
                allverbs[ verb ]['index'] = index
                allverbs[ verb ]['nouns'] = [ ]
                allverbs[ verb ]['full'] = None
                forced_tags, allverbs = find_objects(triplet_list, verb, forced_tags, word_list, allverbs, verb)
                forced_tags, allverbs = check_for_all_nmods(triplet_list, verb, forced_tags, word_list, allverbs, verb )

                #### do any processing

            #elif triplet[i][1] == 'VBD':               #TODO

                #check if present tense equals past tense, e.g. beat/beat

                #### do any processing
                
            #elif nltk_pos in ('VB','VBP','VBG'):        #NLTK labelled it as a verb
            #    if i==2 and triplet[0][1] in ('VBZ','VBD') and triplet[2][1] == 'RB' and triplet[1] == 'advmod':               # TO DO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                ##process verb

            else:
                continue

    ##ASSOCIATE NEGLECTED NOUNS WITH CLOSEST VERBS ( note that we do this after analysing all dependencies)

    i = 0
    for tupl in tag_list:

        index = word_list.index( tupl[0] )
        tag = forced_tags[ index ]

        # TEST IF IT IS A NEGLECTED NOUN
        if (tupl[1].startswith('NN') or is_it_in_nouns(tupl[0], recipe_ings, ingredient_list, equipment_list, agg_list) != "" ) and tag is None: #HAVE MORE SOPHISTICATED TESTS, LEMMATISE
            noun = tupl[0]
            compound, forced_tags = find_compound( triplet_list, noun, forced_tags, word_list ) #no need to check for conjuncts

            # If closest verb found, associate it with it
            closest_verb, forced_tags = find_closest_verb(forced_tags, word_list, tag_list, tupl)
            
            if closest_verb in allverbs.keys():
                allverbs[ closest_verb ]['nouns'].append( compound )
                index = word_list.index( noun )
                forced_tags[index] = 'n'

    ########### FIND CARDINALITY (actually, embed this somehow)

    card_dict = extract_cardinals( forced_tags, tag_list )
    for k in card_dict.keys():
        allverbs[k]['cardinalities'] = card_dict[k]
    #acts_with_numbers = extract_cardinals(triplet_list, action_list)


    #######################################################################################################
    #######   strip away nouns that are not in ontology. ( CLEANUP). Replace noun by corresponding ontology entry.
                
    for k in allverbs.keys():
        if k not in card_dict.keys():
            allverbs[k]['cardinalities']=[]
        
        stripping = []
        for ind in range(0,len(allverbs[ k ]['nouns'])):
            entr = is_it_in_nouns(allverbs[k]['nouns'][ind], recipe_ings, ingredient_list, equipment_list, agg_list)
            if entr != "":
                stripping.append(entr)

        allverbs[ k ]['nouns_stripped'] = stripping      #replace original noun-list with the ontology-cleaned one.
        key_entr = is_it_in_actions(k, action_list)
        if key_entr != "":
            allverbs[key_entr] = allverbs.pop(k)
                
    ###################################################################################            

    return allverbs



#LATER, PERFORM A 'CLEANUP' OF ALL VERB'S NOUNS TO CHECK THAT THEY ARE IN ONTOLOG, AFTER DECOMPOSING!!!!!!!
#discard parts not in ontology!!!!
#Even if the dobj object is neither an ingredient nor aggregate include it and annotate using text.
#For example, Reduce the speed to medium-low has speed as object and medium-low as nmod.

#Sometimes the sentence is not very self-contained and inappropriate for sentence-by-sentence analysis.
#For example: Whisk first 5 ingredients in small bowl.
#Discard nouns that are not in aggregate/ingredient ontology or recipe-specific ingredient-list.
#For example, the above sentence would only retain bowl.
