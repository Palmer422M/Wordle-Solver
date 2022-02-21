

def score_word(wrd, alpha_dist):
    """
    Score a word s given the alphabetic frequency distribution
    """

    score = 0
    for l in wrd:
        k = ord(l) - ord('A')
        score += alpha_dist[k]

    return score

def remove_duplicate_letters(wrds):
    # create new wordlist with duplicated letters removed:
    edited_words = []
    for w in wrds:
        nw = []
        for l in w:
            if l not in nw:
                nw += [l]
        edited_words += [nw]

    return edited_words

def alpha_frequency(wrds):
    """
    Return a list of alphabet letter frequencies based on the wordlist passed.
    shorten words to eliminate duplicates so that letters are only scorred once per word.
    """

    # tabulate letter frequencies:
    alpha = [0] *26

    for w in wrds:
        for l in w:
            i = ord(l) - ord('A')
            alpha[i] += 1

    return alpha

def score_words(wrds):
    """
    given a list of words, return a list of integers of the same length consisting
    of the score for that word.  The score for a word is the sum of frequencies of each
    letter as it appears in all the words in the list.
    """

    ed_words = remove_duplicate_letters(wrds)
    adist = alpha_frequency(ed_words)

    word_scores = [score_word(ew, adist) for ew in ed_words]

    return word_scores

def sort_by_score(wrds, scores):
    """
    return wrds, sorted in decending order according to score
    """
    z_sort = sorted(zip(scores, wrds), reverse=True)
    return [el for _,el in z_sort]

def sort_by_usage(wrds, c_words):
    """
    return the sorted wrds list, sorting according to the ordered list of coomon words.
    """
    cindex = []

    for w in wrds:
        if w in c_words:
            cindex += [c_words.index(w)]
        else:
            cindex += [30000]

    z_sort = sorted(zip(cindex, wrds), reverse=False)
    return [el for _,el in z_sort]


if __name__ == "__main__":

    words = [line.strip().upper() for line in open("combined_wordlist.txt")]
    words = sorted(words[1:])  #get rid of first line comment
    common_words = [line.strip().upper() for line in open("common_words.txt")]

    print(len(words), ' words')

    w_scores = score_words(words)

    maxv = max(w_scores)
    maxi = w_scores.index(maxv)
    max_score = w_scores[maxi]
    print('Maximum Score:', max_score)


    for k, s in enumerate(w_scores):
        if s == max_score:
            print(words[k], max_score)

    ndx1 = words.index('OATER')
    print('OATER Score:', w_scores[ndx1])

    s_words = sort_by_score(words, w_scores)

    print('sort by score')
    for k in range(10):
        print(s_words[k])

    print('sort by usage')
    s_words = sort_by_usage(words, common_words)
    for k in range(10):
        print(s_words[k])


