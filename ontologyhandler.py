#from actions import action_list
from nltk.stem import WordNetLemmatizer
wl = WordNetLemmatizer()

### should I sort?

#lemmatises and will thus take longer. Is only meant to be read in once.
def prepare_ontology_files():           

        filenames_raw = ['ontology/ingredients_raw.txt','ontology/equipment_raw.txt','ontology/aggregates_raw.txt']
        filenames = ['ontology/ingredients.txt', 'ontology/equipment.txt', 'ontology/aggregates.txt']
        for file_idx in range(0,len(filenames_raw)):
                with open(filenames_raw[file_idx], 'r' ) as f:
                        with open(filenames[file_idx], 'w+') as fi:
                             for line in f:
                                     stripped = line.strip()
                                     lemma = wl.lemmatize(stripped).lower()     #dependency issue?
                                     fi.write( lemma + '\n' )
                fi.close()
                f.close()
        return 

#serves to read in a file as a

def read_ing_list():
	ingredient_list = []
	with open('ontology/ingredients.txt', 'r') as f:
		for line in f:
			linelist = line.strip().split()
			ingredient_list.append(linelist)   
	f.close()
	return ingredient_list

def read_agg_list():
	agg_list =  [ ]
	with open('ontology/aggregates.txt', 'r') as f:
		for line in f:
			linelist = line.strip().split()
			agg_list.append(linelist)    
	f.close()
	return agg_list

def read_action_list():
	action_list = [ ]
	with open('ontology/actions.txt', 'r') as f:
		for line in f:
			linelist = line.strip().split()
			action_list.append(linelist)    
	f.close()
	return action_list

def read_equipment_list():
	equipment_list = []
	with open('ontology/equipment.txt', 'r') as f:
		for line in f:
			linelist = line.strip().split()
			equipment_list.append(linelist)    
	f.close()
	return equipment_list

def read_in_ontologies():
        ingredient_list = read_ing_list()
        equipment_list = read_equipment_list()
        agg_list = read_agg_list()
        action_list = read_action_list()
        return [ingredient_list, equipment_list, agg_list, action_list ]


def is_it_in_actions( word, action_list ):
        lemma = wl.lemmatize( word ).lower()
        lemmalist = lemma.split()
        cur_long_entry = ""
        cur_long_entry_len = 0
        for w in action_list:           #iterate over lists
                ##
                entry = ""
                if len(w) > 0:
                        if w[0] == lemmalist[0]:      #compare the last words for a match
                                #print("MATCH" + w[-1])
                                entry = w[0]         #initialise "entry" as last word and see if you can extend it      
                                for i in range(1, len(w)): #iterate over words
                                        if w[i] in lemmalist:
                                                entry = entry + " " + w[i]
                if len(entry) > cur_long_entry_len:
                        cur_long_entry_len = len(entry)
                        cur_long_entry = entry
        ##
        return cur_long_entry

def is_it_in_recipe_ings( word, recipe_ings ):
        if word.endswith('s'):
                word = word[:-1]
        lemma = wl.lemmatize( word ).lower()
        lemmalist = lemma.split()
        cur_long_entry = ""
        cur_long_entry_len = 0
        for w in recipe_ings:           #iterate over the word-lists in the ontology
                ##
                entry = ""
                if len(w) > 0:
                        if w[-1] == lemmalist[-1]:      #compare the last words for a match
                                #print("MATCH" + w[-1])
                                entry = w[-1]         #initialise "entry" as last word and see if you can extend it      
                                for i in reversed(range(0, len(w)-1)): #iterate over words
                                        if w[i] in lemmalist:
                                                entry = w[i] + " " + entry
                if len(entry) > cur_long_entry_len:
                        cur_long_entry_len = len(entry)
                        cur_long_entry = entry
        ##
        return cur_long_entry

def is_it_in_ing_ont( word, ingredient_list):
        if word.endswith('s'):
                word = word[:-1]
        lemma = wl.lemmatize( word ).lower()
        lemmalist = lemma.split()
        cur_long_entry = ""
        cur_long_entry_len = 0
        for w in ingredient_list:           #iterate over lists
                ##
                entry = ""
                if len(w) > 0:
                        if w[-1] == lemmalist[-1]:      #compare the last words for a match
                                #print("MATCH" + w[-1])
                                entry = w[-1]         #initialise "entry" as last word and see if you can extend it      
                                for i in reversed(range(0, len(w)-1)): #iterate over words
                                        if w[i] in lemmalist:
                                                entry = w[i] + " " + entry
                if len(entry) > cur_long_entry_len:
                        cur_long_entry_len = len(entry)
                        cur_long_entry = entry
        ##
        return cur_long_entry

def is_it_in_equip( word, equipment_list):
        if word.endswith('s'):
                word = word[:-1]
        lemma = wl.lemmatize( word ).lower()
        lemmalist = lemma.split()
        cur_long_entry = ""
        cur_long_entry_len = 0
        for w in equipment_list:           #iterate over lists
                ##
                entry = ""
                if len(w) > 0:
                        if w[-1] == lemmalist[-1]:      #compare the last words for a match
                                #print("MATCH" + w[-1])
                                entry = w[-1]         #initialise "entry" as last word and see if you can extend it      
                                for i in reversed(range(0, len(w)-1)): #iterate over words
                                        if w[i] in lemmalist:
                                                entry = w[i] + " " + entry
                if len(entry) > cur_long_entry_len:
                        cur_long_entry_len = len(entry)
                        cur_long_entry = entry
        ##
        return cur_long_entry

def is_it_in_aggs( word, agg_list ):
        if word.endswith('s'):
                word = word[:-1]
        lemma = wl.lemmatize( word ).lower()
        lemmalist = lemma.split()
        cur_long_entry = ""
        cur_long_entry_len = 0
        for w in agg_list:           #iterate over lists
                ##
                entry = ""
                if len(w) > 0:
                        if w[-1] == lemmalist[-1]:      #compare the last words for a match        
                                entry = w[-1]         #initialise "entry" as last word and see if you can extend it      
                                for i in reversed(range(0, len(w)-1)): #iterate over words
                                        if w[i] in lemmalist:
                                                entry = w[i] + " " + entry
                if len(entry) > cur_long_entry_len:
                        cur_long_entry_len = len(entry)
                        cur_long_entry = entry
        ##
        return cur_long_entry

def is_it_in_nouns( word, recipe_ings, ingredient_list, equipment_list, agg_list ):
        entry = ""
        in_rec_ings = is_it_in_recipe_ings( word, recipe_ings )
        #print('rec_ings returns ' + in_rec_ings )
        if in_rec_ings != "":
                return in_rec_ings
        in_ing_ont = is_it_in_ing_ont( word, ingredient_list )
        #print('ing_ont returns ' + in_rec_ings )        
        if in_ing_ont != "":
                return in_ing_ont
        in_equip = is_it_in_equip( word, equipment_list )
        if in_equip != "":
                return in_equip
        in_aggs = is_it_in_aggs( word, agg_list )
        if in_aggs != "":
                return in_aggs
        #
        return entry

################ MAIN-section for testing

prepare_ontology_files()
ingredient_list, equipment_list, agg_list, action_list = read_in_ontologies()

     

