import pickle
import nltk
from nltk.parse.stanford import StanfordDependencyParser
from nltk import word_tokenize
from sentenceparser import parse, read_inst_from_recipe, parse_text_into_sents
from sentenceparser import read_inst_from_recipe
from tripletprocessing import findverbs
from read_ingredients import read_ingredients
from ontologyhandler import read_ing_list, read_in_ontologies


sentence_dict = parse_text_into_sents( read_inst_from_recipe('best_cocoa_brownies.txt'))
ingredient_list, equipment_list, agg_list, action_list = read_in_ontologies()
new_ingredients = []
ingredients, new_ingredients, recipe_ings  = read_ingredients('best_cocoa_brownies.txt', ingredient_list , new_ingredients)

afile = open('sentence_dict.pkl','wb')
pickle.dump(sentence_dict, afile)
afile.close()

afile = open('ingredient_list.pkl','wb')
pickle.dump(ingredient_list, afile)
afile.close()

afile = open('equipment_list.pkl','wb')
pickle.dump(equipment_list, afile)
afile.close()

afile = open('agg_list.pkl','wb')
pickle.dump(agg_list, afile)
afile.close()

afile = open('action_list.pkl','wb')
pickle.dump(action_list, afile)
afile.close()

afile = open('ingredients.pkl','wb')
pickle.dump(ingredients, afile)
afile.close()

afile = open('new_ingredients.pkl','wb')
pickle.dump(new_ingredients, afile)
afile.close()

afile = open('recipe_ings.pkl','wb')
pickle.dump(recipe_ings, afile)
afile.close()
