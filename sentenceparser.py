import nltk.data
import re
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
file_names = [ 'apricot_almond_layer_cake.txt',
               'best_cocoa_brownies.txt',
               'chewy_coconut_chocolate_chip_cookies.txt',
               'chocolate_chip_coffee_cake.txt',
               'chocolate_cream_cheese_cupcakes.txt',
               'chocolate_peanut_butter_cake.txt',
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

#Reads from file into string
def read_inst_from_recipe( filename ):
    readstart = False
    inst_string = ""
    with open('baking_recipes/' + filename, 'r') as f:
        for line in f:
            if "PREPARATION" in line:
                readstart = True
                continue            
            if not readstart:
                continue
            inst_string += line         #No need to exclude blank lines at this step, I think
    return inst_string  

#This function takes a raw text and parses into sentences with the following functions:

#Remove leading ordinals
def parse_text_into_sents( text ):
    text.replace('...','.')
    sentences = sent_detector.tokenize( text.strip() ) #Strip whitespace from beginning and end
    o = re.compile(r'(\d)+(\.)')
    for s in sentences:

        # Remove new-line characters
        sentences[sentences.index(s)] = s.strip('\n').replace("/", "//").replace(" ,", ",").replace('  ',' ')
       
        # Remove leading ordinals
        match = re.match( o,s)    #Match() checks for a match only in the beginning
        if match:
            #sentences[sentences.index(s)] = s[match.start():]   #I think this is unnecessary as parser makes sentence of ordinal
            sentences.remove(s)                 
            continue
    p = re.compile(r'\([^)]*\)')
    q = re.compile(r'(\d)+(\s)+(\d)+(/)+(\d)+')
    for s in sentences:
        # Delete parantheses contents
        #match1 = re.match(p, s)
        if '(' in s and ')' in s:
            sentences[sentences.index(s)] = re.sub(p, '', s).replace('  ',' ')
            #print("Deleted paranthesis!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        # Handle slash-signs by changing numerator
        match2 = re.match( q, s)
        if match2:
            new_num = int(s[match2.start()]) * int(s[match2.start()+2])
            sentences[sentences.index(s)] = s[:match2.start()-1] + new_num + s[match2.start()+3:]
            #print("NEW NUMERATOR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    for s in sentences:
        if len(s) <= 1:
            sentences.remove(s)
            continue
        if s[0] == '(' or s[len(s)-1] == ')':   #Because sometimes brackets contain periods
            sentences.remove(s)
            continue          

    for s in sentences:

        # Take care of semi-colons - separate them into separate sentences
        twosome = s.split(';',1)
        if len(twosome) == 2:
            index = sentences.index(s)
            sentences[index] = twosome[0] + "."
            sentences.insert(index+1, twosome[1].capitalize() )

    for s in sentences:

        # Take care of colons - let it signal the end of a header
        twosome = s.split(':',1)
        if len(twosome) == 2:
            index = sentences.index(s)
            sentences[index] = twosome[0] + " :"
            sentences.insert(index+1, twosome[1] )
    #for s in sentences:
        #print(s)
        #print(" ")
        
    sentence_dict = { }
    i = 1
    for s in sentences:
        sentence_dict[i] = {}
        sentence_dict[i]["original"] = s
        sentence_dict[i]["orig"] = s            #will always remain unmodified
        i += 1
    #print( sentence_dict )
    return sentence_dict

def parse():
    for fn in file_names:
        parse_text_into_sents( read_inst_from_recipe( fn ) )
