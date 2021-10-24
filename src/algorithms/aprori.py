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

    logger.debug("Find association rules and collect rules which satisfy minimum confidence")

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
                # if round(
                #     k_frequent_itemset[rule_length][itemset] /
                #     k_frequent_itemset[rule_length - 1][tuple(itemset[j] for j in range(rule_length) if i != j)],
                #     2,
                # ) >= minconf
            )

            # Pruning - Add rules into final_association_rules where confidence value is higher than minconf
            for candidate_rule in candidate_rules:
                original_itmeset = tuple(sorted({*candidate_rule[0], *candidate_rule[1]}))
                confidence = (
                    k_frequent_itemset[rule_length][original_itmeset] /
                    k_frequent_itemset[rule_length - 1][candidate_rule[0]]
                )
                if confidence >= minconf:
                    if 1 not in found_association_rules:
                        found_association_rules[1] = dict()
                    found_association_rules[1][candidate_rule] = confidence
                    print(f"Found association rule {candidate_rule}, confidence: {confidence: .2f}")

            # Rule expansion and Evaluate confidence value
            rule_oplen = 2
            while rule_length > 2:
                rule_expand_source = list(found_association_rules[rule_oplen - 1].keys())
                candidate_rules.clear()

                # Run intersecion on input set and union on output set while rule length is bigger than 2
                # print(rule_expand_source)

                # Generate new rules which output length matches specific rule_oplen
                for i in range(len(rule_expand_source)):
                    for j in range(i + 1, len(rule_expand_source)):
                        # print(f"{i}, {j}, Generate rules by {rule_expand_source[i]} and {rule_expand_source[j]}")
                        new_rule = (
                            tuple(sorted(set(rule_expand_source[i][0]).intersection(set(rule_expand_source[j][0])))),
                            tuple(sorted(set(rule_expand_source[i][1]).union(set(rule_expand_source[j][1]))))
                        )

                        if len(new_rule[0]) > 0 and len(new_rule[1]) == rule_oplen and len(new_rule[0]) + len(new_rule[1]) == rule_length:
                            candidate_rules.update([new_rule])

                # Pruning - Add rules into final_association_rules where confidence value is higher than minconf
                new_rule_count = 0
                for candidate_rule in candidate_rules:
                    # print(candidate_rule)
                    original_itmeset = tuple(sorted(set({*candidate_rule[0], *candidate_rule[1]})))
                    confidence = (
                        k_frequent_itemset[rule_length][original_itmeset] /
                        k_frequent_itemset[rule_length - rule_oplen][candidate_rule[0]]
                    )
                    if confidence >= minconf:
                        if rule_oplen not in found_association_rules:
                            found_association_rules[rule_oplen] = dict()
                        found_association_rules[rule_oplen][candidate_rule] = confidence
                        print(f"Found association rule {candidate_rule}, confidence: {confidence: .2f}")
                        new_rule_count += 1

                # If no any candidate rules or new rules in candidate available, stop looping
                if new_rule_count == 0:
                    break

                rule_oplen += 1

            final_association_rules[itemset] = found_association_rules

    rule_count = 0
    for freq_itemset in final_association_rules:
        for rule_output_length in final_association_rules[freq_itemset]:
            rule_count += len(final_association_rules[freq_itemset][rule_output_length])
            # for association_rule in final_association_rules[freq_itemset][rule_output_length]:
            #     print(association_rule)

    logger.debug(f"Found {rule_count} valid association rules")

    return final_association_rules


if __name__ == "__main__":
    transactions: List[List[str]] = [
        ['A', 'C', 'D'],
        ['B', 'C', 'E'],
        ['A', 'B', 'C', 'E'],
        ['B', 'E'],
    ]

    result = find_association_rule(transactions, 0.7, 0.8)

    for res in result:
        logger.warning(f"Result of {res}:\n{result[res]}")
