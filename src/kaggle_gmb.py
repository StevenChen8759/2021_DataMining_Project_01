# Python Standard Module Imprt
import os

# External Module Import
from loguru import logger

# Repo-Defined Module Import
from utils import data_reader
from algorithms import aprori, fp_growth

PHASE_CNT = 10

# Adjust this parameter in needed
MINSUP = 0.02
MINCONF = 0.05

def mkdir_conditional(dir_path: str) -> None:
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)


if __name__ == "__main__":

    mkdir_conditional("./output")

    logger.info(f"[Phase 1/{PHASE_CNT}] Read Kaggle GMB (Groceries Marketing Basket) Dataset")
    gmb_transactions = data_reader.read_gmb_data()

    logger.info(f"[Phase 2/{PHASE_CNT}] GMB - Obtain frequent itemset by Aprori algorithm,, minsup: {MINSUP}")
    aprori_gmb_frequent_itemset = aprori.find_frequent_itemset(
        gmb_transactions,
        MINSUP,
    )

    print(aprori_gmb_frequent_itemset)

    logger.info(f"[Phase 3/{PHASE_CNT}] GMB - Obtain association rules by Aprori algorithm,, minconf: {MINCONF}")
    aprori_gmb_association_rules = aprori.find_association_rule(
        aprori_gmb_frequent_itemset,
        MINCONF,
    )

    logger.info("GMB - End of finding association rules by Aprori algorithm")

    logger.info("GMB - Aprori - Write into output files")
    with open(f'./output/Kaggle_GMB_APR_APR_FI_Minsup_{MINSUP}.csv', 'w+') as writer:
        writer.write(f"frequent itemset, support count\n")
        for length in aprori_gmb_frequent_itemset:
            for itemset in aprori_gmb_frequent_itemset[length]:
                writer.write(f"{itemset}, {aprori_gmb_frequent_itemset[length][itemset]}\n")

    with open(f'./output/Kaggle_GMB_APR_APR_AR_Minsup_{MINSUP}_Minconf_{MINCONF}.csv', 'w+') as writer:
        writer.write(f"association runle, confidence\n")

        for itemset in aprori_gmb_association_rules:
            for oplen in aprori_gmb_association_rules[itemset]:
                for rule in aprori_gmb_association_rules[itemset][oplen]:
                    writer.write(f"({rule[0]} -> {rule[1]}), {aprori_gmb_association_rules[itemset][oplen][rule]:.2f}\n")


    logger.info(f"[Phase 4/{PHASE_CNT}] GMB - Obtain frequent itemset by FP-Growth algorithm,, minsup: {MINSUP}")
    fpgrowth_gmb_frequent_itemset = fp_growth.find_frequent_itemset(
        gmb_transactions,
        MINSUP,
    )

    # print(fpgrowth_frequent_itemset[2])

    logger.info(f"[Phase 5/{PHASE_CNT}] GMB - Obtain association rules by FP-Growth algorithm,, minconf: {MINCONF}")
    fpgrowth_association_rules = aprori.find_association_rule(
        fpgrowth_gmb_frequent_itemset,
        MINCONF,
    )

    logger.info("GMB - End of finding association rules by FP-Growth algorithm")

    logger.info("GMB - FP-Growth Write into output files")
    with open(f'./output/Kaggle_FPG_APR_APR_FI_Minsup_{MINSUP}.csv', 'w+') as writer:
        writer.write(f"frequent itemset, support count\n")
        for length in fpgrowth_gmb_frequent_itemset:
            for itemset in fpgrowth_gmb_frequent_itemset[length]:
                writer.write(f"{itemset}, {fpgrowth_gmb_frequent_itemset[length][itemset]}\n")

    with open(f'./output/Kaggle_FPG_APR_APR_AR_Minsup_{MINSUP}_Minconf_{MINCONF}.csv', 'w+') as writer:
        writer.write(f"association runle, confidence\n")

        for itemset in aprori_gmb_association_rules:
            for oplen in aprori_gmb_association_rules[itemset]:
                for rule in aprori_gmb_association_rules[itemset][oplen]:
                    writer.write(f"({rule[0]} -> {rule[1]}), {aprori_gmb_association_rules[itemset][oplen][rule]:.2f}\n")


    logger.info(f"[Phase 6/{PHASE_CNT}] Read IBM QSDG Dataset")
    qsdg_transactions = data_reader.read_qsdg_data()

    logger.info(f"[Phase 7/{PHASE_CNT}] QSDG - Obtain frequent itemset by Aprori algorithm,, minsup: {MINSUP}")
    aprori_qsdg_frequent_itemset = aprori.find_frequent_itemset(
        qsdg_transactions,
        MINSUP,
    )

    logger.info(f"[Phase 8/{PHASE_CNT}] QSDG - Obtain association rules by Aprori algorithm,, minconf: {MINCONF}")
    aprori_qsdg_association_rules = aprori.find_association_rule(
        aprori_qsdg_frequent_itemset,
        MINCONF,
    )

    logger.info("QSDG - Aprori - Write into output files")
    with open(f'./output/IBM_QSDG_APR_APR_FI_Minsup_{MINSUP}.csv', 'w+') as writer:
        writer.write(f"frequent itemset, support count\n")
        for length in aprori_qsdg_frequent_itemset:
            for itemset in aprori_qsdg_frequent_itemset[length]:
                writer.write(f"{itemset}, {aprori_qsdg_frequent_itemset[length][itemset]}\n")

    with open(f'./output/IBM_QSDG_APR_APR_AR_Minsup_{MINSUP}_Minconf_{MINCONF}.csv', 'w+') as writer:
        writer.write(f"association runle, confidence\n")

        for itemset in aprori_qsdg_association_rules:
            for oplen in aprori_qsdg_association_rules[itemset]:
                for rule in aprori_qsdg_association_rules[itemset][oplen]:
                    writer.write(f"({rule[0]} -> {rule[1]}), {aprori_qsdg_association_rules[itemset][oplen][rule]:.2f}\n")

    logger.info("QSDG - End of finding association rules by Aprori algorithm")

    logger.info(f"[Phase 9/{PHASE_CNT}] QSDG - Obtain frequent itemset by FP-Growth algorithm,, minsup: {MINSUP}")
    fpgrowth_qsdg_frequent_itemset = fp_growth.find_frequent_itemset(
        qsdg_transactions,
        MINSUP,
    )

    logger.info(f"[Phase 10/{PHASE_CNT}] QSDG - Obtain frequent itemset by FP-Growth algorithm,, minsup: {MINSUP}")
    fpgrowth_qsdg_association_rules = aprori.find_association_rule(
        aprori_qsdg_frequent_itemset,
        MINCONF,
    )

    logger.info("QSDG - End of finding association rules by FP-Growth algorithm")

    logger.info("QSDG - FP-Growth - Write into output files")
    with open(f'./output/IBM_QSDG_FPG_APR_FI_Minsup_{MINSUP}.csv', 'w+') as writer:
        writer.write(f"frequent itemset, support count\n")
        for length in fpgrowth_qsdg_frequent_itemset:
            for itemset in fpgrowth_qsdg_frequent_itemset[length]:
                writer.write(f"{itemset}, {fpgrowth_qsdg_frequent_itemset[length][itemset]}\n")

    with open(f'./output/IBM_QSDG_FPG_APR_AR_Minsup_{MINSUP}_Minconf_{MINCONF}.csv', 'w+') as writer:
        writer.write(f"association runle, confidence\n")

        for itemset in aprori_qsdg_association_rules:
            for oplen in aprori_qsdg_association_rules[itemset]:
                for rule in aprori_qsdg_association_rules[itemset][oplen]:
                    writer.write(f"({rule[0]} -> {rule[1]}), {aprori_qsdg_association_rules[itemset][oplen][rule]:.2f}\n")


    logger.success("End of the association rule analysis")
