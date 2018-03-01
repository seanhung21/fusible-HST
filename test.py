import ete3
from basic import *
from kserver import *
from tree_conversion import basic_to_ete


def print_kserver(ks):
    """Print the sequence of semi-clusterings and its corresponding tree of the
    given KServer object.

    Args:
        ks (:obj:`KServer`): The KServer object.
    """
    print(ks)
    ks.print_tree()


# construct the sequence of semi-partitions and form the KServer
sp0 = SemiPartition([IntervalsSet([Interval(0, 1)])])
sp1 = SemiPartition([IntervalsSet([Interval(0.1, 0.4)]), IntervalsSet([Interval(0.7, 1)])])
sp2 = SemiPartition([IntervalsSet([Interval(0, 0.3)]), IntervalsSet([Interval(0.3, 0.8)]),
                     IntervalsSet([Interval(0.8, 1)])])
sp3 = SemiPartition([IntervalsSet([Interval(0.75, 0.9)]), IntervalsSet([Interval(0.2, 0.5)]),
                     IntervalsSet([Interval(0.5, 0.75)])])
sp4 = SemiPartition([IntervalsSet([Interval(0.55, 0.65)]), IntervalsSet([Interval(0.15, 0.25)]),
                     IntervalsSet([Interval(0.75, 0.8)]), IntervalsSet([Interval(0.8, 0.95)])])
ks = KServer([sp0, sp1, sp2, sp3, sp4])
print_kserver(ks)


# a series of operations
ks.insert(1, Interval(0.45, 0.65))
print_kserver(ks)

ks.insert(3, Interval(0, 1))
print_kserver(ks)

ks.delete(2, 0.65)
print_kserver(ks)

ks.delete(3, 0.1)
print_kserver(ks)

ks.insert(2, Interval(0.3, 0.8))
print_kserver(ks)

ks.fusion(3, 1, 2)
print_kserver(ks)

ks.fusion(1, 2, 0)
print_kserver(ks)

ks.fusion(2, 2, 1)
print_kserver(ks)

ks.fusion(3, 0, 1)
print_kserver(ks)

ks.delete(3, 0.6)
print_kserver(ks)

ks.insert(3, Interval(0.5, 0.75))
print_kserver(ks)

ks.fusion(3, 1, 0)
print_kserver(ks)

ks.fission(3, 0)
print_kserver(ks)

ks.fusion(1, 0, 1)
print_kserver(ks)

ks.fission(2, 0)
print_kserver(ks)

ks.fission(2, 0)
print_kserver(ks)

ks.fission(1, 0)
print_kserver(ks)


# tree_conversion
ete_tree = basic_to_ete(ks.tree)
print(ete_tree)
ts = ete3.TreeStyle()
# ts.mode = "c"
# ts.arc_start = 0
# ts.arc_span = 180
ts.branch_vertical_margin = 20
ts.rotation = 90

for node in ete_tree.traverse():
    node.add_face(ete3.RectFace(5, 10, "Red", "MediumBlue"), column=0,
                  position="branch-right")

ete_tree.show(tree_style=ts)
