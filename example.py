import random
from main import animate_mass_sequence


# Generate degenerate mass sequence
sequence = []
for i in range(32):
    mass = [0] * 32
    mass[i] = 1
    sequence.append(mass)
animate_mass_sequence(sequence)


# Generate random walk mass sequence
sequence = []
n = 41
steps = 45
walker = 5
p = [random.randrange(n) for i in range(walker)]
for i in range(steps):
    mass = [0] * n
    for j in range(len(p)):
        mass[p[j]] += 1
    sequence.append(mass)
    for j in range(len(p)):
        if p[j] <= 0:
            p[j] += 1
        elif p[j] >= n-1:
            p[j] -= 1
        else:
            p[j] += random.choice([1, -1])
animate_mass_sequence(sequence)
