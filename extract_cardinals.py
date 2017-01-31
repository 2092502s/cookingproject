from ontologyhandler import is_it_in_actions
from nltk.stem import WordNetLemmatizer
wl = WordNetLemmatizer()


units = ['cup','cups','sheet','sheets','degrees','third','batches','batch',
         'tablespoonful','additions','addition','inch','inches','seconds',
         'second','stroke','tablespoons','tbsp','teaspoon','tsp','minutes',
         'hour','hours','minute','squares','strokes']

#def extract_cardinals(verb_word, triplet_list, action_list):

    #potentially perilous assumption: associated CDs will be spatially before next verb word
    
    #obtain list of all verbs found so far

    #find the index that they're at it the tag-list

    #tag them as "key" in a code-list of same length as tokenized string

    #check intervening word in tag-list if they're CD.

    #boldly assume next-coming word is the unit
    #PROBLEM: MAY BE A COMPOUND WORD? Have a unit ontology? incl. 'fourth', 'fifth'...
    #are units always single words?
    #note - maybe it's followed by another CD, in that case remove // and concatenate with ' '
    # 1 1//3
    #and let the following be the unit.
    #problem: "1 heaping tablespoonful" -may be worth checking the next two-coming words
    #ONLY take the next word if the CD word isn't a mix of alpha and numerical

    #allow several cardinalities per verb "Beat in remaining 1//4 cup sugar, 1 tablespoon at a time."
    
def extract_cardinals( forced_tags, tag_list ):

    card_dict = {} 

    for i in range(0,len(tag_list)):    #loop over all tuples and getch their tags
        tag = forced_tags[i]
        if tag == 'v':                  #for each verb...
            key = tag_list[i][0]
            card_dict[ key ] = []       #prepare an empty list entry

            j = i + 1                   #loop over remainder of list
            while j < len(tag_list):

                skipahead = False
                
                if forced_tags[j]=='v':     #next verb reached without any cardinality detected,
                    break                   #so search no further.
                
                ##check if cardinality
                if tag_list[j][1]=='CD':
                    
                    card_string = tag_list[j][0].replace('//','/')
                    unit_list = []
                    
                    if (j+1)<len(tag_list) and tag_list[j+1][0] in ('to','or'):    #risk for index out of bounds
                        card_string = card_string + ' ' + tag_list[j+1][0] + ' ' + tag_list[j+2][0].replace('//','/')
                        if (j+2) < len(tag_list):
                            unit_list.append( tag_list[j+2][0])                        
                        if (j+3) < len(tag_list):
                            unit_list.append(tag_list[j+3][0])
                        skipahead = True
                        
                    elif (j+1)<len(tag_list) and tag_list[j+1][1]=='CD':
                        card_string = card_string + ' ' +  tag_list[j+1][0].replace('//','/')
                        if (j+2) < len(tag_list):
                            unit_list.append( tag_list[j+2][0])
                        if (j+3) < len(tag_list):
                            unit_list.append(tag_list[j+3][0])
                        skipahead = True

                    elif card_string[-1].isalpha() and card_string[0].isnumeric():       #assume this means it's temperature
                        card_dict[key].append( card_string ) #no need to append a unit
                        
                    elif (j+1)<len(tag_list):
                        unit_list.append(tag_list[j+1][0])
                        if (j+2)<len(tag_list):
                            unit_list.append(tag_list[j+2][0])
                        skipahead = True
                        
                    for measure_word in unit_list:
                        if measure_word in units:
                            card_dict[key].append ( card_string + " " + measure_word )  #discard entry completely otherwise
                            break
                        
                if skipahead:
                    j = j+3
                else:
                    j = j+1

                    ##check unit-ontology and concatenate                    
        word = tag_list[i][0]  #
        
    return card_dict        


