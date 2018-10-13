from basic import *
from kserver import *
from visualize import *


def generate_kserver(N):

    sps = []
    sps.append([Interval(0, 1)])
    for i in range(N):
        intervals = []
        for itv in sps[i]:
            mid = (itv.left + itv.right) / 2
            intervals.append(Interval(itv.left, mid))
            intervals.append(Interval(mid, itv.right))
        sps.append(intervals)
    for sp in sps:
        for i in range(len(sp)):
            sp[i] = IntervalsSet([sp[i]])
    sps = [SemiPartition(sp) for sp in sps]
    return KServer(sps)


def generate_simple_m(x):
    def m(itv):
        if itv.contains(x):
            return 1
        else:
            return 0
    return m


def main(N, mass_function, big_alpha, small_alpha, r):

    # Generate a simple kserver object
    ks = generate_kserver(N)

    visualize(ks)


if __name__ == '__main__':
    simple_m = generate_simple_m(0.1)
    main(7, simple_m, 0, 0, 0)
