

class Interval:
    """Represents a bounded interval.

    Attributes:
        left (float): The left endpoint of the interval.
        right (float): The right endpoint of the interval.
        string (str): String representation of the interval.
    """

    def __init__(self, left, right):
        """Form a bounded interval.

        Args:
            left (float): The left endpoint.
            right (float) : The right endpoint.

        Raises:
            Exception: If left is greater than or equal to right.
        """
        if left >= right:
            raise Exception('invalid interval: empty set')
        self.left = left
        self.right = right
        self.string = "[" + str(self.left) + ", " + str(self.right) + "]"

    def intersect(self, other):
        """Take the intersection of this interval and the given interval.

        Args:
            other (:obj:`Interval`): The other interval to be intersected.

        Returns:
            :obj:`Interval`: The interval of intersection if it is not an empty set. `None`
            if the intersection is an empty set.
        """
        left = max(self.left, other.left)
        right = min(self.right, other.right)
        if left >= right:
            return None
        else:
            return Interval(left, right)

    def contains(self, x):
        """Check if the given value is contained in the interval.

        Args:
            x (float): A given value.

        Returns:
            bool: True if the interval contains the given value, False otherwise.
        """
        if x >= self.left and x <= self.right:
            return True
        else:
            return False

    def __str__(self):
        """String representation of the interval in the common format used in mathematics.
        E.g. [0.1, 0.2], [0.75, 1].
        """
        return self.string


class IntervalsSet:
    """A collection of disjoint intervals in sorted order representing a set.

    Attributes:
        data (:obj:`List` of :obj:`Interval`): the collection of intervals.
    """

    def __init__(self, intervals):
        """Form a collection of intervals with the given list of disjoint intervals.

        Args:
            intervals (:obj:`List` of :obj:`Interval`): The list of intervals to be
            included.

        Raises:
            Exception: If the given list of intervals is empty or the intervals are not disjoint.
        """
        if len(intervals) == 0:
            raise Exception('invalid intervals: cannot be empty')
        self.data = sorted(intervals, key=lambda interval: interval.left)
        for i in range(1, len(self.data)):
            if self.data[i - 1].right > self.data[i].left:
                raise Exception('invalid intervals: must be disjoint')

    def intersect(self, other):
        """Take the set intersection of the intervals set and the given intervals set.

        Args:
            other (:obj:`IntervalsSet`): The other intervals set for the set intersection operation.

        Returns:
            :obj:`IntervalsSet`: The intervals set representing the resulting set of the intersection.
            `None` if the intersection is an empty set.
        """
        result = []
        curr1 = curr2 = 0
        length1 = len(self.data)
        length2 = len(other.data)
        while curr1 < length1 and curr2 < length2:
            itv1 = self.data[curr1]
            itv2 = other.data[curr2]
            intersection = itv1.intersect(itv2)
            if intersection != None:
                result.append(intersection)
            if itv1.right < itv2.right:
                curr1 += 1
            else:
                curr2 += 1
        if len(result) == 0:
            return None
        else:
            return IntervalsSet(result)

    def contains(self, x):
        """Check if the given value is contained in the set.

        Args:
            x (float): A given value.

        Returns:
            bool: True if the set contains the given value, False otherwise.
        """
        for itv in self.data:
            if itv.contains(x):
                return True
        return False

    def __str__(self):
        s = str(self.data[0])
        for i in range(1, len(self.data)):
            s += "U" + str(self.data[i])
        return s


class SemiPartition:
    """Represents a semi-partition of the interval [0, 1].

    Attributes:
        sets (:obj:`list` of :obj:`IntervalsSet`): List of sets of the semi-partition.
    """

    def __init__(self, sets):
        """Form a semi-partition of the interval [0, 1].

        Args:
            sets (:obj:`list` of :obj:`IntervalsSet`): List of sets of the semi-partition.

        Raises:
            Exception: If the given list of sets is empty, the sets exceed
            the range [0, 1], or there are sets overlapping with each other.
        """
        if len(sets) == 0:
            raise Exception('invalid sets: cannot be empty')
        all_intervals = []
        for itvs in sets:
            for itv in itvs.data:
                all_intervals.append(itv)
        all_intervals.sort(key=lambda interval: interval.left)
        if all_intervals[0].left < 0 or all_intervals[len(all_intervals) - 1].right > 1:
            raise Exception('invalid sets: exceeds [0, 1]')
        for i in range(len(all_intervals) - 1):
            if all_intervals[i].right > all_intervals[i + 1].left:
                raise Exception('invalid sets: sets not disjoint')
        self.sets = sets[:]

    def __str__(self):
        result = "[" + str(self.sets[0])
        for i in range(1, len(self.sets)):
            result += ", " + str(self.sets[i])
        result += "]"
        return result


