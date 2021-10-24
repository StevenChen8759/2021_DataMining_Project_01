# Python Standard Module Imprt
from itertools import product as cartesian_product
from typing import Dict, List, Any

# External Module Import
from loguru import logger

# Repo-Defined Module Import
from utils import data_reader
from algorithms import aprori

PHASE_CNT = 2
MINSUP = 0.01
MINCONF = 0.50


if __name__ == "__main__":
    logger.info(f"[Phase 1/{PHASE_CNT}] Read Kaggle GMB (Groceries Marketing Basket) Dataset")
    gmb_transactions = data_reader.read_gmb_data()

    logger.info(f"[Phase 2/{PHASE_CNT}] Obtain association rules by Aprori algorithm, minsup: {MINSUP}, minconf: {MINCONF}")

    aprori.find_association_rule(
            gmb_transactions,
            MINSUP,
            MINCONF,
    )

    logger.info("End of finding association rules in brute force manner")

    logger.success("End of the association rule analysis on Kaggle GMB dataset")
