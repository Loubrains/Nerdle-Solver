# Finds possible combinations for Nerdle given any game state
# Find the game state from the web page using dev tools and copy/paste it to the value of "gamestate" at the bottom
# To do: use number of magentas accounting for edge cases, figure out if nerdle has answers like x+-y=z etc,
# make a thing that grabs info from web, adds guesses, can make guesses that give more information

from collections import Counter
from functools import reduce
import re
import generate_permutations
# from multiprocessing import Pool


def game_loop():
    while True:
        myGamestate = Gamestate(game_state)
        myPossible = PossibleSolutions(myGamestate)
        num, poss = myPossible.filter_permutations()
        print('number of possible solutions:', num)
        print('possible solutiobs:', poss)
        if len(myGamestate.guesses) < 6:
            if '' in myGamestate.greens[-1]:
                guess = input('Enter your guess:')
                game_state["guesses"].append(guess)
                myGamestate = Gamestate(game_state)
                myPossible = PossibleSolutions(myGamestate)
                num, poss = myPossible.filter_permutations()
                print('number of possible solutions:', num)
                print('possible solutiobs:', poss)
            else:
                print('You win!')
                return False

        else:
            print('Game over')
            return False

class Gamestate:
    # emulates the game state including the guessing mechanism and colour calculation
    def __init__(self, game_state):
        print('initializing game state')

        self.charset = set('0123456789+-*/=')
        self.special_charset = set('*/+-=')

        self.solution = game_state["solution"]
        self.guesses = game_state["guesses"]
        
        self.greens = []
        self.blacks = []
        self.magentas = []
        
        self.update_guesses()

    # def add_guess(self, guess):
    #     print('adding guess')
    #     self.guesses += guess
    #     print('updating colours')
    #     self.update_colours(guess)

    def update_guesses(self):
        print('updating colours')
        for guess in self.guesses:
            self.update_colours(guess)

    def update_colours(self, guess):
        counts = Counter(self.solution)
        green = self.empty_guess()
        for i, char in enumerate(guess):
            if char == self.solution[i]:
                green[i] = char
                counts.subtract([char])
        self.greens.append(green)

        black = self.empty_guess()
        magenta = self.empty_guess()
        for i, char in enumerate(guess):
            if char == self.greens[-1][i]:
                continue
            if char not in self.solution:
                black[i] = char
            if char in self.solution:
                if counts[char] > 0:
                    magenta[i] = char
                    counts.subtract([char])
                else:
                    black[i] = char
        self.blacks.append(black)
        self.magentas.append(magenta)

    def empty_guess(self):
        return ['' for _ in range(len(self.solution))]


class PossibleSolutions:
    def __init__(self, game_state):
        print('initializing solver')

        self.game_state = game_state

        self.precalculated_permutations = self.load_precalculated_permutations()

        self.squashed_greens = self.squash(self.game_state.greens)
        self.reduced_greens = self.reduce(self.game_state.greens)
        self.reduced_blacks = self.reduce(self.game_state.blacks)
        self.reduced_magentas = self.reduce(self.game_state.magentas)

        self.min_required, self.exact_required = self.must_use_magentas()
        self.required = (self.min_required | self.exact_required)

        self.available = ((self.game_state.charset - self.reduced_blacks) | self.reduced_magentas) | self.reduced_greens

    def filter_permutations(self):
        # run this to get the answer
        print('filtering impossible permutations')
        possible = [''.join(x) for x in filter(lambda permutation: self.is_possible_permutation(permutation),
                                               self.precalculated_permutations)]
        return len(possible), possible

    def is_possible_permutation(self, permutation):
        # pass if: contains correct no. of magentas (currently just contains reduced set of magentas),
        # contains only remaining available characters, has greens in the correct place,
        # magenta/black numbers not in their positions
        count_permutation = Counter(permutation)
        for num in self.required:
            if self.min_required.get(num):
                if not self.min_required[num] <= count_permutation[num]:
                    return False
            if self.exact_required.get(num):
                if count_permutation[num] != self.exact_required[num]:
                    return False
        if not set(permutation).issubset(self.available):
            return False
        for i, permutation_char in enumerate(permutation):
            if self.squashed_greens[i] != permutation_char and self.squashed_greens[i] != '':
                return False
            if any(magenta[i] == permutation_char for magenta in self.game_state.magentas):
                return False
            if any(black[i] == permutation_char for black in self.game_state.blacks):
                return False
        return True

    def must_use_magentas(self):
        exact_required = {}
        min_required = {}
        for i in range(len(self.game_state.guesses)):
            count_greens = Counter(self.game_state.greens[i])
            num_counts = Counter(self.game_state.magentas[i])
            del num_counts['']
            count_blacks = Counter(self.game_state.blacks[i])
            for num in num_counts:
                if num in count_greens:
                    num_counts[num] += count_greens[num]
                if num in count_blacks:
                    exact_required.update({num: num_counts[num]})
                elif num_counts[num] > (min_required.get(num) if min_required.get(num) else 0):
                    min_required.update({num: num_counts[num]})
        return min_required, exact_required

    def load_precalculated_permutations(self):
        try:
            print('loading precalculated valid permutations')
            with open('precalculated_permutations.txt', 'r') as precalculated_file:
                precalculated_permutations = precalculated_file.read().splitlines()
                return precalculated_permutations
        except Exception:
            print('no precalculated permutations file exists')
            print('generating valid permutations')
            generate_permutations.write_to_file()
            self.load_precalculated_permutations()

    @staticmethod
    def reduce(colour):
        reduced = set(reduce(lambda x, y: set(x) | set(y), colour))
        reduced.remove('')
        return reduced

    @staticmethod
    def squash(list_of_lists):
        # flatten greens to one list
        squashed = ['' for _ in list_of_lists[0]]
        for ls in list_of_lists:
            for i, char in enumerate(ls):
                if char:
                    squashed[i] = char
        return squashed

    @staticmethod
    def split_numbers(permutation):
        return re.findall(r'[0-9]+', permutation)


game_state = {"guesses":["12+34=46"],"solution":"9*9-6=75","gameMode":""}

game_loop()

