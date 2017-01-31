import nltk
import pickle
from nltk.parse.stanford import StanfordDependencyParser
from nltk import word_tokenize
from sentenceparser import parse, read_inst_from_recipe, parse_text_into_sents
from sentenceparser import read_inst_from_recipe
from tripletprocessing import findverbs
from read_ingredients import read_ingredients
from ontologyhandler import read_ing_list, read_in_ontologies
import json
from prep import sentence_dict, ingredient_list, equipment_list, agg_list, action_list, new_ingredients, ingredients, recipe_ings

#from extract_cardinals import extract_cardinals
#from ontologyhandler import ''''

from nltk.tag import StanfordPOSTagger
st = StanfordPOSTagger('english-bidirectional-distsim.tagger')
import re

path_to_jar = r'C:\Users\Lovisa\Downloads\stanford-corenlp-full-2016-10-31\stanford-corenlp-full-2016-10-31\stanford-corenlp-3.7.0.jar'
path_to_models_jar = r'C:\Users\Lovisa\Downloads\stanford-corenlp-full-2016-10-31\stanford-corenlp-full-2016-10-31\stanford-corenlp-3.7.0-models.jar'
dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)





############################# MAIN ################################

#sentence_dict = parse()             # TO RUN ACTUAL FILES
##sentence_dict = parse_text_into_sents( read_inst_from_recipe('apricot_almond_layer_cake.txt'))
##ingredient_list, equipment_list, agg_list, action_list = read_in_ontologies()
##new_ingredients = []
##ingredients, new_ingredients, recipe_ings  = read_ingredients('apricot_almond_layer_cake.txt', ingredient_list , new_ingredients)
# 'ingredients' is the dictionary
file2 = open('sentence_dict.pkl','rb')
sentence_dict = pickle.load(file2)
file2.close()
file2 = open('ingredient_list.pkl','rb')
ingredient_list = pickle.load(file2)
file2.close()
file2 = open('equipment_list.pkl','rb')
equipment_list = pickle.load(file2)
file2.close()
file2 = open('agg_list.pkl','rb')
agg_list = pickle.load(file2)
file2.close()
file2 = open('action_list.pkl','rb')
action_list = pickle.load(file2)
file2.close()
file2 = open('ingredients.pkl','rb')
ingredients = pickle.load(file2)
file2.close()
file2 = open('new_ingredients.pkl','rb')
new_ingredients = pickle.load(file2)
file2.close()
file2 = open('recipe_ings.pkl','rb')
recipe_ings = pickle.load(file2)
file2.close()

#f = open('output.txt','w')
#sentence_dict = parse_text_into_sents( text )
for key in sentence_dict.keys():

    orig = sentence_dict[key]["original"]

    ############ APPENDING "WE" AS A DIRTY HACK #############################################
    tag_list = nltk.pos_tag(orig.split())       #should I not use word_tokenize? nah irrelevant
    if tag_list[0][1] in ('NN','NNP','VB'):    #VB since st tagger returns it as VB 
        changed = "We " + orig[0].lower() + orig[1:]
        if orig[0].isalpha():
            changed = "We " + orig[0].lower() + orig[1:]
        else:
            changed ="We " + orig[1].lower() + orig[2:]
        orig = changed
    ##########################################################################################
    print( "-----------------------------------------------------------------------------")
    print("ORIGINAL INSTRUCTION: " + orig)
    
    result = dependency_parser.raw_parse(orig)
    dep = result.__next__()
    tag_list = nltk.pos_tag(word_tokenize(orig))        #The one with We prepended
    print(str(tag_list))
    triplet_list = list(dep.triples())              #Parsing function takes tag_list and triplet_list as arguments

    

    #f.write( '------------------------------------------------------- \n' )
    #f.write( orig + '\n' )
    #f.write( '------------------------------------------------------- \n' )
    print( "-----------------------------------------------------------------------------")
    allverbs = findverbs(orig, tag_list, triplet_list, recipe_ings, ingredient_list, equipment_list, agg_list, action_list)
    sentence_dict[key]['allverbs'] = allverbs
    for key in allverbs.keys():
        if allverbs[ key ]['full'] is not None:
            #f.write(allverbs[ key ]['full'] +':\n')
            print( allverbs[ key ]['full'] +':')
        else:
            #f.write(key + '\n')
            print( key )
        #f.write ( str(allverbs[ key ]['nouns_stripped'])+'\n' )
        #print (allverbs[ key ]['nouns'] )
        #print ("Stripped")
        print(allverbs[key]['nouns_stripped'])
        print(str(allverbs[key]['cardinalities']))
    
    print('END----------------------------------------------------------------------------')
f = open('webdev\output.txt','w')
recipe_dict = json.dumps(sentence_dict) #recipe_dict is a string
json = json.loads(recipe_dict)
f.write(json)
f.close()

#f.close()


###
###
###
###
###
##### TEST CARDINALITY
##
##sentence_dict = parse_text_into_sents( read_inst_from_recipe('frozen_passion_fruit_meringue_cake.txt'))
##ingredient_list, equipment_list, agg_list, action_list = read_in_ontologies()
##new_ingredients = []
###ingredients, new_ingredients, recipe_ings  = read_ingredients('apricot_almond_layer_cake.txt', ingredient_list , new_ingredients)
### 'ingredients' is the dictionary
##
##for key in sentence_dict.keys():
##    orig = sentence_dict[key]["original"]
##
##    ############ APPENDING "WE" AS A DIRTY HACK #############################################
##    tag_list = nltk.pos_tag(orig.split())       #should I not use word_tokenize? nah irrelevant
##    if tag_list[0][1] in ('NN','NNP','VB'):    #VB since st tagger returns it as VB
##        if orig[0].isalpha():
##            changed = "We " + orig[0].lower() + orig[1:]
##        else:
##            changed ="We " + orig[1].lower() + orig[2:]     #otherwise, first is probs blank
##        sentence_dict[key]["original"] = changed
##        orig = changed
##    ##########################################################################################
##    result = dependency_parser.raw_parse(orig)
##    dep = result.__next__()
##    tag_list = nltk.pos_tag(word_tokenize(orig))        #The one with We prepended
##    triplet_list = list(dep.triples())              #Parsing function takes tag_list and triplet_list as arguments
##
##    
##    print( "-----------------------------------------------------------------------------")
##    print("ORIGINAL INSTRUCTION: " + orig)
##    print( "-----------------------------------------------------------------------------")
##    #awn = extract_cardinals(triplet_list, action_list)
##    print(str(triplet_list))
##    print( "-----------------------------------------------------------------------------")
##    print(str(tag_list))
##    print( "-----------------------------------------------------------------------------")
##    #for key in awn:
##    #    print( key )
##    #    print( str(awn[key]))
##    
##    print('END----------------------------------------------------------------------------')
