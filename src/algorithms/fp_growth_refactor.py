from logging import log
import sys
from itertools import product as cartesian_product, repeat
from typing import Dict, List, Tuple, Any

from loguru import logger


class FPTreeNode:
    # Attribute of FPTreeNode
    data: Any = None
    fp_count: int = None
    children: List['FPTreeNode'] = None
    pnode: 'FPTreeNode' = None

    #------------------------------------------------------------------------------
    # Initialization Function
    def __init__(self: 'FPTreeNode', data: Any) -> 'FPTreeNode':
        self.data = data
        self.children = []

def print_fptree(fptree_root: FPTreeNode):
    traverse_node = fptree_root
    print(f"Node Element: {traverse_node.data} -> {traverse_node.fp_count}")

    # In-order Traversal
    for child in traverse_node.children:
        print_fptree(child)


def print_fplink(fptree_link: List[FPTreeNode]):
    for fp1_item in fptree_link:
        pt_node = fptree_link[fp1_item]
        node_data = [(pt_node.data, pt_node.fp_count)]          # Head Node Data
        while pt_node.pnode is not None:
            pt_node = pt_node.pnode
            node_data.append((pt_node.data, pt_node.fp_count))

        print(f"{fp1_item} -> {node_data}")


def fp_tree_link_parallel(
    fptree_root: FPTreeNode,
    fptree_link: Dict[Any, FPTreeNode]
) -> None:
    traverse_node = fptree_root

    # Append to parallel link of tree if node data is not None
    if traverse_node.data is not None:
        if fptree_link[traverse_node.data] is not None:
            # Not first node of item, append at last node
            pt_node = fptree_link[traverse_node.data]        # Get Head
            while pt_node.pnode is not None:    # Move to Tail
                pt_node = pt_node.pnode
            pt_node.pnode = traverse_node        # Add Node
        else:
            # First node of item
            fptree_link[traverse_node.data] = traverse_node

    # In-order Traversal
    for child in traverse_node.children:
        fp_tree_link_parallel(child, fptree_link)


def fptree_build_up(
    ordered_transactions: List[List[Any]],
    frequent_1_itemset: Dict[Any, int],
) -> Tuple[Any, Any]:
    # Scan ordered_transactions to Construct FP-Tree
    logger.debug("Build Up FP-Tree with 1-frequent pattern link")
    fp_tree_root = FPTreeNode(None)
    fp_tree_link: Dict[Any, FPTreeNode] = {
        itemset_1: None
        for itemset_1 in frequent_1_itemset
    }

    for transaction in ordered_transactions:
        traverse_node = fp_tree_root     # Point to root node of FP-Tree while scanning new transaction

        # Scan items in transaction
        for item in transaction:
            scan_next = False

            # Traverse child of node
            for child_node in traverse_node.children:

                # Check if pattern of node matches the item of transaction
                if child_node.data == item:
                    # Frequent Pattern Matched, count once.
                    child_node.fp_count += 1

                    # Replace traversing node to created_node
                    traverse_node = child_node

                    # Set Flag to Scan Next Item
                    scan_next = True

            if scan_next:
                continue

            # No any children match current item, create new node
            created_node = FPTreeNode(item)

            # Don`t forget to count current node as a frequent pattern
            created_node.fp_count = 1

            # Append to traverse_node
            traverse_node.children.append(created_node)

            # Replace traversing node to created_node
            traverse_node = created_node

    fp_tree_link_parallel(fp_tree_root, fp_tree_link)

    return fp_tree_root, fp_tree_link


def fptree_bfs_find_fp_prefixes(
    fptree_root: FPTreeNode,
    frequent_1_itemset: Dict[Any, int],
) -> Dict[Any, Dict[Any, FPTreeNode]]:
    # Ref: https://favtutor.com/blogs/breadth-first-search-python

    fp_prefixes: Dict[Any, Dict[Any, FPTreeNode]] = {item: [] for item in frequent_1_itemset}
    bfs_queue: List[Tuple[FPTreeNode, Tuple]] = [(fptree_root, tuple())]

    while len(bfs_queue) > 0:
        # Traverse Node
        traverse_node, traverse_prefix_nodes = bfs_queue.pop(0)

        # Add to fp_prefixes if length of pattern is bigger than 1
        if len(traverse_prefix_nodes) > 0:
            fp_prefixes[traverse_node.data].append(
                (traverse_prefix_nodes, traverse_node.fp_count)
            )

        # Add nodes to queue for traversing in future
        bfs_queue += [
            (
                child,
                traverse_prefix_nodes + (traverse_node,)
                if traverse_node.data is not None
                else tuple(),
            )
            for child in traverse_node.children
        ]

    return fp_prefixes


