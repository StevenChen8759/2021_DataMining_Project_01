import sys
from itertools import product as cartesian_product, repeat
from typing import Any, Dict, List, Set, Tuple

from loguru import logger


def itemset_join(
    left_itemset: Set[Tuple[Any]],
    right_itemset: Set[Tuple[Any]],
    expected_length: int,
) -> Set[Tuple[Any]]:
    """Join two itemset without duplicated items in an itemset and duplicated itemsets between all itemsets

    Args:
        left_itemset (Tuple[Any]): input left itemset
        right_itemset (Tuple[Any]): input right itemset
        expected_length (int): expected length of itemset in joined itemsets

    Returns:
        Set[Tuple[Any]]: joined itemset with strictly testing
    """
    # Do Cartesian product on two itemset with filtering itemsets which length is not matched
    # FIXME: 考量 Python 為泛型程式設計語言，須留意未實作排序的資料結構，可能會需要額外的排序函式。
    itemset_joined = set(   # Filter duplicated tuples
        tuple(
            sorted(     # Sort items by order for filtering duplicated tuples usage
                {
                    *new_itemset[0],    # Merge two different tuples
                    *new_itemset[1],
                }
            )
        )
        for new_itemset in cartesian_product(   # Do Cartesian product and traverse each result
            left_itemset,
            right_itemset,
        )
        if len(tuple({*new_itemset[0],*new_itemset[1]})) == expected_length
    )

    # Verify length after cartesian_product
    # Verify duplicated item in an itemset
    for itemset in itemset_joined:
        assert len(itemset) == expected_length, "Cartesian product outcome does not match expected length."
        assert len(itemset) == len(set(itemset)), "Cartesian product outcome does not match expected length."

    # Verify if there exists two itemsets which have same item with different order
    for itemset_i in itemset_joined:
        for itemset_j in itemset_joined:
            assert (
                set(itemset_i) != set(itemset_j) or itemset_i == itemset_j
            ), "There exists two itemsets which have same item with different order"

    # After passing all assertion test, return joined itemset
    return itemset_joined


