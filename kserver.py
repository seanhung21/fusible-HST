from basic import *


class KServer:
    """Keep track of a sequence of semi-clusterings and its corresponding tree of sets obtained
    by inductive refinement.

    Attributes:
        semi_clusterings (:obj:`list` of :obj:`SemiClustering`): The sequence of semi-clusterings
        derived from the initial semi-partitions.
        tree (:obj:`Tree` of :obj:`DoublyLinkedList` of :obj:`tuple`): The corresponding tree of
        the sequence of the semi-clusterings. Each node of the tree is a list of 2-tuple
        (content, origin) where 'content' (:obj:`IntervalsSet`) represents a set and 'origin'
        (:obj:`IntervalsSet`) points to the interval set the content was derived from in the
        semi-clusterings.
    """

    def __init__(self, semi_partitions):
        """
        Args:
            semi_partitions (:obj:`list` of :obj:`SemiPartition`): A sequence of semi-partitions.
        """
        # Semi-Clusterings
        self.semi_clusterings = []
        for sp in semi_partitions:
            clusters = []
            for itvs in sp.sets:
                clusters.append(Cluster([itvs]))
            self.semi_clusterings.append(SemiClustering(clusters))

        # Tree Structure
        root_set_origin = self.semi_clusterings[0].clusters[0].sets.first.data
        root_set = IntervalsSet([Interval(0, 1)]).intersect(root_set_origin)
        self.tree = Tree(TreeNode(DoublyLinkedList([(root_set, root_set_origin)])))
        self._init_tree(self.tree.root, 1)

    def _init_tree(self, node, next_level):
        if next_level < len(self.semi_clusterings):
            semi_clustering = self.semi_clusterings[next_level]
            for cluster in semi_clustering.clusters:
                child_data = DoublyLinkedList([])
                for intervals_set in cluster.sets:
                    for t in node.data:
                        content = intervals_set.intersect(t[0])
                        if content != None:
                            child_data.push_back((content, intervals_set))
                if not child_data.is_empty():
                    node.add_child(child_data)

            for child in node.children:
                self._init_tree(child, next_level + 1)

    def insert(self, j, interval):
        """Insert the given interval into the j-th semi-clustering.

        Args:
            j (int): An index indicating which semi-partition to insert into.
            interval (:obj:`Interval`): The interval to be inserted.

        Raises:
            Exception: If the entire interval has already existed in the j-th semi-clustering.
        """
        complement = interval_complement_semi_clustering(interval, self.semi_clusterings[j])
        if complement == None:
            raise Exception('interval already existed')

        self.semi_clusterings[j].clusters.append(Cluster([complement]))
        self._insert(self.tree.root, 1, j, complement)

    def _insert(self, node, next_level, target_level, intervals_set):
        if next_level == target_level:
            child_data = DoublyLinkedList([])
            for t in node.data:
                content = intervals_set.intersect(t[0])
                if content != None:
                    child_data.push_back((content, intervals_set))
            if not child_data.is_empty():
                node.add_child(child_data)
                self._init_tree(node.children[len(node.children) - 1], next_level + 1)
        else:
            for child in node.children:
                flag = False
                for t in child.data:
                    intersection = intervals_set.intersect(t[0])
                    if intersection != None:
                        flag = True
                        break
                if flag:
                    self._insert(child, next_level + 1, target_level, intervals_set)

    def delete(self, j, x):
        """Delete the set in the j-th semi-clustering that contains the given value x.

        Args:
            j (int): The index of the semi-clustering.
            x (float): A given value.
        """
        semi_clustering = self.semi_clusterings[j]
        removed_set = None
        for clt in semi_clustering.clusters:
            try:
                removed_set = clt.remove(x)
                if removed_set != None:
                    break
            except:
                removed_set = clt.sets.first.data
                semi_clustering.clusters.remove(clt)
                break
        if removed_set == None:
            raise Exception('no set contains specified value')

        self._delete(self.tree.root, 1, j, removed_set)

    def _delete(self, node, next_level, target_level, intervals_set):
        if next_level < target_level:
            for child in node.children:
                flag = False
                for t in child.data:
                    intersection = intervals_set.intersect(t[0])
                    if intersection != None:
                        flag = True
                        break
                if flag:
                    self._delete(child, next_level + 1, target_level, intervals_set)
        else:
            for child in node.children:
                remaining = DoublyLinkedList([])
                flag = False
                for t in child.data:
                    intersection = intervals_set.intersect(t[0])
                    if intersection == None:
                        remaining.push_back(t)
                    else:
                        flag = True
                child.data = remaining
                if not child.data.is_empty() and flag:
                    self._delete(child, next_level + 1, target_level, intervals_set)
            remaining = []
            for child in node.children:
                if not child.data.is_empty():
                    remaining.append(child)
            node.children = remaining

    def fusion(self, p, a, b):
        """Perform fusion on two clusters in a semi-clustering.

        Args:
            p (int): The index of the semi-clustering in the sequence of semi-clusterings.
            a (int): The index of the first cluster in the semi-clustering.
            b (int): The index of the second cluster in the semi-clustering.

        Raises:
            Exception: If a == b.
        """
        if a == b:
            raise Exception('cannot fuse a cluster and itself')
        clusters = self.semi_clusterings[p].clusters
        clusters[a].sets.extend(clusters[b].sets)
        new_cluster = clusters[a]
        clusters.remove(clusters[b])

        self._fusion(self.tree.root, 1, p, new_cluster)

    def _fusion(self, node, next_level, target_level, cluster):
        if next_level == target_level:
            self._fuse(node, next_level)
        elif next_level < target_level:
            for child in node.children:
                flag = False
                for t in child.data:
                    for intervals_set in cluster.sets:
                        if intervals_set.intersect(t[0]) != None:
                            flag = True
                            break
                    if flag:
                        break
                if flag:
                    self._fusion(child, next_level + 1, target_level, cluster)

    def _fuse(self, node, next_level):
        child_and_clusters = []
        for child in node.children:
            intervals_set = child.data.first.data[1]
            child_and_clusters.append((child, self._find_cluster(next_level, intervals_set)))
        child_and_clusters.sort(key=lambda e: e[1])
        new_children = []
        i = 0
        while i < len(child_and_clusters) - 1:
            if child_and_clusters[i][1] == child_and_clusters[i + 1][1]:
                child1 = child_and_clusters[i][0]
                child2 = child_and_clusters[i + 1][0]
                child1.data.extend(child2.data)
                child1.children.extend(child2.children)
                new_children.append(child1)
                self._fuse(child1, next_level + 1)
                i += 1
            else:
                new_children.append(child_and_clusters[i][0])
            i += 1
        if i < len(child_and_clusters):
            new_children.append(child_and_clusters[i][0])
        node.children = new_children

    def _find_cluster(self, j, intervals_set):
        """Find the cluster which the given set in the j-th semi-clustering is in.

        Args:
            j (int): The index of the semi-clustering.
            intervals_set (:obj:`IntervalsSet`): The given set.

        Returns:
            int: The index of the cluster in the j-th semi-clustering.

        Raises:
            Exception: If the given set is not in the j-th semi-clustering.
        """
        semi_clustering = self.semi_clusterings[j]
        for i in range(len(semi_clustering.clusters)):
            cluster = semi_clustering.clusters[i]
            for s in cluster.sets:
                if s is intervals_set:
                    return i
        raise Exception('no such intervals set in the j-th semi-clustering')

    def fission(self, p, a):
        """Perform fission on a cluster in a semi-clustering.

        Args:
            p (int): The index of the semi-clustering in the sequence of semi-clusterings.
            a (int): The index of the cluster in the semi-clustering.
        """
        clusters = self.semi_clusterings[p].clusters
        removed_cluster = clusters[a]
        for intervals_set in removed_cluster.sets:
            clusters.append(Cluster([intervals_set]))
        clusters.remove(removed_cluster)

        self._fission(self.tree.root, 1, p, removed_cluster)

    def _fission(self, node, next_level, target_level, cluster):
        if next_level == target_level:
            flag = False
            for child in node.children:
                for t in child.data:
                    for intervals_set in cluster.sets:
                        if intervals_set.intersect(t[0]) != None:
                            fission_child = child
                            flag = True
                            break
                    if flag:
                        break
                if flag:
                    break
            data = list(fission_child.data)
            data.sort(key=lambda t: id(t[1]))
            new_nodes_data = []
            start = None
            for i in range(len(data)):
                if i == 0:
                    start = 0
                elif not (data[i][1] is data[start][1]):
                    new_nodes_data.append(data[start:i])
                    start = i
            new_nodes_data.append(data[start:len(data)])
            node.children.remove(fission_child)
            for node_data in new_nodes_data:
                node.add_child(DoublyLinkedList(node_data))
                self._init_tree(node.children[len(node.children) - 1], next_level + 1)

        elif next_level < target_level:
            for child in node.children:
                flag = False
                for t in child.data:
                    for intervals_set in cluster.sets:
                        if intervals_set.intersect(t[0]) != None:
                            flag = True
                            break
                    if flag:
                        break
                if flag:
                    self._fission(child, next_level + 1, target_level, cluster)

    # work for specific trees only (2^(-i))
    # Generator: Each call fuse a heavy interval until all are fused
    # TODO: Instance method or not?
    def fuse_heavy_generator(self, mass, alpha, r):
        heavy_list = []
        self._find_heavy(self.tree.root, mass, alpha, r, 0, heavy_list)
        for (level, itv) in heavy_list:
            length = 2**(-level)
            left_itv = Interval(itv.left - length, itv.left)
            right_itv = Interval(itv.right, itv.right + length)
            a = self._find_cluster_including_interval(level, itv)
            b = self._find_cluster_including_interval(level, left_itv)
            if a is not None and b is not None:
                self.fusion(level, a, b)
            a = self._find_cluster_including_interval(level, itv)
            b = self._find_cluster_including_interval(level, right_itv)
            if a is not None and b is not None:
                self.fusion(level, a, b)

            yield 'level=%d, left=%f, right=%f' % (level, itv.left, itv.right)

    def _find_heavy(self, node, mass, alpha, r, level, heavy_list):
        itv = node.data.first.data[0].data[0]
        length = 2**(-level)
        mass_in_N = mass(Interval(itv.left - r * length, itv.right + r * length))
        if mass(itv) > alpha * mass_in_N:
            heavy_list.append((level, itv))
        for child in node.children:
            self._find_heavy(child, mass, alpha, r, level + 1, heavy_list)

    def _find_cluster_including_interval(self, j, itv):
        """Find the cluster in j-th semi-clustering that includes the given interval.

        Args:
            j (int): The index of the semi-clustering.
            itv (:obj:`Interval`): The given interval.

        Returns:
            int: The index of the cluster in the j-th semi-clustering.
            None: If no cluster include the given interval.
        """
        sc = self.semi_clusterings[j]
        for i in range(len(sc.clusters)):
            cluster = sc.clusters[i]
            for s in cluster.sets:
                for interval in s.data:
                    if itv.left >= interval.left and itv.right <= interval.right:
                        return i
        return None


    def print_tree(self):
        """Print the tree structure of the current sequence of semi-clusterings."""
        self._print_tree(self.tree.root, 0)
        print()

    def _print_tree(self, node, level):
        output = "    " * level
        output += str(node.data.first.data[0])
        curr = node.data.first.next
        while curr != None:
            output += "-" + str(curr.data[0])
            curr = curr.next
        print(output)
        for child in node.children:
            self._print_tree(child, level + 1)

    def __str__(self):
        """List the sequence of semi-clusterings as a string."""
        output = ""
        for sc in self.semi_clusterings:
            output += str(sc) + '\n'
        return output
