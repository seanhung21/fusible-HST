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


def main(N, mass_function, alpha, beta, r):

    # Generate a simple kserver object
    ks = generate_kserver(N)

    # (1) Fuse heavy intervals

    # (2) Deactive light intervals

    visualize(ks)


if __name__ == '__main__':
    main(7, 0, 0, 0, 0)
