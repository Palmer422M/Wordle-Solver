"""
Search for best starting word.
M. Palmer 3/2022
"""
import random
import time
from matching import *

N_RANDOM_WORDLE = 500
use_random_wordles = False

# the following for testing readability
C = ST_CORRECT
E = ST_ELSEWHERE
R = ST_REJECT

combined_wordlist = [line.strip().upper() for line in open("combined_wordlist.txt")]
combined_wordlist = sorted(combined_wordlist[1:])  # get rid of first line comment

print('First Word Search started: ', time.asctime())

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

t0 = time.time()

if use_random_wordles:
    random_wordles = [common_words[random.randint(0, N_RANDOM_WORDLE - 1)] for k in range(N_RANDOM_WORDLE)]

    print('Generating first turn list with random wordles, N=', N_RANDOM_WORDLE)
    first_word_search_wordles = random_wordles
else:
    print('Generating first turn list with all  common word wordles, N=', len(common_words))
    first_word_search_wordles = common_words

guesses = non_nrl_guesses
#current_list = nrl_wordlist
current_list = common_words

nrl_flag = False

list_lens = measure_list_reduction(first_word_search_wordles, guesses, current_list, nrl_flag, tick_lines=1)
min_ndx = list_lens.index(min(list_lens))
print('Minimum avg remaining list of %.1f for %s' % (list_lens[min_ndx], guesses[min_ndx]))

t1 = time.time()
print('Elapsed %.1f sec' % (t1 - t0))

save_ranked_guesses(guesses, list_lens, 'sm.xlsx')


