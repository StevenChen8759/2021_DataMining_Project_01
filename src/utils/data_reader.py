from typing import List

from loguru import logger

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