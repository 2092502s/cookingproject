from difflib import SequenceMatcher

def listingredients():
	ing_list = []
	with open('ingredients.txt', 'r') as f:
		for line in f:
			linelist = line.split(':',1)
			ing_list.append(linelist[0])
			#print(linelist[0])
	return ing_list

def parseingredients( recipefilename ):
	#this dictionary is file-specific...
	ingredients = {}
	equipment = ""
	with open('baking_recipes/' + recipefilename,'r') as f:
	    for line in f:
	        ##Check which basic section it belongs to
	        if "INGREDIENTS" in line:
	            continue
	        if "PREPARATION" in line:
	            break
	        ##Check if it concerns special equipment
	        if "Special equipment:" in line:
	            equipment = line[17:]

	        ##Ignore any blank lines
	        line = line.strip()
	        if not line:
	            continue

	        section = None
	        ##Subheading
	        wordlist = line.split()
	        if line.endswith(":") or not wordlist[0][0].isdigit():          #it's not special equipment
	            section = line
	            continue

	        ##Normal ingredient line - parse it
	        

	        ##If the second word is an integer, it belongs to the quantity as well.
	        if wordlist[1][0].isdigit():
	            ingr_name = ' '.join(wordlist[3:])
	            ingredients[ingr_name]= {}
	            ingredients[ingr_name]['Quantity']= ' '.join(wordlist[:2])
	            ingredients[ingr_name]['Measure']= wordlist[2]
	        else:
	            ingr_name = ' '.join(wordlist[2:])
	            ingredients[ingr_name]={}
	            ingredients[ingr_name]['Quantity']= wordlist[0]
	            ingredients[ingr_name]['Measure']= wordlist[1]
	            
	        #print("Ingredient name is " + ingr_name)
	        #print("Quantity is " + ingredients[ingr_name]['Quantity'])
	        #print("Measure is " + ingredients[ingr_name]['Measure'])
	        ingredients[ingr_name]['Specifics'] = ingr_name         #Just provisionally...
	        
	        if section:
	                ingredients[ingr_name]['Section'] = section

	f.close()
	return [ingredients, equipment]

def find_best_candidate( ing_list, recipe_dict ):

        original_names = []
        new_names = []
        ind_index = []
        best_ratios = [0.0] * len(recipe_dict.keys())

        #Initialise a list of format
        # [description given by recipe, currently best candidate ingredient, index for that ingredient in ing_list ]
        i = 0
        for ing in recipe_dict.keys():
                #best_candidates[i,0] = ing     #save description given by recipe
                #print(best_candidates)
                #print(ing)
                original_names.append(ing)
                
                key_words = ing.split()         #split into individual words
                for word in key_words:      #compare every word in the description with list
                        best_index = 0
                        for j in range(0,len(ing_list)):      #loop over every word in the ontology
                ##### Modification where I instead check word for word
                                cand_split = ing_list[j].split()
                                for cand in cand_split:
                                        sim_ratio = SequenceMatcher(None, word, cand).ratio()   #may not work if small subset???          
                                        if sim_ratio > best_ratios[i]:                  #keep track of the best match
                                                best_ratios[i] = sim_ratio
                                                best_index = j
                new_names.append( ing_list[ best_index ] )
                ind_index.append( best_index ) #store index of winning candidate
                #print(best_candidates)
                #print("NEW ITERATION")
                i += 1
               
                
        #print(best_candidates[i-1][0] + " became " + best_candidates[i-1][1])
        for k in range(0, len(recipe_dict.keys())):
                print(original_names[k] + " became " + new_names[k])
        #print(best_candidates)
        return [original_names, new_names, ind_index, best_ratios]

def parse_ingredient_name(original_names, new_names, ind_index, best_ratios, recipe_dict, ing_list):

        for index in range(len(best_ratios)):
                #print(best_ratios[index])
                if best_ratios[index] > 0.1:                            #similarity-cutoff-point
                        recipe_dict[new_names[index]] = recipe_dict.pop( original_names[index])

        #NOTE: for the future, I should write into a file entries that don't match!
        return recipe_dict
                        
##################################### THIS IS WHERE MAIN FUNCTION STARTS ###############################
ing_list = listingredients()
#Should work correctly
recipe_dict, equipment = parseingredients( "best_cocoa_brownies.txt" )                  #Should work correctly
#print(recipe_dict)
original_names, new_names, ind_index, best_ratios = find_best_candidate( ing_list, recipe_dict )

#for cand in best_candidates:
#        print(cand[1])

#print(best_candidates)

##for i in range(len(best_candidates)):
##    if best_candidates[i][0] not in recipe_dict.keys():
##        print(best_candidates[i][0] + " not found")
##    else:
##        print(best_candidates[i][0] + " found")
recipe_dict = parse_ingredient_name( original_names, new_names, ind_index, best_ratios, recipe_dict, ing_list )

#for ing in recipe_dict.keys():
#        print(ing)

##
##for ing in ingredients.keys():
##
##    print("Ingredient name: " + ing)
##    print("Quantity is: " + ingredients[ing]['Quantity'])
##    print("Measure is: " + ingredients[ing]['Measure'])
##    if section:
##            print("Section is: " + ingredients[ingr_name]['Section'])
