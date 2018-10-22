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
        """Mass contained in the given interval.

        Args:
            itv (:obj:`Interval`): The given interval.

        Returns:
            int: The amount of mass contained in the interval.
        """
        if itv.contains(x):
            return 1
        else:
            return 0
    return m


def tmp_m(itv):
    total = 0
    if itv.contains(0.3):
        total += 0.91
    if itv.contains(0.9):
        total += 0.09
    return total


def main(N, mass_function, big_alpha, small_alpha, r):

    # Generate a simple kserver object
    ks = generate_kserver(N)
    ks.fuse_heavy(mass_function, big_alpha, r)
    ks.print_tree()
    visualize(ks, tmp_m, 0.01)


if __name__ == '__main__':
    simple_m = generate_simple_m(0.3)
    main(4, tmp_m, 0.9, 0, 4)
