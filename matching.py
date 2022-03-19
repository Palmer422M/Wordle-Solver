"""

ToDo: try to clean up outdated comments

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
import random
import time
import openpyxl as opxl

import numpy as np

ST_REJECT = 0
ST_CORRECT = 1
ST_ELSEWHERE = 2

TICK_LINES = 10

def save_ranked_guesses(guesses, list_lens, filename):
    """
    Sort the guesses list according to average lengths (lowest first) and
    write them to an Excel file
    """

    z_sort = sorted(zip(list_lens, guesses), reverse=False)
    for zs in z_sort[:10]:
        print(zs)

    wb = opxl.Workbook()
    ws = wb.active
    for zs in z_sort:
        ws.append(zs)

    wb.save(filename=filename)

def count_painted_letters1(guess, state, letter):
    """
    count the number of times that letter is already painted (i.e. state is either ST_CORRECT,
    or ST_ELSEWHERE
    """

    pl_word = [pl for pl, st in zip(guess,state) if pl == letter and st != ST_REJECT]
    return len(pl_word)

def count_painted_letters(guess, state, letter):
    """
    count the number of times that letter is already painted (i.e. state is either ST_CORRECT,
    or ST_ELSEWHERE
    """
    paint_count = 0
    for k in range(5):
        if state[k] == ST_REJECT:
            continue
        if guess[k] != letter:
            continue

        paint_count += 1

    return paint_count

def paint_guess(wordle, guess):
    """
    say you have a guess and a wordle, return a list of 5 states as follows:
    o	Mark all the positional hits (greens)
    o	Progress left to right and consider any guess letters that are in the
        wordle and not yet coded.  They get coded gold if they are in the Wordle
        with a count larger than the number that have been coded so far (either
        green or gold).

    """

    state = [ST_REJECT] * 5 # defaults

    for k in range(5):
        if wordle[k] == guess[k]:
            state[k] = ST_CORRECT

    for k in range(5):
        if state[k] != ST_REJECT: # already painted
            continue

        match_count = wordle.count(guess[k])
        if match_count == 0:
            continue
        #print('mc=', match_count)

        painted_count = count_painted_letters(guess, state, guess[k])
        #print('pc=', painted_count)

        if painted_count < match_count:
            state[k] = ST_ELSEWHERE

    return state

def filter_guess_nrl(word, guess, state):
    """
    Given the guess and state feedback from wordle turn, decide if the
    candidate word is valid or not.

    This version is only valid for words/guesses with 5 distinct letters
    (non-repeating letters).

    """
    for k in range(5):
        if state[k] == ST_CORRECT:
            if word[k] != guess[k]:
                return False
        else:
            if word[k] == guess[k]:  # both E and R have to fail for exact match
                return False

            if state[k] == ST_REJECT:
                if guess[k] in word:
                    return False
            elif state[k] == ST_ELSEWHERE:
                if guess[k] not in word:
                    return False

    return True

def filter_guess(word, guess, state):
    """
    accept or reject a word, given the information for guess and it's state vector,
    algorithm:
    o   go through in sequence, any single failure fails the full word
    o   filter the correct (green) state - i.e. for every letter that is ST_CORRECT, the word
        must match corresponding letter in guess, if not, reject the word.
    o   filter the reject (grey) state - i.e. for every letter that is ST_REJECT in guess,
        count the number of marked (green or gold) copies of that letter. If the word contains
        number of copies of this letter more than that, reject it.
    o   to filter the elsewhere (gold) state - edit the word to remove

    nm : number of times this letter is marked
    nw : number of times thsi letter appears in word

    guess       state       word         -> result   nw      nw
    [A x x x x] [C x x x x] [A y y y y]  -> True
    [x A x x x] [E x x x x] [A y y y y]  -> True
    [A A x x x] [C E R R R] [A y A y y]  -> True     2       2
    [A A x x x] [C E R R R] [A A y y y]  -> False    2       2
    [A A x x x] [C E R R R] [A y A A y]  -> True     2       3
    [A A x x x] [C E R R R] [A y y y y]  -> False    2       1

    [A A x x x] [C R R R R] [A y A y y]  -> False    1       2
    [A A x x x] [C R R R R] [A y A A y]  -> False    1       3
    [A A x x x] [C R R R R] [A y y y y]  -> True     1       1

    E: Fail if nm > nw
    R: Fail if nm < nw

    """
    for k in range(5):
        if state[k] == ST_CORRECT:
            if word[k] != guess[k]:
                return False
        else:
            if word[k] == guess[k]:  # both E and R have to fail for exact match
                return False

    for k in range(5):
        if state[k] == ST_CORRECT:
            continue

        #if guess[k] == word[k]:
        #    return False

        n_painted = count_painted_letters(guess, state, guess[k])
        n_word = word.count(guess[k])

        if state[k] == ST_ELSEWHERE:
            if n_painted > n_word:
                return False

        else: # state[k] = ST_REJECT
            if n_painted < n_word:
                return False

    return True

def filter_word_list(words, guess, state):
    """
    filter the list to remove words that don't conform the the state associated with guess

    """
    return [word for word in words if filter_guess(word, guess, state)]

def count_remaining_words(wordle, guess, wordlist, nrl_only):
    """
    Given a (what would be hidden) wordle, calculate how many words remain in the
    word list if guess is played.

    """
    st = paint_guess(wordle, guess)

    filter_function = filter_guess_nrl if nrl_only else filter_guess

    sum = 0
    for word in wordlist:
        if filter_function(word, guess, st):
            sum += 1

    return sum

def reducing_power(wordles, guess, wordlist, nrl_only):
    """
    nrl_only (bool)
        True if guess and wordlist are NRL (non-repeated leters) words
    """
    sum = 0
    for wordle in wordles:
        n = count_remaining_words(wordle, guess, wordlist, nrl_only)
        if n == 0:
            print('0: wordle, guess', wordle, guess)
        sum += n
    avg = sum / float(len(wordles))
    return avg

def measure_list_reduction(wordles, guesses, wordlist, nrl_only, tick_lines=TICK_LINES):

    avg_list_len = []
    for k, guess in enumerate(guesses):
        avg = reducing_power(wordles, guess, wordlist, nrl_only)
        avg_list_len += [avg]

        if k % tick_lines == 0:
            print('%5.5d' % k, end='\r')

    print('%5.5d' % len(guesses))
    return avg_list_len

def remove_non_nrl(wordlist):
    nrl_wordlist = []
    for word in wordlist:
        lc = [word.count(l) for l in word]
        if max(lc) == 1:
            nrl_wordlist += [word]
    return nrl_wordlist


if __name__ == "__main__":
    # the following for testing readability
    C = ST_CORRECT
    E = ST_ELSEWHERE
    R = ST_REJECT

    ST = ['R', 'C', 'E']

    def test_paint(wordle, guess):
        print('wordle=', wordle, 'guess=', guess)
        st = paint_guess(wordle, guess)
        print('State=', [ST[s] for s in st])


    def test_filter(guess, state, word, expected):
        res = filter_guess(word, guess, state)
        res_str = '--> Match' if res else '--> NO Match'
        print('guess=', guess, 'state=', [ST[s] for s in state], 'word=', word, res_str)
        if res ^ expected:
            raise ValueError('Unexpected result')


    test_paint('ABCDE', 'FGHIJ')
    test_paint('ABCDE', 'Axxxx')
    test_paint('ABCDE', 'xxxxA')
    test_paint('ABCDE', 'AAxxx')
    test_paint('ABCDE', 'CCxxx')
    test_paint('ABCDE', 'CCCxx')
    print('...')
    test_paint('AAyyy', 'xxxxA')
    test_paint('yBByy', 'BBxxx')
    test_paint('yyBBy', 'BBxxx')
    test_paint('yyBBy', 'xBBxx')

    """
        guess       state       word         -> result   pl      nw
        [A A x x x] [C E R R R] [A y A y y]  -> True 
        [A A x x x] [C E R R R] [A A y y y]  -> False    2       2
        [A A x x x] [C E R R R] [A y A A y]  -> True     2       3
        [A A x x x] [C E R R R] [A y y y y]  -> False    2       1
        
        [A A x x x] [C R R R R] [A y A y y]  -> False    1       2
        [A A x x x] [C R R R R] [A y A A y]  -> False    1       3
        [A A x x x] [C R R R R] [A y y y y]  -> True     1       1
    """

    print('...')
    print('...')
    P = True
    F = False

    test_filter('Axxxx', [C, R, R, R, R], 'Ayyyy', P) # should Pass
    test_filter('Axxxx', [E, R, R, R, R], 'AAyyy', F) # should Fail
    test_filter('Axxxx', [E, R, R, R, R], 'yAyyy', P) # should Pass
    test_filter('Axxxx', [R, R, R, R, R], 'Ayyyy', F) # should Fail
    print('...')

    test_filter('xxxxA', [R, R, R, R, C], 'yyyyA', P) # should Pass
    test_filter('xxxxA', [R, R, R, R, E], 'yyyAA', F) # should Fail
    test_filter('xxxxA', [R, R, R, R, E], 'yyyAy', P) # should Pass
    test_filter('xxxxA', [R, R, R, R, R], 'yyyyA', F) # should Fail
    print('...')

    test_filter('AAxxx', [C, E, R, R, R], 'AyAyy', P) # should Pass
    test_filter('AAxxx', [C, E, R, R, R], 'AAyyy', F) # should Fail
    test_filter('AAxxx', [C, E, R, R, R], 'AyAAy', P) # should Pass
    test_filter('AAxxx', [C, E, R, R, R], 'Ayyyy', F) # should Fail

    combined_wordlist = [line.strip().upper() for line in open("combined_wordlist.txt")]
    combined_wordlist = sorted(combined_wordlist[1:])  #get rid of first line comment
    common_words = [line.strip().upper() for line in open("common_words.txt")]
    common_words = list(set(common_words)) # removed duplicates
    common_words = [w for w in common_words if w in combined_wordlist] # delete illegal words

    t0 = time.time()

    nrl_wordlist = remove_non_nrl(combined_wordlist)

    print('Unique words: ', len(nrl_wordlist))

    non_nrl_guesses = remove_non_nrl(combined_wordlist)
    print('reduced guesses len', len(non_nrl_guesses))

    #guesses = nrl_wordlist[500:600]
    #current_list = nrl_wordlist[:300]
    #nrl_flag = True
    #guesses = combined_wordlist
    #current_list = combined_wordlist[:300]
    #nrl_flag = False

    N_RANDOM_WORDLE = 500
    random_wordles = [common_words[random.randint(0, N_RANDOM_WORDLE - 1)] for k in range(N_RANDOM_WORDLE)]

    do_first_word_search = True
    use_random_wordles = False

    if (do_first_word_search):

        if use_random_wordles:
            print('Generating first turn list with random wordles, N=', N_RANDOM_WORDLE)
            first_word_search_wordles = random_wordles
        else:
            print('Generating first turn list with all  common word wordles, N=', len(common_words))
            first_word_search_wordles = common_words

        guesses = non_nrl_guesses
        current_list = nrl_wordlist
        nrl_flag = True


        list_lens = measure_list_reduction(first_word_search_wordles, guesses, current_list, nrl_flag, tick_lines=1)
        min_ndx = list_lens.index(min(list_lens))
        print('Minimum avg remaining list of %.1f for %s' % (list_lens[min_ndx], guesses[min_ndx]))

        z_sort = sorted(zip(list_lens, guesses), reverse=False)
        for zs in z_sort[:50]:
            print(zs)

        t1 = time.time()
        print('Elapsed %.1f sec' % (t1 - t0))


    #print('Best Starting word: %s, subsequent list length = %.1f' % (combined_wordlist[amin_ndx], amin))



    crane_avg = reducing_power(random_wordles, 'CRANE', nrl_wordlist, True)
    print('CRANE avg %.1f' % crane_avg)

    DO_STATS = False
    if DO_STATS:
        N_SAMP = 5
        averages = []
        for k in range(N_SAMP):
            random_wordles = [common_words[random.randint(0, N_RANDOM_WORDLE - 1)] for k in range(N_RANDOM_WORDLE)]
            arose_avg = reducing_power(random_wordles, 'AROSE', nrl_wordlist, True)
            print('AROSE avg1 %.1f' % arose_avg)
            averages += [arose_avg]

        mean = float(np.mean(averages))
        sd = float(np.std(averages))
        print('Mean = %.1f, sd = %.1f' % (mean, sd))

    t1 = time.time()
    print('Elapsed %.1f sec' % (t1 - t0))

