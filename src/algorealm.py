"""
AlgoRealm, only generous heart will ever rule over Algorand. (by cusma)

Usage:
  algorealm.py poem
  algorealm.py dynasty [--test]
  algorealm.py longevity (--crown | --sceptre) [--test]
  algorealm.py braveness (--crown | --sceptre) [--test]
  algorealm.py claim-majesty (--crown | --sceptre) <majesty-name> <microalgos> [--test]
  algorealm.py claim-card
  algorealm.py buy-order <microalgos> [--notify]
  algorealm.py verify-order <seller-address>
  algorealm.py sell-card
  algorealm.py [--help]

Commands:
  poem             AlgoRealm's poem.
  dynasty          Print the glorious dynasty of AlgoRealm's Majesties.
  longevity        Print AlgoRealm's Majesties longevity.
  braveness        Print AlgoRealm's Majesties braveness.
  claim-majesty    Claim the Crown of Entropy or the Sceptre of Proof, become Majesty of Algorand.
  claim-card       Brake the spell and claim the AlgoRealm Card by AlgoWorld.
  buy-order        Place an order for the AlgoRealm Card.
  verify-order     Verify the partially signed AlgoRealm Card buy order.
  sell-card        Sell the AlgoRealm Card (paying a 10% royalty).

Options:
  -n, --notify    Notify the Seller about your buy order on-chain.
  -t, --test      TestNet mode
  -h, --help
"""


import sys

from algosdk import util
from algosdk.error import AlgodHTTPError
from algosdk.future.transaction import retrieve_from_file
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from docopt import docopt
from prettytable import PrettyTable

import actions
import query
from const import (
    ALGOD_ADDRESS,
    ALGOREALM_APP_ID,
    ALGOREALM_CARD_FIRST_BLOCK,
    ALGOREALM_FIRST_BLOCK,
    ALGOREALM_LAW_BYTECODE,
    CARD_CONTRACT_BYTECODE,
    CARD_ID,
    CROWN_ID,
    HEADER,
    INDEXER_ADDRESS,
    ROYALTY_COLLECTOR_1,
    ROYALTY_COLLECTOR_2,
    SCEPTRE_ID,
    TEST_ALGOD_ADDRESS,
    TEST_ALGOREALM_APP_ID,
    TEST_ALGOREALM_FIRST_BLOCK,
    TEST_ALGOREALM_LAW_BYTECODE,
    TEST_CROWN_ID,
    TEST_INDEXER_ADDRESS,
    TEST_SCEPTRE_ID,
)


def build_algod_client(
    api_address: str = ALGOD_ADDRESS,
    test: bool = False,
) -> AlgodClient:
    if test:
        api_address = TEST_ALGOD_ADDRESS
    return AlgodClient(algod_token="", algod_address=api_address, headers=HEADER)


def build_indexer_client(
    api_address: str = INDEXER_ADDRESS,
    test: bool = False,
) -> IndexerClient:
    if test:
        api_address = TEST_INDEXER_ADDRESS
    return IndexerClient(indexer_token="", indexer_address=api_address, headers=HEADER)


def title():
    return r"""
                               __  __   ___   __  __
                               \*) \*)  \*/  (*/ (*/
                                \*\_\*\_|O|_/*/_/*/
                                 \_______________/
          _       __                 _______                  __
         / \     [  |               |_   __ \                [  |
        / _ \     | |  .--./)  .--.   | |__) |  .---.  ,--.   | |  _ .--..--.
       / ___ \    | | / /'`\;/ .'`\ \ |  __ /  / /__\\`'_\ :  | | [ `.-. .-. |
     _/ /   \ \_  | | \ \._//| \__. |_| |  \ \_| \__.,// | |, | |  | | | | | |
    |____| |____|[___].',__`  '.__.'|____| |___|'.__.'\'-;__/[___][___||__||__]
                     ( ( __))
                                                                    by cusma
    """


def poem():
    return r"""
                    ,-----------------------------------------.
                   (_\                                         \
                      |  There was a time                       |
                      |  When nothing but Entropy was there.    |
                      |  Then came the cryptographic Proof,     |
                      |  And took it care.                      |
                      |                                         |
                      |  Verifiability of Randomness,           |
                      |  Since genesis block,                   |
                      |  Brings Consensus over realm vastness,  |
                      |  So Algorand shall not fork.            |
                     _|                                         |
                    (_/___________________(*)___________________/
                                           \\
                                            ))
                                            ^
    """


