### little trial
import nltk
from nltk.tag import StanfordPOSTagger
st = StanfordPOSTagger('english-bidirectional-distsim.tagger')
original = "In a medium bowl, whisk together the flour, oats, coconut, baking soda, and salt."

tag_list = st.tag(original.split())
print( tag_list )
if tag_list[0][0] in ('In','in'):                   #If first verb is 'In'
    print( "Found 'In'!" )
    comma_index = original.find(', ')                #Find index of comma
    print( "Comma index is " + str(comma_index) )
    remainder = original[comma_index + 2 : ]
    print( "Remainder is " + str(remainder) )
    first_space = remainder.find(' ')
    print( "First space is " + str(first_space) )
    word_after_comma = original[ comma_index + 2 : comma_index + 2 + first_space ]
    print( word_after_comma )