class Cluster:
    """A collection of sets implemented with a DoublyLinkedList. The sets consist of one
    or more disjoint intervals.

    Attributes:
        sets (:obj:`DoublyLinkedList` of :obj:`IntervalsSet`): The collection of sets.
    """

    def __init__(self, sets):
        """Form a cluster consisting of the sets in the given list.

        Args:
            sets (:obj:`list` of :obj:`IntervalsSet`): The list of sets to be included
            in the cluster.
        """
        if len(sets) == 0:
            raise Exception('invalid sets: cannot be empty')
        self.sets = DoublyLinkedList(sets)

    def is_empty(self):
        return self.sets.is_empty()

    def remove(self, x):
        """Remove the set that contains the given value, if any.

        Args:
            x (float): A given value.

        Returns:
            :obj:`IntervalsSet`: The set removed. `None` if no set is removed.

        Raises:
            Exception: If the cluster would become empty after removal.
        """
        curr = self.sets.first
        while curr != None:
            if curr.data.contains(x):
                if curr.prev == None and curr.next == None:
                    raise Exception()
                if curr.prev == None:
                    self.sets.first = curr.next
                else:
                    curr.prev.next = curr.next
                if curr.next == None:
                    self.sets.last = curr.prev
                else:
                    curr.next.prev = curr.prev
                return curr.data
            curr = curr.next
        return None

    def __str__(self):              # assume self is nonempty
        curr = self.sets.first
        result = str(curr.data)
        curr = curr.next
        while curr != None:
            result += "--" + str(curr.data)
            curr = curr.next
        return result


class SemiClustering:

    def __init__(self, clusters):
        if len(clusters) == 0:
            raise Exception('invalid clusters: cannot be empty')
        self.clusters = clusters[:]

    def __str__(self):
        result = "{" + str(self.clusters[0])
        for i in range(1, len(self.clusters)):
            result += ", " + str(self.clusters[i])
        result += "}"
        return result


class TreeNode:

    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, data):
        self.children.append(TreeNode(data))


class Tree:

    def __init__(self, root):
        self.root = root

    def print_tree(self):
        self._print_tree(self.root, 0)

    def _print_tree(self, node, level):
        print(str("    " * level) + str(node.data))
        for child in node.children:
            self._print_tree(child, level + 1)



class DoublyListNode:

    def __init__(self, data, prev_node, next_node):
        self.data = data
        self.prev = prev_node
        self.next = next_node


class DoublyLinkedList:
    """An implementation of doubly linked list.

    Attributes:
        first (:obj:`DoublyListNode`): The first node of the list.
        last (:obj:`DoublyListNode`): The last node of the list.
    """

    def __init__(self, data_list):
        """Form a doubly linked list according to the given list.

        Args:
            data_list (:obj:`List`): The list of data used to form the doubly linked list.
        """
        self.first = None
        self.last = None
        for data in data_list:
            self.push_back(data)

    def is_empty(self):
        """Check if the doubly linked list is empty.

        Returns:
            bool: True if the list is empty. False otherwise.
        """
        return self.first == None and self.last == None

    def set_to_empty(self):
        """Turn the doubly linked list into an empty list."""
        self.first = None
        self.last = None

    def push_back(self, data):
        """Add data to the back (last) of the list.

        Args:
            data: The data to be inserted.
        """
        if self.is_empty():
            self.first = DoublyListNode(data, None, None)
            self.last = self.first
        else:
            node = DoublyListNode(data, self.last, None)
            self.last.next = node
            self.last = node

    def extend(self, other):
        """Move the elements in the given doubly linked list to the back of this list
        with original order preserved. The given list becomes empty after the operation.

        Args:
            other (:obj:`DoublyLinkedList`): The list of elements to be added.
        """
        if self.is_empty():
            self.first = other.first
            self.last = other.last
        elif not other.is_empty():
            self.last.next = other.first
            other.first.prev = self.last
            self.last = other.last
        other.set_to_empty()

    def print_list(self):
        """Print the list in the forward direction with the format
        "[<first>, <second>, ..., <last>]".
        """
        if self.is_empty():
            print("[]")
        else:
            output = "[" + str(self.first.data)
            curr = self.first.next
            while curr != None:
                output += ", " + str(curr.data)
                curr = curr.next
            output += "]"
            print(output)

    def print_list_reverse(self):
        """Print the list in the reverse direction with the format
        "[<last>, <second_last>, ..., <first>]".
        """
        if self.is_empty():
            print("[]")
        else:
            output = "[" + str(self.last.data)
            curr = self.last.prev
            while curr != None:
                output += ", " + str(curr.data)
                curr = curr.prev
            output += "]"
            print(output)

    def __iter__(self):
        return DoublyLinkedListIterator(self)


class DoublyLinkedListIterator:

    def __init__(self, dll):
        self.curr = dll.first

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr == None:
            raise StopIteration
        else:
            data = self.curr.data
            self.curr = self.curr.next
            return data


def interval_complement_semi_clustering(interval, semi_clustering):
    """Obtain the set of all numbers that are contained in the given interval, but not in
    the given semi-clustering.

    Args:
        interval (:obj:`Interval`): The interval for the operation described.
        semi_clustering (:obj:`SemiClustering`): The semi-clustering for the operation described.

    Returns:
        :obj:`IntervalsSet`: The resulting set of the operation. `None` if the resulting set is empty.
    """
    intersections = []
    for cluster in semi_clustering.clusters:
        curr = cluster.sets.first
        while curr != None:
            for itv in curr.data.data:
                intersection = interval.intersect(itv)
                if intersection != None:
                    intersections.append(intersection)
            curr = curr.next
    if len(intersections) == 0:
        complement = [interval]
    else:
        intersections.sort(key=lambda itv: itv.left)
        complement = []
        left = interval.left
        right = intersections[0].left
        if left < right:
            complement.append(Interval(left, right))
        for i in range(len(intersections) - 1):
            left = intersections[i].right
            right = intersections[i + 1].left
            if left < right:
                complement.append(Interval(left, right))
        left = intersections[len(intersections) - 1].right
        right = interval.right
        if left < right:
            complement.append(Interval(left, right))
    if len(complement) == 0:
        return None
    else:
        return IntervalsSet(complement)
