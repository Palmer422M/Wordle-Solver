"""
routines for wordle match logic.
Terminology:
    wordle : str, 5-letter
        the truth
    guess : str, 5-letter
        the word to test for a match to the wordle
    state : list if int
    `   results of testing the guess against match.  each letter is
        ST_CORRECT : (green) correct letter in correct position
        ST_ELSEWHERE : (gold) this letter needs to be moved to be correct
        ST_REJECT : (grey) letter not in word

    paint : test a guess against a wordle, the results of which is a state

    filter : given a guess and a state, test whether a candidate wordle matches.  This
        is the inverse of paint.
"""
import time
from matching import *

# the following for testing readability
C = ST_CORRECT
E = ST_ELSEWHERE
R = ST_REJECT

"""

So simulate the next level search that would follow this move
 - reduce the wordlist to words that can fit the Status.  
 - Reduce it further by keeping only NRL words
 - Obtain a reduced set of wordles by filtering from common words, only the wordles that fit the Status.
 - obtain a reduced guess list that includes only NRL words - for probe moves, only interested in those
 - benchmark a search for best subseqent move
"""

combined_wordlist = [line.strip().upper() for line in open("combined_wordlist.txt")]
combined_wordlist = sorted(combined_wordlist[1:])  # get rid of first line comment

# Common words requires some processing:
# - remove duplicates
# - remove words that are not legal wordles
common_words = [line.strip().upper() for line in open("common_words.txt")]
print('Common words = ', len(common_words))
common_words = list(set(common_words))
print('Common words (remove duplicates)= ', len(common_words))
common_words = [w for w in common_words if w in combined_wordlist]
print('Common words that are legal wordles = ', len(common_words))


non_nrl_guesses = remove_non_nrl(combined_wordlist)
print('reduced guesses len', len(non_nrl_guesses))


first_guess = 'LARES'
status = [R, R, E, E, R]
#first_guess = 'CRANE'
#first_guess = 'SOARE'
#status = paint_guess('SWEET', first_guess)

reduced_wordlist = filter_word_list(combined_wordlist, first_guess, status)
print('reduced list len = ', len(reduced_wordlist))
#print(sorted(reduced_wordlist))

non_nrl_wordlist = remove_non_nrl(reduced_wordlist)
#print('Non NRL list len = ', len(non_nrl_wordlist))

reduced_wordles = filter_word_list(common_words, first_guess, status)
print('reduced wordles len', len(reduced_wordles))
#print(sorted(reduced_wordles))

t0 = time.time()

guesses = non_nrl_guesses

list_lens = measure_list_reduction(reduced_wordles, guesses, reduced_wordlist, False)

min_ndx = list_lens.index(min(list_lens))
print('Minimum avg remaining list of %.1f for %s' % (list_lens[min_ndx], guesses[min_ndx]))


t1 = time.time()
print('Elapsed %.1f sec' % (t1 - t0))

save_ranked_guesses(guesses, list_lens, 'sm.xlsx')