##def extract_cardinals(triplet_list, action_list):
##
##    acts_with_numbers = { }
##    acts_with_numbers[ 'verbless' ] = []
##    found_cardinals = []
##    for triplet in triplet_list:            #Look for a cardinal number
##        which = 1
##        other = 1
##        if triplet[0][1] == 'CD' and triplet[0][0] not in found_cardinals: #We don't want to relaunch search on same number
##            which = 0
##            other = 2
##        if triplet[2][1] == 'CD' and triplet[2][0] not in found_cardinals:
##            which = 2
##            other = 0
##        if which is not 1:                  #A new cardinal number has been found...
##            #print("found cd: " + triplet[which][0])
##            found_cardinals.append ( triplet[which][0] )
##            
##            otherword = triplet[other][0]
##
##            #Is the other one a verb? If so, add it as key to dict and move immediately forward.
##            if triplet[other][1] in ('VB','VBP','VBG')  or is_it_in_actions(triplet[other][0], action_list):       #e.g. preheat + 325F                
##                acts_with_numbers[ wl.lemmatize( otherword ).lower() ] = triplet[which][0]
##                #print("Found verb immediately! " + otherword)
##                
##            else:
##                unit = ""                       
##                foundverb = False
##                if triplet[1] == 'nummod' or triplet[1] == 'nmod' or triplet[1] == 'compound': #These usually indicate units, e.g.('one', 'CD'), 'nmod', ('time', 'NN') ('hour', 'NN'), 'compound', ('1', 'CD')
##                    unit = otherword
##                    ## TODO:check if unit is in ingredients-list,
##                    # so that it is not something useless like "one time"           #Note: Im not sure if it's exhaustive
##                i = 0
##                length = len(triplet_list)
##                verb_cand = otherword
##                #print("first cand is " + verb_cand)
##                visited = []        #save indices of explored triples
##                verbs = []
##                while i < length:                #Do at most one search per triple
##
##                    #Firstly, do a check if any is accompanied by a verb (best case scenario)
##                    for trip in triplet_list:
##                        if triplet_list.index(trip) in visited:     #dont explore visited ones any further. This wont ever be entered.
##                            continue
##                        if ( trip[2][0] == verb_cand and (trip[0][1] in ('VB','VBP','VBG') or is_it_in_actions(trip[0][0],action_list)))):
##                            acts_with_numbers[ trip[0][0] ] = triplet[which][0] + " " + unit
##                            foundverb = True
##                            verbs.append( trip[0][0] ) 
##                            #print("Found verb! " + trip[0][0])
##                            continue
##                        if (trip[0][0] == verb_cand and (trip[2][1] in ('VB','VBP','VBG')  or is_it_in_actions(trip[2][0],action_list)))):                          
##                            acts_with_numbers[ trip[2][0] ] = triplet[which][0] + " " + unit
##                            foundverb = True
##                            verbs.append( trip[0][0] ) 
##                            #print("Found verb! " + trip[2][0])
##                            continue  #break out of for-loop
##                        
##                    if foundverb:   #once verb has been found, we can break while-loop as well
##                        break
##                    #If first search was successful, this won't be entered, so check for any instance of candidate
##                    j = 0
##
##                    #FOR-LOOP MEANT FOR CHANGING CANDIDATE WORD
##                    for trip in triplet_list:
##                        if triplet_list.index(trip) in visited:     #dont explore visited ones any further
##                            continue
##                        if (trip[0][0] == verb_cand):     #verb not found yet, so re-launch search on the other one
##                            verb_cand = trip[2][0] #look up the other word
##                            visited.append( triplet_list.index(trip) )     #pop the triple just visited
##                            i += 1
##                            #print("changed candidate to " + trip[2][0])
##                            break
##                            
##                        elif (trip[2][0] == verb_cand):
##                            verb_cand = trip[0][0]
##                            visited.append( triplet_list.index(trip) )     ##pop the triple just visited
##                            i += 1
##                            #print("changed candidate to " + trip[0][0])
##                            break
##                        else:                               #no more instance of current search word found
##                            j += 1
##                            continue
##                        
##                    if j == len(triplet_list):  #dead-end with verb_cand, no point in continuing
##                        break
##
##                        
##                if foundverb == False:
##                    acts_with_numbers[ 'verbless' ].append( triplet[which][0] + " " + unit)
##
##
##    return acts_with_numbers #requires post-processing to associate the action
##                            #keys with those gathered in the action-extraction
