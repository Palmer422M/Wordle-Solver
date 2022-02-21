"""
Program to solve Wordle puzzles

M. Palmer, Feb, 2022

Do you really not have anything better to do?

Note that "english_words" database (pip install english-words) contains british spelling.  Thought about trying to add
American translations but can't find a source of these.  Decided to try the hug dictionary as follows:
I downloaded words dictionary in json format from here: https://github.com/dwyl/english-words

Official Wordle List obtained from:
https://github.com/Kinkelin/WordleCompetition



"""
import sys
from stats import score_words, sort_by_score, sort_by_usage
import json
#from english_words import english_words_lower_alpha_set
from PyQt5 import QtGui, QtCore, QtWidgets

#words = sorted([w for w in english_words_lower_alpha_set if len(w) == 5])
#print(len(words))
TURN_ROWS = 6
# Letter box states:

ST_REJECT = 0
ST_CORRECT = 1
ST_ELSEWHERE = 2

"""
with open('words_dictionary.json') as f:
    full_list = json.load(f).keys()

print('Full dictionary', len(full_list))

words = sorted([w.upper() for w in full_list if len(w) == 5])

"""


fixed_font = QtGui.QFont('Courier New', 14, QtGui.QFont.Monospace)
grid_font = QtGui.QFont('Ariel', 18)


