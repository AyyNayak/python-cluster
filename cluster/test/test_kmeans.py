#
# This is part of "python-cluster". A library to group similar items together.
# Copyright (C) 2006    Michel Albert
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

from cluster import (KMeansClustering, ClusteringError)
import unittest


def compare_list(x, y):
    """
    Compare lists by content. Ordering does not matter.
    Returns True if both lists contain the same items (and are of identical
    length)
    """

    cmpx = [set(cluster) for cluster in x]
    cmpy = [set(cluster) for cluster in y]

    all_ok = True

    for cset in cmpx:
        all_ok &= cset in cmpy

    for cset in cmpy:
        all_ok &= cset in cmpx

    return all_ok


class KClusterSmallListTestCase(unittest.TestCase):

    def testClusterLen1(self):
        "Testing that a search space of length 1 returns only one cluster"
        cl = KMeansClustering([876])
        self.assertEqual([876], cl.getclusters(2))
        self.assertEqual([876], cl.getclusters(5))

    def testClusterLen0(self):
        "Testing if clustering an empty set, returns an empty set"
        cl = KMeansClustering([])
        self.assertEqual([], cl.getclusters(2))
        self.assertEqual([], cl.getclusters(7))


class KCluster2DTestCase(unittest.TestCase):

    def testClusterCount(self):
        "Test that asking for less than 2 clusters raises an error"
        cl = KMeansClustering([876, 123, 344, 676],
                              distance=lambda x, y: abs(x - y))
        self.assertRaises(ClusteringError, cl.getclusters, 0)
        self.assertRaises(ClusteringError, cl.getclusters, 1)

    def testNonsenseCluster(self):
        """
        Test that asking for more clusters than data-items available raises an
        error
        """
        cl = KMeansClustering([876, 123], distance=lambda x, y: abs(x - y))
        self.assertRaises(ClusteringError, cl.getclusters, 5)

    def testUniformLength(self):
        """
        Test if there is an item in the cluster that has a different
        cardinality
        """
        data = [(1, 5), (2, 5), (2, 6), (3, 4), (3, 5), (3, 6, 7), (7, 3),
                (8, 1), (8, 2), (8), (9, 2), (9, 3)]
        self.assertRaises(ValueError, KMeansClustering, data)

    def testPointDoubling(self):
        "test for bug #1604868"
        data = [(18, 13), (15, 12), (17, 12), (18, 12), (19, 12), (16, 11),
                (18, 11), (19, 10), (0, 0), (1, 4), (1, 2), (2, 3), (4, 1),
                (4, 3), (5, 2), (6, 1)]
        cl = KMeansClustering(data)
        clusters = cl.getclusters(2)
        expected = [[(18, 13), (15, 12), (17, 12), (18, 12), (19, 12),
                     (16, 11), (18, 11), (19, 10)],
                    [(0, 0), (1, 4), (1, 2), (2, 3), (4, 1),
                     (5, 2), (6, 1), (4, 3)]]
        self.assertTrue(compare_list(
            clusters,
            expected),
            "Elements differ!\n%s\n%s" % (clusters, expected))

    def testClustering(self):
        "Basic clustering test"
        data = [(8, 2), (7, 3), (2, 6), (3, 5), (3, 6), (1, 5), (8, 1),
                (3, 4), (8, 3), (9, 2), (2, 5), (9, 3)]
        cl = KMeansClustering(data)
        self.assertEqual(
            cl.getclusters(2),
            [[(8, 2), (8, 1), (8, 3), (7, 3), (9, 2), (9, 3)],
             [(3, 5), (1, 5), (3, 4), (2, 6), (2, 5), (3, 6)]])

    def testUnmodifiedData(self):
        "Basic clustering test"
        data = [(8, 2), (7, 3), (2, 6), (3, 5), (3, 6), (1, 5), (8, 1),
                (3, 4), (8, 3), (9, 2), (2, 5), (9, 3)]
        cl = KMeansClustering(data)

        new_data = []
        [new_data.extend(_) for _ in cl.getclusters(2)]
        self.assertEqual(sorted(new_data), sorted(data))


class KClusterSFBugs(unittest.TestCase):

    def testLostFunctionReference(self):
        "test for bug #1727558"
        cl = KMeansClustering([(1, 1), (20, 40), (20, 41)],
                              lambda x, y: x + y)
        clusters = cl.getclusters(3)
        expected = [(1, 1), (20, 40), (20, 41)]
        self.assertTrue(compare_list(
            clusters,
            expected),
            "Elements differ!\n%s\n%s" % (clusters, expected))

    def testMultidimArray(self):
        from random import random
        data = []
        for _ in range(200):
            data.append([random(), random()])
        cl = KMeansClustering(data, lambda p0, p1: (
            p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)
        cl.getclusters(10)
