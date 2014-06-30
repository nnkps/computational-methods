__author__ = 'ania'

import copy
import random, math
from sys import float_info
import sys
import matplotlib.pyplot as plt



def read_sudoku_from_file(filename):
    try:
        file = open(filename, "r")
    except IOError:
        print('there is no such file')
        return

    sudoku = []
    counter = []  # this gives us info about the repeats of numbers

    NUMBER_OF_X = 0

    for i in xrange(9):
        sudoku.append([])
        counter.append(0)
        for j in xrange(9):
            sudoku[i].append(0)

    i = 0
    for line in file.readlines():
        j = 0
        for char in line.split(' '):
            try:
                sudoku[i][j] = int(char)
                counter[sudoku[i][j] - 1] += 1  # for example under index 0 we have how many times 1 repeated
            except ValueError:
                sudoku[i][j] = 0  # field to fill in sudoku
                NUMBER_OF_X += 1
            j += 1
        i += 1

    print 'Blank fields: %d' % NUMBER_OF_X
    file.close()
    return sudoku, counter


def get_random_coordinates():
    x = random.randint(0, 8)
    y = random.randint(0, 8)
    return x, y


def filling_initial_sudoku_with_random_values(sudoku_base, counter):
    state = copy.deepcopy(sudoku_base)  # copying sudoku, we will fill this sudoku randomly
    for number in xrange(1, 10, 1):
        fill_times = 9 - counter[number - 1]
        for j in xrange(fill_times):
            x, y = get_random_coordinates()
            while state[x][y] != 0:
                x, y = get_random_coordinates()  # we want to get empty field
            state[x][y] = number

    return state


def which_position(x):
    if x in [0, 1, 2]:
        return 0
    elif x in [3, 4, 5]:
        return 3
    else:
        return 6


def which_box(x, y):
    u, v = 0, 0 # coordinates of top-left field
    u = which_position(x)
    v = which_position(y)
    return u, v


def energy_for_one_field(state, x, y): # counting repetitions for this field
    value = state[x][y]
    num_of_repeats = 0
    for i in xrange(9):
        if state[x][i] == value and i != y:  # in this row
            num_of_repeats += 1
        if state[i][y] == value and i != x:  # in this column
            num_of_repeats += 1

    u, v = which_box(x, y)
    for i in xrange(u, u + 3, 1):
        for j in xrange(v, v + 3, 1):
            if i != x and j != y and state[i][j] == value:
                num_of_repeats += 1

    return num_of_repeats


def total_energy(state):
    total = 0
    for i in xrange(0, 9, 1):
        for j in range(0, 9, 1):
            total += energy_for_one_field(state, i, j)

    return total


def get_coordinates_of_empty_field(sudoku_base):
    x, y = get_random_coordinates()
    while sudoku_base[x][y] != 0: # we should not change this field!
        x, y = get_random_coordinates()
    return x, y


def swapping_fields(sudoku_base, old_state):
    new_state = copy.deepcopy(old_state)
    x, y = get_coordinates_of_empty_field(sudoku_base)
    while energy_for_one_field(new_state, x, y) == 0:
        x, y = get_coordinates_of_empty_field(sudoku_base)

    u, v = get_coordinates_of_empty_field(sudoku_base)
    while x == u and y == v:
        u, v = get_coordinates_of_empty_field(sudoku_base)

    tmp = new_state[x][y]
    new_state[x][y] = new_state[u][v]
    new_state[u][v] = tmp

    return new_state


def P(new_energy, old_energy, t):
    if new_energy < old_energy:
        return 1
    else:
        return math.exp((-1.0) * float(new_energy - old_energy)/t)


def temperature(t):
    return 0.999 * t
    #return t - 0.05


def simulated_annealing(sudoku_base, initial_state, t):
    s = initial_state
    e = total_energy(s)
    sbest, ebest = s, e
    done = False  # information for us if the result is proper
    accepted_energies = []
    temperatures = []
    while done == False and t > float_info.epsilon:
        t = temperature(t)
        snew = swapping_fields(sudoku_base, s)
        enew = total_energy(snew)

        if P(enew, e, t) > random.random():
            s = snew
            e = enew
        accepted_energies.append(e)
        temperatures.append(t)

        if enew < ebest:
            sbest, ebest = snew, enew

        if ebest == 0:
            done = True

    return s, e, done, accepted_energies, temperatures


def write_solution_to_file(solution, filename):
    file = open(filename, 'w')
    for i in xrange(0, 9, 1):
        for j in range(0, 9, 1):
            file.write(str(solution[i][j]) + ' ')
        file.write('\n')

    file.close()


def show_sudoku(state):
    for line in state:
        char_line = [str(i) if i != 0 else 'X' for i in line]
        print ' '.join(char_line)


if __name__ == '__main__':
    no_sample = raw_input('Choose sudoku sample number [1 - 4]: ')
    if int(no_sample) not in range(1, 5):
        print 'error: wrong number'
        sys.exit(1)

    base, repetitions = read_sudoku_from_file('sudoku_in' + str(no_sample))  # game is first sudoku, we should not change it!
    first_state = filling_initial_sudoku_with_random_values(base, repetitions)
    show_sudoku(base)
    print 'Lowering energy...'
    solution, energy, done, energies, temp = simulated_annealing(base, first_state, 100)

    print 'Solved: ' + str(done)
    print 'Number od repetitions: %d' % energy

    show_sudoku(solution)

    write_solution_to_file(solution, 'sudoku_out' + str(no_sample))
    print 'Showing energy-time curve.'
    plt.plot(xrange(len(energies)), energies)
    plt.show()
