# Python Standard Module Imprt
from itertools import product as cartesian_product
from typing import Dict, List, Any

# External Module Import
from loguru import logger

PHASE_CNT = 2
MINSUP = 0.05
MINCONF = 0.05


def read_gmb_data() -> List[List[str]]:
    """Read Kaggle GMB Dataset

    Returns:
        List[List[str]]: List of Transactions. For each transaction, it includes items inside.
    """
    with open('./dataset/Kaggle_GMB/groceries.csv', 'r', encoding='utf-8') as gmb_list_fd:
        gmb_list_data = [line[:-1].split(',') for line in gmb_list_fd.readlines()]
    logger.debug(f"Read {len(gmb_list_data)} Transactions")

    # Verify Data Type
    for transaction in gmb_list_data:
        assert isinstance(transaction, list)
        for item in transaction:
            assert isinstance(item, str)

    return gmb_list_data


def find_association_rules_brute_force(
    transactions: List[List[Any]],
    minsup: float,
    minconf: float,
) -> None:
    """Find association rules in a brute force manner

    Args:
        transactions (List[List[Any]]): List of Transactions. For each transaction, it includes items inside.
        minsup (float): minimum support ratio
        minconf (float): minimum confidence ratio
    """
    logger.debug("Evaluate type of items and count of each item")

    minsup_int = round(len(transactions) * minsup)
    minconf_int = round(len(transactions) * minconf)
    logger.debug(f"Minimum support equivalent count: {minsup_int}")
    logger.debug(f"Minimum confidence equivalent count: {minconf_int}")

    # Build up item count list
    item_count_info: Dict[Any, int] = {}
    for transaction in transactions:
        for itemset in transaction:
            if itemset in item_count_info.keys():
                item_count_info[itemset] += 1
            else:
                item_count_info[itemset] = 1

    # Get 1-frequent itemset
    logger.debug("Evaluate 1-frequent itemset")
    freq_itemset = {(itemset,) for itemset in item_count_info if item_count_info[itemset] >= minsup_int}
    logger.debug(f"End of evaluate 1-frequent itemset, count: {len(freq_itemset)}")

    # Get k-frequent itemset for all k >= 2
    freq_itemset_max_item_count = 0
    for k in range(2, len(item_count_info)):
        if k > 10:
            break
        logger.debug(f"Evaluate {k}-frequent itemset")

        # Get Candidate Itemset
        k_freq_itemset_candidates = set(
            tuple(
                {*k_itemset[0], *k_itemset[1]}
            )
            for k_itemset in cartesian_product(
                [itemset for itemset in freq_itemset if len(itemset) == (k - 1)],
                repeat=2,
            )
            if len(tuple({*k_itemset[0], *k_itemset[1]})) == k
        )
        logger.debug(f"Candidate count: {len(k_freq_itemset_candidates)}")

        # Validate length of candidates in candidate itemset
        for candidate in k_freq_itemset_candidates:
            assert len(candidate) == k

        # Scanning Transactions andEvaluate k itemset count
        k_itemset_count_info: Dict[Any, int] = {}
        for transaction in transactions:
            for candidate_itemset in k_freq_itemset_candidates:
                if all(item in transaction for item in candidate_itemset):
                    if candidate_itemset in k_itemset_count_info:
                        k_itemset_count_info[candidate_itemset] += 1
                    else:
                        k_itemset_count_info[candidate_itemset] = 1

        # Filter frequent itemset from count info dict with minimum support
        k_freq_itemset = {
            tuple(itemset)
            for itemset in k_itemset_count_info
            if k_itemset_count_info[itemset] > minsup_int
        }
        logger.debug(f"End of evaluate {k}-frequent itemset, count: {len(k_freq_itemset)}")

        # Check if frequent itemset lookup process reaches terminated condition
        if len(k_freq_itemset) > 0:
            freq_itemset.update(k_freq_itemset)
        else:
            freq_itemset_max_item_count = k
            logger.warning("No any new frequent itemset found, end of iteration")
            break

    # Composite differnet cardinary of I/O Set
    rule_pair_length = []
    for max_rule_length in range(2, freq_itemset_max_item_count + 1):
        for rule_left_length in range(1, max_rule_length):
            # Get perm_limit set and total_items - perm_limit length set
            rule_pair_length.append(
                (rule_left_length, (max_rule_length - rule_left_length))
            )

    # Get input domain set and output range set
    rules = set()
    for rule_pair in rule_pair_length:
        logger.debug(f"Generate Association Rules, Pair Length -> {rule_pair}")
        input_set = {itemset for itemset in freq_itemset if len(itemset) == rule_pair[0]}
        output_set = {itemset for itemset in freq_itemset if len(itemset) == rule_pair[1]}

        # Do cartesian_product and filter duplicated items
        rules.update(
            set(
                rule_pair
                for rule_pair in cartesian_product(input_set, output_set)
                if len(set({*rule_pair[0], *rule_pair[1]})) == len(rule_pair[0]) + len(rule_pair[1])
            )
        )

    # Evaluate confidence by scanning all transaction
    logger.debug("Scan Transactions to Evaluate confidence value")
    final_association_rule = []
    for rule in rules:
        rule_itemset = set({*rule[0], *rule[1]})
        assert len(rule_itemset) == len(rule[0]) + len(rule[1])

        conf_cnt = 0
        for transaction in transactions:
            if all(item in transaction for item in rule_itemset):
                conf_cnt += 1

        if conf_cnt >= minconf_int:
            # print("Found Valid Association Rules")
            final_association_rule.append(rule)

    logger.debug(f"Found {len(final_association_rule)} association rules in final")


if __name__ == "__main__":
    logger.info(f"[Phase 1/{PHASE_CNT}] Read Kaggle GMB (Groceries Marketing Basket) Dataset")
    gmb_transactions = read_gmb_data()

    logger.info(f"[Phase 2/{PHASE_CNT}] Obtain association rules <brute-force> minsup: {MINSUP}, minconf: {MINCONF}")
    find_association_rules_brute_force(
        gmb_transactions,
        MINSUP,
        MINCONF,
    )
    logger.info("End of finding association rules in brute force manner")

    logger.success("End of the association rule analysis on Kaggle GMB dataset")
