__author__ = 'ania'

from PIL import Image
import random, copy
from sys import float_info
import sys
import math
import matplotlib.pyplot as plt

# colors
BLACK = 0
WHITE = 1

SIZE = 50


def get_random_coordinates():
    x = random.randint(0, SIZE - 1)
    y = random.randint(0, SIZE - 1)
    return x, y


def generate_image(g):  # g - density of black points
    image = Image.new("1", (SIZE, SIZE), color=WHITE)
    image.save("bin_in.png")
    pixels = image.load()

    number_of_pixels = SIZE**2
    number_of_black_pixels = int(g * number_of_pixels)

    for i in xrange(number_of_black_pixels):
        x,y = get_random_coordinates()
        while pixels[x,y] != WHITE:
            x,y = get_random_coordinates()
        pixels[x,y] = BLACK

    image.save("bin_in.png")
    return image, pixels


def get_rank(pixels, x, y):  # we give +1 for WHITE, 0 for BLACK
    if pixels[x,y] == BLACK:
        return 1
    else:
        return -1


def energy_of_point1(pixels, x, y):  # 8 neighbors
    energy = 0

    for i in xrange(x - 1, x + 2, 1):
        for j in xrange(y - 1, y + 2, 1):
            if 0 <= i < SIZE and 0 <= j < SIZE:
                energy += 2 * get_rank(pixels, i, j)

    return energy


def energy_of_point2(pixels, x, y):  # 8 neighbors
    energy = 0

    for i in xrange(x - 1, x + 2, 1):
        for j in xrange(y - 1, y + 2, 1):
            if 0 <= i < SIZE and 0 <= j < SIZE:
                if abs(i) == abs(j):
                    energy += 2 * get_rank(pixels, i, j)
    return energy


def energy_of_point3(pixels, x, y):  # 8 neighbors
    energy = 18
    try:
        energy -= 2 * get_rank(pixels, x - 1, y - 1)
    except KeyError:
        pass
    try:
        energy -= 2 * get_rank(pixels, x + 1, y + 1)
    except KeyError:
        pass
    return energy


def rank_4(pixels, x, y, expected_value):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        if pixels[x, y] == expected_value:
            return -1
        else:
            return 0
    else:
        return 0


def energy_of_point4(pixels, x, y):  # 4 neighbors
    energy = 0
    energy += rank_4(pixels, x, y + 1, WHITE)
    energy += rank_4(pixels, x - 1, y, BLACK)
    energy += rank_4(pixels, x, y, WHITE)
    energy += rank_4(pixels, x + 1, y, BLACK)
    energy += rank_4(pixels, x, y - 1, WHITE)
    return energy


def energy_of_point5(pixels, x, y): # 8 neighbors
    energy = 0
    for i in xrange(x - 1, x + 2, 1):
        for j in xrange(y - 1, y + 2, 1):
            if 0 <= i < SIZE and 0 <= j < SIZE and i != x and j != y:
                if pixels[i, j] != pixels[x, y]:
                    energy -= 1
    return energy


def energy_of_point6(pixels, x, y):  # 8 - 16 neighbours
    energy = 0
    for i in xrange(x - 2, x + 3, 1):
        for j in xrange(y - 2, y + 3, 1):
            if 0 <= i < SIZE and 0 <= j < SIZE and i != x and j != y:
                if pixels[i, j] != pixels[x, y] and (abs(i - x) == 1 or abs(j - y) == 1):
                    energy -= 1
                if pixels[i, j] == pixels[x, y] and (abs(i - x) == 2 or abs(j - y) == 2):
                    energy -= 1
    return energy


def total_energy(pixels):
    total = 0
    for i in xrange(0, SIZE, 1):
        for j in xrange(0, SIZE, 1):
            total += energy_of_point6(pixels, i, j)
    return total


def P(new_energy, old_energy, t):
    if new_energy < old_energy:
        return 1
    else:
        return math.exp((-1.0) * float(new_energy - old_energy)/t)


def temperature(t):
    return 0.999 * t


def energy_in_neighbourhood(pixels, x, y):
    sum = 0
    for i in xrange(x - 2, x + 3, 1):
        for j in xrange(y - 2, y + 3, 1):
            if 0 <= i < SIZE and 0 <= j < SIZE:
                sum += energy_of_point6(pixels, i, j)
    return sum


def swap_and_get_energy(image, old_energy):
    new_image = image.copy()
    new_energy = old_energy
    new_image.save("bin_temp.png")
    pixels = new_image.load()
    x,y = get_random_coordinates()
    u,v = get_random_coordinates()

    while pixels[x,y] == pixels[u,v]: # getting pixels with different colors
        u,v = get_random_coordinates()
    new_energy -= energy_in_neighbourhood(pixels, x, y)
    new_energy -= energy_in_neighbourhood(pixels, u, v)

    tmp = pixels[x,y]
    pixels[x,y] = pixels[u,v]
    pixels[u,v] = tmp

    new_energy += energy_in_neighbourhood(pixels, x, y)
    new_energy += energy_in_neighbourhood(pixels, u, v)
    new_image.save("bin_temp.png")

    return new_image, new_energy


def simulated_annealing(initial_image, t):
    s = initial_image
    s_pixels = initial_image.load()
    e = total_energy(s_pixels)
    best_state = s.copy()
    best_state.save("bin_best.png")
    best_energy = e

    energies = []
    while t > float_info.epsilon:
        new_state, new_energy = swap_and_get_energy(s, e)

        if P(new_energy, e, t) > random.random():
            s = new_state.copy()
            s.save("bin_out.png")
            e = new_energy

        energies.append(e)

        if new_energy < best_energy:
            best_state, best_energy = new_state.copy(), new_energy
            best_state.save("bin_best.png")

        t = temperature(t)

    return best_state, best_energy, energies


if __name__ == '__main__':
    density = float(raw_input('Choose density [0.1, 0.2, 0.3, 0.4]: '))
    if density not in [0.1, 0.2, 0.3, 0.4]:
        print 'error: wrong density'
        sys.exit(1)
    image, pix = generate_image(density)

    print 'Lowering energy, wait...'
    best_d, best_e, energies = simulated_annealing(image, 10)
    print 'Showing input and output images.'
    Image.open('bin_in.png').show()
    Image.open('bin_best.png').show()
    print 'Showing energy-time curve.'
    plt.plot(xrange(len(energies)), energies)
    plt.show()