def generate_frequent_itemset(
    prefixes,
    suffix,
    fptree_root,
    fptree_link,
):
    logger.debug(f"Generate Frequent Itemset with suffix {suffix}")

    # Split length of prefixes
    k_prefixes: Dict[int, Dict] = dict()
    for prefix in prefixes:
        if len(prefix[0]) in k_prefixes:
            k_prefixes[len(prefix[0])][prefix[0]] = prefix[1]
        else:
            k_prefixes[len(prefix[0])] = {prefix[0]: prefix[1]}
        print(f"Prefix Length: {len(prefix[0])} -> {tuple(node.data for node in prefix[0])}, support count: {prefix[1]}")

    print(k_prefixes)

    for k_expand in k_prefixes:
        for k_scan in k_prefixes:
            if k_expand >= k_scan:
                print(f"To Expand {k_expand}, Scan {k_scan} => Pass")
                continue

            print(f"To Expand {k_expand}, Scan {k_scan} => Run")
            for expand_prefix in k_prefixes[k_expand]:
                for scan_prefix in k_prefixes[k_scan]:
                    print(f"Expand: {tuple(prefix_node.data for prefix_node in expand_prefix)}, Scan: {tuple(prefix_node.data for prefix_node in scan_prefix)}")
                    if all(exp_prefix_node in scan_prefix for exp_prefix_node in expand_prefix):
                        k_prefixes[k_expand][expand_prefix] += k_prefixes[k_scan][scan_prefix]
                        print(f"Adjust {tuple(prefix_node.data for prefix_node in expand_prefix)} to -> {k_prefixes[k_expand][expand_prefix]}")



                    # if expand_prefix == 1 and 



@logger.catch(onerror=lambda _: sys.exit(1))
def find_frequent_itemset(
    transactions: List[List[Any]],
    minsup: float,
):
    # Evaluate minimum support count
    minsup_count = round(minsup * len(transactions))
    logger.debug(f"Minimum support count: {minsup_count}")

    logger.debug("Find 1-frequent itemset by scanning transaction")
    candidate_itemset: Dict[Any, int] = {}  # Record candidate itemset with support count

    # Collect all 1-candidate itemsets by scanning transactions
    for transaction in transactions:
        for item in transaction:
            candidate_itemset[item] = (
                candidate_itemset[item] + 1
                if item in candidate_itemset
                else 1
            )

    # Filter 1-frequent itemset by minimum support and sort items
    frequent_1_itemset: Dict[Any, int] = {
        itemset: support_count
        for itemset, support_count in sorted(
            candidate_itemset.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        if candidate_itemset[itemset] >= minsup_count
    }

    # Print count of 1-frequent itemset
    logger.debug(f"Found {len(frequent_1_itemset)} 1-frequent itemset")

    #---------------------------------------------------------------------------------------------------

    # Scan Transactions again to construct ordered transactions without items not in 1-frequent itemset
    logger.debug("Construct ordered transaction")
    ordered_transactions: List[Any] = []
    for transaction in transactions:
        ordered_transaction = []

        # Scan 1-frequent itemset in order
        for itemset_1 in frequent_1_itemset:
            # Scan Item in a Transaction
            for item in transaction:
                # Item matches 1-frequent itemset
                if item == itemset_1:
                    ordered_transaction.append(item)  # Append item by frequent_1_itemset order
                    continue                          # Not possible to find duplicated value, continue.

        # Add to ordered_transactions if length of ordered_transaction is not zero
        if len(ordered_transaction) > 0:
            ordered_transactions.append(ordered_transaction)

    # Scan ordered_transactions to Construct FP-Tree
    logger.debug("Build Up FP-Tree with 1-frequent pattern link")
    fp_tree_root, fp_tree_link = fptree_build_up(
        ordered_transactions,
        frequent_1_itemset,
    )

    #----------------------------------------------------------------------------------------------
    fp_prefixes = fptree_bfs_find_fp_prefixes(fp_tree_root, frequent_1_itemset)

    #----------------------------------------------------------------------------------------------
    for suffix_of_prefix in reversed(fp_prefixes):
        generate_frequent_itemset(fp_prefixes[suffix_of_prefix], suffix_of_prefix)


if __name__ == "__main__":
    find_frequent_itemset(
        [
            # ['A', 'C', 'D'],
            # ['B', 'C', 'E'],
            # ['A', 'B', 'C', 'E'],
            # ['B', 'E']
            # ['a', 'c', 'd', 'f', 'g', 'i', 'm', 'p',],
            # ['a', 'b', 'c', 'f', 'i', 'm', 'o',],
            # ['b', 'f', 'h', 'j', 'o',],
            # ['b', 'c', 'k', 's', 'p',],
            # ['a', 'c', 'e', 'f', 'l', 'm', 'n', 'p',],
            ['Bread', 'Milk', 'Beer'],
            ['Bread', 'Coffee'],
            ['Bread', 'Egg'],
            ['Bread', 'Milk', 'Coffee'],
            ["Milk", 'Egg'],
            ["Bread", 'Egg'],
            ['Milk', 'Egg'],
            ['Bread', 'Milk', 'Egg', 'Beer'],
            ['Bread', 'Milk', 'Egg']
        ],
        0.2
    )