@logger.catch(onerror=lambda _: sys.exit(1))
def find_association_rule(
    transactions: List[List[Any]],
    minsup: float,
    minconf: float,
):
    """Find association rules by aprori algorithm

    Args:
        transactions (List[List[Any]]): List of Transactions. For each transaction, it stores items in List format.
        minsup (int): minimum support for finding frequent itemset
        minconf (int): minimum confidence for finding frequent itemset
    """
    # TODO: combine duplicated and similar pattern in this function

    # Evaluate minimum support count
    minsup_count = round(minsup * len(transactions))

    # Record k-frequent itemset with support count
    # Dict[k value, k-frequent itemset in dict format]
    #               => Dict[itemset in tuple format, support count of itemset]
    #                       => item with unspecificed type in itemset
    k_frequent_itemset: Dict[int, Dict[Tuple[Any], int]] = dict()

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

    # Filter candidate itemset with minimum support
    k_frequent_itemset[1] = {
        (item,): candidate_itemset[item]    # Key: Itemset in Tuple format, Value: support count of itemset
        for item in candidate_itemset
        if candidate_itemset[item] >= minsup_count
    }
    logger.debug(f"Found {len(k_frequent_itemset[1])} 1-frequent itemset(s)")

    # Loop while 1-frequent itemset is not empty, until count of k-frequent itemset is zero
    k_value = 2
    while len(k_frequent_itemset[1]):
        logger.debug(f"Find {k_value}-frequent itemset by scanning transaction")

        # Clear all elements in candidate_itemset_suppout
        candidate_itemset.clear()

        # Obtain k-candidate itemset within join operation on k-1 itemset
        candidate_itemset = {
            itemset: 0
            for itemset in itemset_join(
                k_frequent_itemset[k_value - 1],
                k_frequent_itemset[k_value - 1],
                k_value
            )
        }

        # Scan transactions to evaluate support value
        for transaction in transactions:
            for itemset in candidate_itemset:
                if all(item in transaction for item in itemset):
                    candidate_itemset[itemset] += 1

        # Select k-frequent itemset with minimum support
        k_frequent_itemset[k_value] = {
            itemset: candidate_itemset[itemset]      # Key: Itemset in Tuple format, Value: support count of itemset
            for itemset in candidate_itemset
            if candidate_itemset[itemset] >= minsup_count
        }

        logger.debug(f"Found {len(k_frequent_itemset[k_value])} {k_value}-frequent itemset(s)")

        # Stop looping if there are no any new frequent itemset found
        if len(k_frequent_itemset[k_value]) == 0:
            break

        k_value += 1

    # Record association rules for specific frequent itemset with confidence value
    # Dict[itemset in tuple format, association rules for specific frequent itemset in dict format]
    #                               => Dict[association rule, cofidence of rule]
    final_association_rules: Dict[Tuple[Any], Dict[Tuple[Any], float]] = dict()
    total_rule_count: int = 0
    is_added_new_rule: bool = False

    logger.debug("Find association rules and collect them.")

    # Traverse all frequent itemset with different rule length where length >= 2
    for rule_length in range(2, len(k_frequent_itemset)):
        for itemset in k_frequent_itemset[rule_length]:
            found_association_rules: Dict[int, Dict[Tuple[Any], float]] = dict()

            # For each frequent itemset, initially generate rule with length <(rule_length - 1) -> 1>
            candidate_rules = set(
                (
                    tuple(itemset[j] for j in range(rule_length) if i != j),
                    tuple(itemset[j] for j in range(rule_length) if i == j)
                )
                for i in range(rule_length)
            )

            # Pruning - Add rules into final_association_rules where confidence value is higher than minconf
            is_added_new_rule = False
            for candidate_rule in candidate_rules:
                # For traversing convenience, we compose original itemset here
                # FIXME: 考量 Python 為泛型程式設計語言，須留意未實作排序的資料結構，可能會需要額外的排序函式。
                original_itmeset = tuple(sorted({*candidate_rule[0], *candidate_rule[1]}))

                # Evaluate confidence value
                confidence = (
                    k_frequent_itemset[rule_length][original_itmeset] /
                    k_frequent_itemset[rule_length - 1][candidate_rule[0]]
                )

                # Filter by minimum confidence threshold
                if confidence >= minconf:
                    # Dict operation for creating key for specific rule output length
                    if 1 not in found_association_rules:
                        found_association_rules[1] = dict()

                    # Add candidate rule and assign confidence value for rule
                    found_association_rules[1][candidate_rule] = confidence

                    # Count new rule and set loop parameter
                    is_added_new_rule = True
                    total_rule_count += 1

            # If no any candidate rules or new rules in candidate available, continue to scan next frequent itemset
            if not is_added_new_rule:
                continue

            # Rule expansion and evaluate confidence value while rule length is bigger than 2
            rule_oplen = 2
            while rule_length > 2:
                # Collect source for rule expansion
                rule_expand_source = list(found_association_rules[rule_oplen - 1].keys())

                # Clear old candidate rules
                candidate_rules.clear()

                # Generate new rules by traversing rule_expand_source with set operations
                for i in range(len(rule_expand_source)):
                    for j in range(i + 1, len(rule_expand_source)):
                        # Run intersecion on input set and union on output set to expand new rules
                        # FIXME: 考量 Python 為泛型程式設計語言，須留意未實作排序的資料結構，可能會需要額外的排序函式。
                        new_rule = (
                            tuple(sorted(set(rule_expand_source[i][0]).intersection(set(rule_expand_source[j][0])))),
                            tuple(sorted(set(rule_expand_source[i][1]).union(set(rule_expand_source[j][1]))))
                        )

                        # Add to candidate rules set if new rule satisfies specific condition
                        if (
                            len(new_rule[0]) > 0 and
                            len(new_rule[1]) == rule_oplen and
                            len(new_rule[0]) + len(new_rule[1]) == rule_length
                        ):
                            candidate_rules.update([new_rule])

                # Pruning - Add rules into final_association_rules where confidence value is higher than minconf
                is_added_new_rule = False
                for candidate_rule in candidate_rules:
                    # For traversing convenience, we compose original itemset here
                    # FIXME: 考量 Python 為泛型程式設計語言，須留意未實作排序的資料結構，可能會需要額外的排序函式。
                    original_itmeset = tuple(sorted(set({*candidate_rule[0], *candidate_rule[1]})))

                    # Evaluate confidence value with stored support count in frequent itemset
                    confidence = (
                        k_frequent_itemset[rule_length][original_itmeset] /
                        k_frequent_itemset[rule_length - rule_oplen][candidate_rule[0]]
                    )

                    # Filter by minimum confidence threshold
                    if confidence >= minconf:
                        # Dict operation for creating key for specific rule output length
                        if rule_oplen not in found_association_rules:
                            found_association_rules[rule_oplen] = dict()

                        # Add candidate rule and assign confidence value for rule
                        found_association_rules[rule_oplen][candidate_rule] = confidence

                        # Count new rule and set loop parameter
                        is_added_new_rule = True
                        total_rule_count += 1

                # If no any candidate rules or new rules in candidate available, stop rule expansion loop
                if not is_added_new_rule:
                    break

                # Add rule output length for next iteration
                rule_oplen += 1

            # Add found rules to final association rules set
            final_association_rules[itemset] = found_association_rules

    logger.debug(f"Found {total_rule_count} valid association rules")

    return final_association_rules


if __name__ == "__main__":
    transactions: List[List[str]] = [
        ['A', 'C', 'D'],
        ['B', 'C', 'E'],
        ['A', 'B', 'C', 'E'],
        ['B', 'E'],
    ]

    result = find_association_rule(transactions, 0.6, 0.6)

    rule_list = []
    for res in result:
        for oplen in result[res]:
            for rule in result[res][oplen]:
                logger.success(f"Rule: {rule[0]} -> {rule[1]}, confidence: {result[res][oplen][rule]:.2f}")

