# Python Standard Module Imprt
from itertools import product as cartesian_product
from typing import Dict, List, Any

# External Module Import
from loguru import logger

# Repo-Defined Module Import
from algorithms import aprori

PHASE_CNT = 2
MINSUP = 0.01
MINCONF = 0.25


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


if __name__ == "__main__":
    logger.info(f"[Phase 1/{PHASE_CNT}] Read Kaggle GMB (Groceries Marketing Basket) Dataset")
    gmb_transactions = read_gmb_data()

    logger.info(f"[Phase 2/{PHASE_CNT}] Obtain association rules by Aprori algorithm, minsup: {MINSUP}, minconf: {MINCONF}")

    aprori.find_association_rule(
            gmb_transactions,
            MINSUP,
            MINCONF,
    )

    logger.info("End of finding association rules in brute force manner")

    logger.success("End of the association rule analysis on Kaggle GMB dataset")