def main():
    if len(sys.argv) == 1:
        # Display help if no arguments, see:
        # https://github.com/docopt/docopt/issues/420#issuecomment-405018014
        sys.argv.append("--help")

    args = docopt(__doc__)

    print(title())

    if args["poem"]:
        return print(poem())

    # API
    algod_client = build_algod_client(test=args["--test"])
    indexer_client = build_indexer_client(test=args["--test"])

    if args["--test"]:
        crown_nft_id = TEST_CROWN_ID
        sceptre_nft_id = TEST_SCEPTRE_ID
        algorealm_app_id = TEST_ALGOREALM_APP_ID
        algorealm_contract = TEST_ALGOREALM_LAW_BYTECODE
        algorealm_first_round = TEST_ALGOREALM_FIRST_BLOCK
    else:
        crown_nft_id = CROWN_ID
        sceptre_nft_id = SCEPTRE_ID
        algorealm_app_id = ALGOREALM_APP_ID
        algorealm_contract = ALGOREALM_LAW_BYTECODE
        algorealm_first_round = ALGOREALM_FIRST_BLOCK

    # CLI
    if args["dynasty"]:
        claims = query.claims_history(
            client=indexer_client,
            algorealm_app_id=algorealm_app_id,
            algorealm_first_round=algorealm_first_round,
        )

        print("\t\t\t\t*** DYNASTY ***\n")
        return print(*["\n", *query.dynasty(claims)])

    if args["longevity"]:
        claims = query.claims_history(
            client=indexer_client,
            algorealm_app_id=algorealm_app_id,
            algorealm_first_round=algorealm_first_round,
        )
        latest_block = algod_client.status()["last-round"]

        if args["--crown"]:
            majesty_title = "👑 RANDOMIC"
            claim_select = "Crown"
        else:
            majesty_title = "🪄 VERIFIABLE"
            claim_select = "Sceptre"

        majesty_longevity = query.longevity(claims, latest_block, claim_select)

        longevity_table = PrettyTable()
        longevity_table.field_names = ["Majesty Name", "Longevity (blocks)"]
        longevity_table.add_rows(
            [[claim["name"], claim["longevity"]] for claim in majesty_longevity]
        )

        print(f"\t\t*** {majesty_title} MAJESTY LONGEVITY ***\n")
        return print(longevity_table)

    if args["braveness"]:
        claims = query.claims_history(
            client=indexer_client,
            algorealm_app_id=algorealm_app_id,
            algorealm_first_round=algorealm_first_round,
        )

        if args["--crown"]:
            majesty_title = "👑 RANDOMIC"
            claim_select = "Crown"
        else:
            majesty_title = "🪄 VERIFIABLE"
            claim_select = "Sceptre"

        majesty_braveness = query.braveness(claims, claim_select)

        braveness_table = PrettyTable()
        braveness_table.field_names = ["Majesty Name", "Braveness"]
        braveness_table.add_rows(
            [[claim["name"], claim["braveness"]] for claim in majesty_braveness]
        )

        print(f"\t\t*** {majesty_title} MAJESTY BRAVENESS ***\n")
        return print(braveness_table)

    if args["claim-majesty"]:
        majesty_name = args["<majesty-name>"]

        if args["--crown"]:
            proclaim = (
                f"\n👑 Glory to {majesty_name}, the Randomic Majesty of Algorand! 🎉\n"
            )
            claim_select = "Crown"
            nft_id = crown_nft_id
        else:
            proclaim = (
                f"\n🪄 Glory to {majesty_name}, the Verifiable Majesty of Algorand! 🎉\n"
            )
            claim_select = "Sceptre"
            nft_id = sceptre_nft_id

        user = actions.get_user()
        algorealm_law = actions.get_contract_account(algorealm_contract)
        current_owner = query.current_owner(
            indexer_client, nft_id, algorealm_first_round
        )
        donation = int(args["<microalgos>"])
        nft_name = algod_client.asset_info(nft_id)["params"]["name"]

        opted_in = False
        while not opted_in:
            optin_choice = input(
                f"Do you want to opt-in the {nft_name} (ID: {nft_id})? (Y/n)"
            )
            if optin_choice.lower() == "y":
                actions.opt_in_algorealm_nft(algod_client, user, nft_id)
                opted_in = True
            elif optin_choice.lower() == "n":
                opted_in = True

        print(f"Claiming the {nft_name} as donating {donation / 10 ** 6} ALGO...\n")
        try:
            actions.claim_algorealm_nft(
                client=algod_client,
                algorealm_app_id=algorealm_app_id,
                algorealm_law=algorealm_law,
                user=user,
                current_owner=current_owner,
                claim_select=claim_select,
                majesty_name=majesty_name,
                donation_amount=donation,
                nft_id=nft_id,
            )
            return print(proclaim)
        except AlgodHTTPError:
            quit(
                "\n☹️ Were you too stingy? Only generous hearts will rule "
                "over Algorand Realm!\n️"
            )

    elif args["claim-card"]:
        if algod_client.status()["last-round"] <= ALGOREALM_CARD_FIRST_BLOCK:
            return print(
                "🔐 The spell can be broken starting from the block "
                f"{ALGOREALM_CARD_FIRST_BLOCK}... ⏳\n"
            )

        user = actions.get_user()
        card_contract = actions.get_contract_account(CARD_CONTRACT_BYTECODE)
        card_contract_info = algod_client.account_info(card_contract.lsig.address())
        nft_name = algod_client.asset_info(CARD_ID)["params"]["name"]

        assets = card_contract_info["assets"]

        card_nft = list(filter(lambda asset: asset["asset-id"] == CARD_ID, assets))[0]

        if card_nft["amount"] == 0:
            return print(
                "🔓 The enchanted coffer is empty! "
                "The AlgoRealm Special Card has been claimed!\n"
            )

        opted_in = False
        while not opted_in:
            optin_choice = input(
                f"Do you want to opt-in the {nft_name} (ID: {CARD_ID})? (Y/n)"
            )
            if optin_choice.lower() == "y":
                actions.opt_in_algorealm_nft(algod_client, user, CARD_ID)
                opted_in = True
            elif optin_choice.lower() == "n":
                opted_in = True

        print("\n✨ Whispering words of wisdom...")
        try:
            actions.claim_card(algod_client, card_contract, user)
            return print(
                f"\n � The spell has been broken! "
                f"The AlgoRealm Special Card is yours! 🎉\n"
            )
        except AlgodHTTPError:
            quit(
                "\nOnly the generous heart of the Great Majesty of Algorand "
                "can break the spell!\n"
                "Conquer both the 👑 Crown of Entropy and the 🪄 Sceptre "
                "of Proof first!\n"
            )

    if args["buy-order"]:
        user = actions.get_user()
        card_contract = actions.get_contract_account(CARD_CONTRACT_BYTECODE)
        nft_name = algod_client.asset_info(CARD_ID)["params"]["name"]

        opted_in = False
        while not opted_in:
            optin_choice = input(
                f"Do you want to opt-in the {nft_name} (ID: {CARD_ID})? (Y/n)"
            )
            if optin_choice.lower() == "y":
                actions.opt_in_algorealm_nft(algod_client, user, CARD_ID)
                opted_in = True
            elif optin_choice.lower() == "n":
                opted_in = True

        amount = int(args["<microalgos>"])

        print(f"✏️ Placing order of: {util.microalgos_to_algos(amount)} ALGO\n")

        seller_address = query.current_owner(
            indexer_client, CARD_ID, ALGOREALM_CARD_FIRST_BLOCK
        )

        trade_gtxn = actions.card_order(
            client=algod_client,
            card_contract=card_contract,
            buyer=user,
            seller_address=seller_address,
            royalty_collector_1_addr=ROYALTY_COLLECTOR_1,
            royalty_collector_2_addr=ROYALTY_COLLECTOR_2,
            price=amount,
        )
        print("📝 Partially signed trade group transaction saved as: 'trade.gtxn'\n")

        if args["--notify"]:
            print("✉️  Sending buy order notification to the Seller...\n")
            result = actions.notify(algod_client, user, seller_address, trade_gtxn)
            tx_id = result.tx_ids[0]
            print("\n📄 Buy order notification:\n" "https://algoexplorer.io/tx/" + tx_id)
        return print("📦 Send `trade.gtxn` file to the Seller to finalize the trade!\n")

    if args["verify-order"]:
        card_contract = actions.get_contract_account(CARD_CONTRACT_BYTECODE)
        trade_gtxn = retrieve_from_file("trade.gtxn")

        verified_buy_order = actions.verify_buy_order(
            card_contract=card_contract,
            seller_address=args["<seller-address>"],
            royalty_collector_1_addr=ROYALTY_COLLECTOR_1,
            royalty_collector_2_addr=ROYALTY_COLLECTOR_2,
            trade_gtxn=trade_gtxn,
        )
        return print(actions.order_summary(algod_client, verified_buy_order))

    if args["sell-card"]:
        trade_gtxn = retrieve_from_file("trade.gtxn")

        print(
            f"🤝 Selling the AlgoRealm Special Card for "
            f"{trade_gtxn[2].transaction.amt / 10 ** 6} ALGO:\n"
        )

        user = actions.get_user()

        try:
            return actions.sell_card(algod_client, user, trade_gtxn)
        except AlgodHTTPError:
            quit("You must hold the 👑 Crown and the 🪄 Scepter to sell the Card!\n")

    else:
        quit("\nError: read AlgoRealm '--help'!\n")


if __name__ == "__main__":
    main()
