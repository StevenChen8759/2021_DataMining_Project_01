import sys
from typing import Dict, List, OrderedDict, Tuple, Any

from loguru import logger


class FPTreeNode:
    # Attribute of FPTreeNode
    data: Any
    fp_count: int = None
    children: List['FPTreeNode'] = []
    next_pnode: 'FPTreeNode' = None

    #------------------------------------------------------------------------------
    # Initialization Function
    def __init__(self: 'FPTreeNode', data: Any) -> 'FPTreeNode':
        self.data = data

#     #------------------------------------------------------------------------------
#     # Node Data Operations
#     def get_data(self: 'FPTreeNode') -> Any:
#         return self.__data

#     def set_data(self: 'FPTreeNode', data: Any) -> None:
#         self.__data = data

#     #------------------------------------------------------------------------------
#     # Node Frequent Pattern Count Operations
#     def get_fp_count(self: 'FPTreeNode') -> int:
#         return self.__fp_count

#     def set_fp_count(self: 'FPTreeNode', new_fp_count: int) -> None:
#         if not isinstance(self.__fp_count, int):
#             raise ValueError("Frequent Pattern Count is not set.")
#         self.__fp_count = new_fp_count

#     def set_fp_count_add_1(self: 'FPTreeNode') -> None:
#         if not isinstance(self.__fp_count, int):
#             raise ValueError("Frequent Pattern Count is not set.")
#         self.set_fp_count(self.__fp_count + 1)

#     #------------------------------------------------------------------------------
#     # Parallel Node Operations
#     def get_pnode(self: 'FPTreeNode') -> 'FPTreeNode':
#         return self.__pnode

#     def set_pnode(self: 'FPTreeNode', parallel_node: 'FPTreeNode') -> None:
#         self.__pnode = parallel_node

#     #------------------------------------------------------------------------------
#     # Children List Operations
#     def add_child(self: 'FPTreeNode', child:'FPTreeNode') -> None:
#         self.__children.append(child)

#     def remove_child(self: 'FPTreeNode', child: 'FPTreeNode') -> None:
#         self.__children.remove(child)

#     #------------------------------------------------------------------------------
#     # Child Access Operations
#     def get_children(self: 'FPTreeNode') -> List['FPTreeNode']:
#         return self.__children

#     def get_nth_child(self: 'FPTreeNode', n: int) -> 'FPTreeNode':
#         return self.__children[n]

#     def get_child_count(self: 'FPTreeNode') -> int:
#         return len(self.__children)


# def print_fptree(fptree_root: FPTreeNode):
#     traverse_node = fptree_root
#     print(f"Node Element: {traverse_node.get_data()}")

#     # In-order Traversal
#     for child in traverse_node.get_children():
#         print_fptree(child)


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

    # Print all 1-frequent itemset
    for itemset in frequent_1_itemset:
        print(f"{frequent_1_itemset[itemset]} -> {itemset}")
    logger.debug(f"Found {len(frequent_1_itemset)} 1-frequent itemset")

    # Scan Transactions again to construct ordered transactions without items not in 1-frequent itemset
    ordered_transactions: List[Any] = []
    for transaction in transactions:
        print(f"Original Transaction: {transaction}")
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
            print(f"Ordered Transaction: {ordered_transaction}")
            ordered_transactions.append(ordered_transaction)

        print("----------------------------")

    # Scan ordered_transactions to Construct FP-Tree
    fp_tree_root = FPTreeNode(None, True)
    for transaction in ordered_transactions:
        traverse_node = fp_tree_root     # Point to root node of FP-Tree while scanning new transaction
        print(f"Root Node: {fp_tree_root}")

        # Scan items in transaction
        for item in transaction:
            scan_next = False
            print(f"Traverse Node: {traverse_node}, Children Count: {traverse_node.get_child_count()}")

            # Traverse child of node
            for child_node in traverse_node.get_children():

                # Check if pattern of node matches the item of transaction
                if child_node.get_data() == item:
                    # Frequent Pattern Matched, count once.
                    child_node.set_fp_count_add_1()

                    # Replace traversing node to created_node
                    traverse_node = child_node

                    # Set Flag to Scan Next Item
                    scan_next = True

            if scan_next:
                continue

            # No any children match current item, create new node
            created_node = FPTreeNode(item, False)
            print(f"Build Node with item {item}")

            # Don`t forget to count current node as a frequent pattern
            created_node.set_fp_count_add_1()

            # Append to traverse_node
            traverse_node.add_child(created_node)
            print(f"Created Node: {created_node}, Children Count: {created_node.get_child_count()}")
            print(f"Final Traverse Node: {traverse_node}, Children Count: {traverse_node.get_child_count()}")
            print("-")

            # Replace traversing node to created_node
            traverse_node = None
            traverse_node = created_node
            print(f"Replaced Traverse Node: {traverse_node}, Children Count: {traverse_node.get_child_count()}")
            print("-----------------------")


        break

    # # Print Tree
    # # print_fptree(fp_tree_root)
    # print(fp_tree_root.get_children())


@logger.catch(onerror=lambda _: sys.exit(1))
def find_association_rule():
    pass


if __name__ == "__main__":
    find_frequent_itemset(
        [
            ['a', 'c', 'd', 'f', 'g', 'i', 'm', 'p',],
            ['a', 'b', 'c', 'f', 'i', 'm', 'o',],
            ['b', 'f', 'h', 'j', 'o',],
            ['b', 'c', 'k', 's', 'p',],
            ['a', 'c', 'e', 'f', 'l', 'm', 'n', 'p',],
        ],
        0.6
    )