class LetterBox(QtWidgets.QLabel):
    def __init__(self, update_function, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        self.update_function = update_function
        self.setFont(grid_font)
        self.setFixedSize(30, 30)
        self.state = ST_REJECT
        self.style_from_state()
        #self.setTextAlignment(QtCore.Qt.AlignHCenter)

    def style_from_state(self):

        if self.state == ST_REJECT:
            self.setStyleSheet("border: 1px solid black; background-color : gray; color : white")

        elif self.state == ST_ELSEWHERE:
            self.setStyleSheet("border: 1px solid black; background-color : gold; color : white")

        else: #correct
            self.setStyleSheet("border: 1px solid black; background-color : lightgreen; color : white")

    def mousePressEvent(self, event):
        """
        Handle the single mouse press event.  Note that a single press preceeds double click events.

        Parameters
        ----------
        event

        Returns
        -------

            ROI State:
            0 - nothing happening
            1 - one or more points defined, building new ROI
            2 - moving a control point or the entire ROI (index set to -1)
            3 - dragging to place an arrow
        """
        if event.button() != QtCore.Qt.LeftButton:
            return

        if self.text() == '':
            return

        self.state = (self.state + 1) % 3
        self.style_from_state()

        self.update_function()


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Wordle Solver')

        self.setup_gui()
        self.box_ptr = 0

        self.setCentralWidget(self.main_widget)
        self.letter_entry_box.setFocus()
        #self.main_widget.setFocus()

        self.update_list()


    def update_list(self):
        """
        update the word list box given current constraints
        :return:
        """

        def edit_elim(wlist, letter, psn, row_word, row_state):
            """
            eliminate all words that do not contain letter in any position. Except if the letter is
            duplicated - i.e. fixed in another position a position
            """
            newlist = []
            for w in wlist:
                if not letter in w:
                    newlist += [w]
                elif row_word.count(letter) > 1: # rejected letter is in word but if it's fixed in another place then okay
                    for k, l in enumerate(row_word):
                        if l == letter and ((row_state[k] == ST_CORRECT) or (row_state[k] == ST_ELSEWHERE)):
                            newlist += [w]
                            break
            return newlist

        def edit_elim_positional(wlist, letter, psn):
            """
            remove words that:
                - don't have that letter at all
                - do have that letter in psn
            """
            newlist = []
            for w in wlist:
                if not (w[psn] == letter or letter not in w):
                    newlist += [w]
            return newlist

        def edit_elim_notfixed(wlist, letter, psn):
            newlist = []
            for w in wlist:
                if w[psn] == letter:
                   newlist += [w]

            return newlist

        def post_new_wlist(nlist):
            self.possible_box.clear()

            for w in nlist:
                item = QtWidgets.QListWidgetItem(w)
                item.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.possible_box.addItem(item)

            nw = len(nlist)
            s = 's' if nw != 1 else ''
            self.possible_label.setText('%d possible word%s' % (nw, s))

        if self.box_ptr == 0:
            scores = score_words(words)
            post_new_wlist(sort_by_score(words, scores))
            return

        maxrow = max(0, (self.box_ptr-1) // 5)

        newlist = words

        for r in self.box_row:

            this_row_word = []
            this_row_state = []
            for b in r:
                letter = b.text()
                this_row_word += letter
                this_row_state += [b.state]

            # first set of edits - all words that don't have a correct letter in correct psn.
            for k, b in enumerate(r):
                letter = b.text()
                if letter == '':
                    continue
                if b.state == ST_CORRECT:
                    newlist = edit_elim_notfixed(newlist, letter, k)

            # second set of edits - rejected letters unless in fixed position elsewhere
            for k, b in enumerate(r):
                letter = b.text()
                if letter == '':
                    continue
                if b.state == ST_REJECT:
                    newlist = edit_elim(newlist, letter, k, this_row_word, this_row_state)

            # third set of edits - letters that must exist but are in wrong postion
            # whole grid
            for k, b in enumerate(r):
                letter = b.text()
                if letter == '':
                    continue
                if b.state == ST_ELSEWHERE:
                    newlist = edit_elim_positional(newlist, letter, k)


        if self.sort_button_score.isChecked():
            scores = score_words(newlist)
            post_new_wlist(sort_by_score(newlist, scores))
        else:
            post_new_wlist(sort_by_usage(newlist, common_words))


    def setup_gui(self):

        self.main_widget = QtWidgets.QWidget()

        layout = QtWidgets.QHBoxLayout()

        layV1 = QtWidgets.QVBoxLayout()
        layV2 = QtWidgets.QVBoxLayout()

        test = QtWidgets.QLabel()

        self.box_row = []
        for r in range(TURN_ROWS):
            letter_layout = QtWidgets.QHBoxLayout()

            letter_box = []
            for k in range(5):
                b = LetterBox(self.update_list)
                letter_layout.addWidget(b)
                letter_box += [b]
            layV1.addLayout(letter_layout)
            self.box_row += [letter_box]

        layV1.addStretch()
        self.letter_entry_box = QtWidgets.QLineEdit()
        self.letter_entry_box.textChanged.connect(self.letter_entered_callback)
        self.letter_entry_box.returnPressed.connect(self.word_entered_callback)
        self.letter_entry_box.setFont(fixed_font)

        self.entry_status_box = QtWidgets.QLabel()

        layV1.addWidget(self.letter_entry_box)
        layV1.addWidget(self.entry_status_box)

        layV1.addStretch()

        self.possible_label = QtWidgets.QLabel('Possible Words')
        self.sort_button_score = QtWidgets.QRadioButton('Sort by score')
        self.sort_button_score.setChecked(True)
        self.sort_button_score.clicked.connect(self.sort_score_callback)
        self.sort_button_usage = QtWidgets.QRadioButton('Sort by usage')
        self.sort_button_usage.clicked.connect(self.sort_usage_callback)

        self.possible_box = QtWidgets.QListWidget()
        self.possible_box.setFont(fixed_font)
        self.possible_box.setMaximumWidth(120)
        self.possible_box.itemClicked.connect(self.word_clicked_callback)

        layV2.addWidget(self.possible_label)
        layV2.addWidget(self.sort_button_score)
        layV2.addWidget(self.sort_button_usage)
        layV2.addWidget(self.possible_box)

        layout.addLayout(layV1)
        layout.addLayout(layV2)

        self.main_widget.setLayout(layout)

    def sort_score_callback(self):
        currently_legal_words = [self.possible_box.item(x).text() for x in range(self.possible_box.count())]
        self.possible_box.clear()

        scores = score_words(words)

        sorted_words = sort_by_score(currently_legal_words, scores)
        for w in sorted_words:
            self.possible_box.addItem(w)

    def sort_usage_callback(self):
        currently_legal_words = [self.possible_box.item(x).text() for x in range(self.possible_box.count())]
        self.possible_box.clear()

        sorted_words = sort_by_usage(currently_legal_words, common_words)
        for w in sorted_words:
            self.possible_box.addItem(w)


    def letter_entered_callback(self):
        s = self.letter_entry_box.text()
        if len(s) > 5:
            self.entry_status_box.setText('Too many letters')
            self.letter_entry_box.setText(s[:-1])
            return

        self.letter_entry_box.setText(s.upper())

    def word_clicked_callback(self, item):
        s = item.text()
        self.letter_entry_box.setText(s)
        self.letter_entry_box.setFocus()
        pass

    def word_entered_callback(self):

        s = self.letter_entry_box.text()
        if len(s) < 5:
            self.entry_status_box.setText('Too few letters')
            return

        currently_legal_words = [self.possible_box.item(x).text() for x in range(self.possible_box.count())]
        if s not in currently_legal_words:
            self.entry_status_box.setText('Not a legal word')
            return

        self.letter_entry_box.clear()

        row, col = self.box_ptr // 5, self.box_ptr % 5
        if row >= TURN_ROWS:
            return

        for k in range(5):
            bx = self.box_row[row][k]
            bx.setText(s[k])
            bx.state = ST_REJECT
            bx.style_from_state()

        self.box_ptr = min((row+1)*5, (TURN_ROWS-1)*5)

        self.update_list()

words = [line.strip().upper() for line in open("combined_wordlist.txt")]
words = sorted(words[1:])  #get rid of first line comment
common_words = [line.strip().upper() for line in open("common_words.txt")]

print('Five letter words:', len(words))
print('Common words: ', len(common_words))

qApp = QtWidgets.QApplication(sys.argv)

aw = ApplicationWindow()
aw.show()
rc = qApp.exec_()

sys.exit(rc)