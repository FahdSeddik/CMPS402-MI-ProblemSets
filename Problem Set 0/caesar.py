from typing import Tuple, List
import utils
from helpers.test_tools import read_text_file,read_word_list
import string
'''
    The DecipherResult is the type defintion for a tuple containing:
    - The deciphered text (string).
    - The shift of the cipher (non-negative integer).
        Assume that the shift is always to the right (in the direction from 'a' to 'b' to 'c' and so on).
        So if you return 1, that means that the text was ciphered by shifting it 1 to the right, and that you deciphered the text by shifting it 1 to the left.
    - The number of words in the deciphered text that are not in the dictionary (non-negative integer).
'''
DechiperResult = Tuple[str, int, int]

def caesar_dechiper(ciphered: str, dictionary: List[str]) -> DechiperResult:
    '''
        This function takes the ciphered text (string) and the dictionary (a list of strings where each string is a word).
        It should return a DechiperResult (see above for more info) with the deciphered text, the cipher shift, and the number of deciphered words that are not in the dictionary. 
    '''
    words = ciphered.split()
    fast_lookup = set(dictionary)
    best_result = ("", 0, len(words))

    for shift in range(26):
        shifted_words = []
        for word in words:
            shifted_word = ''.join(
                string.ascii_lowercase[(ord(letter) - ord('a') - shift) % 26] for letter in word
            )
            shifted_words.append(shifted_word)
        
        in_dict_count = sum(word in fast_lookup for word in shifted_words)
        
        if in_dict_count > len(words) - best_result[2]:
            best_result = (" ".join(shifted_words), shift, len(words) - in_dict_count)
    
    return best_result


