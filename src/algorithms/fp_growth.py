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
    # ancestor: 'FPTreeNode' = None

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

    # In-order Traversal to link all nodes in fptree
    for child in traverse_node.children:
        fp_tree_link_parallel(child, fptree_link)


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

    # Print Tree
    # print_fptree(fp_tree_root)
    # print_fplink(fp_tree_link)

    logger.debug("Use Level Order (BFS) Traversal on FP-Tree to Find All Frequent Pattern Prefixes")
    # Ref: https://favtutor.com/blogs/breadth-first-search-python

    fp_prefixes: Dict[Any, Dict[Any, FPTreeNode]] = {item: [] for item in frequent_1_itemset}
    bfs_queue: List[Tuple[FPTreeNode, Tuple]] = [(fp_tree_root, tuple())]

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

    # for itemset in reversed(fp_prefixes):
    #     print(f"{itemset}")
    #     for prefix_nodes, support_count in fp_prefixes[itemset]:
    #         print(f"{tuple(node.data for node in prefix_nodes)} -> {support_count}")

    # print("------------------------------------------------")

    # Build up conditional FP-Tree (Traverse in reversed order)
    cond_fptrees: Dict[Any, Tuple[FPTreeNode, Dict[Any, FPTreeNode]]] = {}
    for itemset in reversed(fp_prefixes):
        suffix_support_count = frequent_1_itemset[itemset]
        # print(f"{itemset} -> Support Count {suffix_support_count}")

        # Traverse each prefix in the list of prefixes for specific itemset to build up Conditional FP-Tree
        cond_fp_tree_root: FPTreeNode = FPTreeNode(None)
        cond_fp_tree_link: Dict[Any, FPTreeNode] = {}

        # Scan all prefix nodes to find out all possible items
        for prefix_nodes, _ in fp_prefixes[itemset]:
            for prefix_node in prefix_nodes:
                cond_fp_tree_link[prefix_node.data] = None

        # Sort by frequent 1 itemset order
        # TODO: integrate sorting function into a independent function
        index_map = {v: i for i, v in enumerate(frequent_1_itemset)}
        cond_fp_tree_link = {
            k: v for k, v in
            sorted(cond_fp_tree_link.items(), key=lambda pair: index_map[pair[0]])
        }

        # Build Condition FP Tree
        for prefix_nodes, prefix_support_count in fp_prefixes[itemset]:
            # print([node.data for node in prefix_nodes])

            traverse_node: FPTreeNode = cond_fp_tree_root
            for prefix_node in prefix_nodes:
                scan_next = False

                # Check if pattern of node matches the data of prefix_node
                for child_node in traverse_node.children:
                    if prefix_node.data == child_node.data:
                        # Frequent Pattern Matched, count once.
                        # print(f"Prefix matched {prefix_node.data}")
                        child_node.fp_count += prefix_support_count

                        # Replace traversing node to specific child node
                        traverse_node = child_node

                        scan_next = True
                        break

                if scan_next:
                    continue

                # No any children match current prefix_node.data, create new node
                created_node = FPTreeNode(prefix_node.data)
                # print(f"Create node {prefix_node.data}")

                # Don`t forget to count current node as a frequent pattern
                created_node.fp_count = prefix_support_count

                # Append to traverse_node
                traverse_node.children.append(created_node)

                # Replace traversing node to created_node
                traverse_node = created_node
                # print_fptree(cond_fp_tree_root)

        fp_tree_link_parallel(cond_fp_tree_root, cond_fp_tree_link)
        # print("Final Tree:")
        # print_fptree(cond_fp_tree_root)
        # print_fplink(cond_fp_tree_link)

        # print("------------")
        cond_fptrees[itemset] = (cond_fp_tree_root, cond_fp_tree_link)

    # Build up frequent itemset by FP-Tree Traversal (Traverse in reversed order)
    logger.debug("Generate frequent itemset")
    frequent_itemset: Dict[Tuple[Any], int] = dict()
    for suffix in cond_fptrees:
        # print(f"Suffix: {suffix}")
        fp_tree_root, fp_tree_link = cond_fptrees[suffix]

        valid_prefixes_component: Dict[Any, int] = dict()
        # Horizontal Scanning
        for itemset in fp_tree_link:
            traverse_node = fp_tree_link[itemset]
            total_support = 0

            while traverse_node is not None:
                total_support += traverse_node.fp_count

                traverse_node = traverse_node.pnode

            if total_support >= minsup_count:
                valid_prefixes_component[itemset] = total_support
            # print(f"Parallel Prefix: {itemset} -> {total_support} {'(v)' if total_support >= minsup_count else ''}")

        # Tree Scanning (by BFS)
        # print_fptree(fp_tree_root)
        traverse_node = fp_tree_root
        bfs_queue: List[Tuple[FPTreeNode, Tuple]] = [(fp_tree_root, tuple())]
        bfs_valid_prefixes: Dict[Tuple[Any], int] = {}
        while len(bfs_queue) > 0:
            traverse_node, traverse_prefix_nodes = bfs_queue.pop(0)

            # Add to fp_prefixes if length of pattern is bigger than 2
            if len(traverse_prefix_nodes) > 1:
                bfs_prefix = tuple([node.data for node in traverse_prefix_nodes])
                bfs_prefix_support = min([node.fp_count for node in traverse_prefix_nodes])

                # print(f"BFS Prefix: {bfs_prefix} -> {bfs_prefix_support} {'(v)' if bfs_prefix_support >= minsup_count else ''} ")

                bfs_valid_prefixes[bfs_prefix] = bfs_prefix_support

            # Add nodes to queue for traversing in future
            bfs_queue += [
                (
                    child,
                    traverse_prefix_nodes + (child,)
                    if traverse_node.data is not None
                    else (child,),
                )
                for child in traverse_node.children
            ]

        # for component in bfs_valid_prefixes:
        #     print(component)

        valid_prefixes = list(
            {
                tuple(set(result))
                for result in cartesian_product(
                    tuple(valid_prefixes_component),
                    repeat=len(valid_prefixes_component)
                )
            }
        )

        for prefix in valid_prefixes:
            if prefix == tuple():
                break

            final_support = min([valid_prefixes_component[item] for item in list(prefix)])

            if len(prefix) > 1 and prefix in bfs_valid_prefixes:
                final_support = min(final_support, bfs_valid_prefixes[prefix])

            complete_itemset = prefix + (suffix,)
            frequent_itemset[complete_itemset] = final_support

        # print("----------------------------")
    # print(frequent_itemset)

    logger.debug(f"Found {len(frequent_1_itemset)} 1-frequent itemset")

    k_frequent_itemset: Dict[int, Dict[Tuple[Any], int]] = dict()

    k_frequent_itemset[1] = {
        (itemset,): frequent_1_itemset[itemset]
        for itemset in frequent_1_itemset
    }


    k = 2
    while True:
        k_frequent_itemset[k] = {
            tuple(sorted(itemset)): frequent_itemset[itemset]
            for itemset in frequent_itemset
            if len(itemset) == k
        }

        logger.debug(f"Found {len(k_frequent_itemset[k])} {k}-frequent itemset")

        if len(k_frequent_itemset[k]) == 0:
            break

        k = k + 1

    # print(k_frequent_itemset)

    return k_frequent_itemset


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
