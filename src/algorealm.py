"""
AlgoRealm, only generous heart will ever rule over Algorand. (by cusma)

Usage:
  algorealm.py poem
  algorealm.py dynasty
  algorealm.py verify-order <seller-address>
  algorealm.py claim-crown <mnemonic> <majesty-name> <microalgos>
  algorealm.py claim-sceptre <mnemonic> <majesty-name> <microalgos>
  algorealm.py claim-card <mnemonic>
  algorealm.py buy-order <mnemonic> <microalgos> [--notify]
  algorealm.py sell-card <mnemonic>
  algorealm.py [--help]

Commands:
  poem             AlgoRealm's poem.
  dynasty          Print the glorious dynasty of AlgoRealm's Majesties.
  verify-order     Verify the partially signed AlgoRealm Card buy order.
  claim-crown      Claim the Crown of Entropy, become the Randomic Majesty of Algorand.
  claim-sceptre    Claim the Sceptre of Proof, become the Verifiable Majesty of Algorand.
  claim-card       Brake the spell and claim the AlgoRealm Card by AlgoWorld.
  buy-order        Place an order for the AlgoRealm Card.
  sell-card        Sell the AlgoRealm Card (paying a 10% royalty).

Options:
  -n --notify      Notify the Seller about your buy order on-chain.
  -h --help
"""

import base64
import dataclasses
import math
import sys
import time
import traceback

import msgpack
from algosdk import account, mnemonic, util
from algosdk.error import AlgodHTTPError, IndexerHTTPError
from algosdk.future import transaction
from algosdk.v2client import algod, indexer
from docopt import docopt


@dataclasses.dataclass
class Account:
    address: str
    private_key: str
    lsig: transaction.LogicSig = None

    def mnemonic(self) -> str:
        return mnemonic.from_private_key(self.private_key)

    def is_lsig(self):
        return not self.private_key and self.lsig

    @classmethod
    def create_account(cls):
        private_key, address = account.generate_account()
        return cls(private_key=private_key, address=address)


# --- Config
MAX_CONNECTION_ATTEMPTS = 10
CONNECTION_ATTEMPT_DELAY_SEC = 2

INDEXER_ADDRESS = "https://mainnet-idx.algonode.cloud"
ALGOD_ADDRESS = "https://mainnet-api.algonode.cloud"

REWARDS_POOL = "737777777777777777777777777777777777777777777777777UFEJ2CI"

ALGOREALM_FIRST_BLOCK = 13578170
ALGOREALM_APP_ID = 137491307
CROWN_ID = 137493252
SCEPTRE_ID = 137494385

ALGOREALM_LAW_BYTECODE = (
    "AiAIAwbr5sdBAQSE9sdB8f7HQegHJgEg/v////////////////////////////////////"
    "////8yBCISMwAQIxIzABgkEhAQMwEQJRIzAQAzAAASEDMBBygSEBAzAhAhBBIzAhQzAQAS"
    "EDMCESEFEjMCESEGEhEQMwISJRIQMwIBIQcOEDMCFTIDEhAzAiAyAxIQEA=="
)

ALGOREALM_LAW_LSIG = transaction.LogicSig(
    base64.decodebytes(ALGOREALM_LAW_BYTECODE.encode())
)

ALGOREALM_LAW = Account(
    address=ALGOREALM_LAW_LSIG.address(),
    private_key=None,
    lsig=ALGOREALM_LAW_LSIG,
)

ALGOREALM_CARD_FIRST_BLOCK = 16250000
ROYALTY_PERC = 5
ROYALTY_COLLECTOR_1 = Account(
    address="H7N65NZIWBOKFDSRNPLLDGN72HVFKXT4RRSY7M66B6Y2PFLQFKLPLHU5JU", private_key=""
)
ROYALTY_COLLECTOR_2 = Account(
    address="2PDM3E7WLVPMEKCCMNTHM3FCZNZM4CSJQUOC4SWHMFPAR3N4NXBLCQKHPE", private_key=""
)
ASA_STATE_OBSERVER_APP_ID = 321230622
CARD_ID = 321172366
CARD_CONTRACT_BYTECODE = (
    "AyAOAQMGBOgHnq6WmQGE9sdB8f7HQQVkjueSmQGQ6d8HAM7i0wcmAwtBc2FBbW91bnRFcS"
    "A/2+63KLBcoo5Ra9axmb/R6lVefIxlj7PeD7GnlXAqliDTxs2T9l1ewihCY2Z2bKLLcs4K"
    "SYUcLkrHYV4I7bxtwjIEIhJAAaIyBCMSQAD4MgQkEkAAAQAzABAkEjMBECQSEDMCECISED"
    "MDECISEDMEECISEDMFECUSEDMFASEEDhAzBSAyAxIQMwUVMgMSEDMAGCEFEjcAGgAoEhA3"
    "ABwBMwAAEhA3ADAAIQYSEDcAGgEiFhIQEDMBGCEFEjcBGgAoEhA3ARwBMwEAEhA3ATAAIQ"
    "cSEDcBGgEiFhIQEDMAADMCBxIQMwEAMwIHEhAzAgAzBRQSEDMDADMCBxIQMwMHKRIQMwQA"
    "MwIHEhAzBAcqEhAzAwgzBAgSEDMDCDMCCCEICyEJCg8QMwURIQoSEDMFEiISEDMFEzMCBx"
    "IQMwUUMwIAEhBCANczABAkEjMBECQSEDMCECUSEDMCASEEDhAzAiAyAxIQMwIVMgMSEDMA"
    "GCEFEjcAGgAoEhA3ABwBMwAAEhA3ADAAIQYSEDcAGgEiFhIQEDMBGCEFEjcBGgAoEhA3AR"
    "wBMwEAEhA3ATAAIQcSEDcBGgEiFhIQEDMAADMCFBIQMwEAMwIUEhAzAgIhCw0QMwIRIQoS"
    "EDMCEiISEDMCADMCExIQQgA0MRAlEjEBIQQOEDETMgMSEDEVMgMSEDEgMgMSEDERIQoSED"
    "ESIQwSEDEAMRQSEDEEIQ0MEA=="
)

CARD_CONTRACT_LSIG = transaction.LogicSig(
    base64.decodebytes(CARD_CONTRACT_BYTECODE.encode())
)

CARD_CONTRACT = Account(
    address=CARD_CONTRACT_LSIG.address(),
    private_key=None,
    lsig=CARD_CONTRACT_LSIG,
)


def wait_for_confirmation(client: algod.AlgodClient, txid: str):
    """
    Utility function to wait until the transaction is confirmed before
    proceeding.
    """
    last_round = client.status().get("last-round")
    txinfo = client.pending_transaction_info(txid)

    while not txinfo.get("confirmed-round", -1) > 0:
        print(f"Waiting for transaction {txid} confirmation.")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)

    print(f"Transaction {txid} confirmed in round {txinfo.get('confirmed-round')}.")
    return txinfo


def sign(account: Account, txn: transaction.Transaction):
    if account.is_lsig():
        return transaction.LogicSigTransaction(txn, account.lsig)
    else:
        assert account.private_key
        return txn.sign(account.private_key)


def sign_send_wait(algod_client: algod.AlgodClient, account: Account, txn):
    """Sign a transaction, submit it, and wait for its confirmation."""
    signed_txn = sign(account, txn)
    tx_id = signed_txn.transaction.get_txid()
    algod_client.send_transactions([signed_txn])
    wait_for_confirmation(algod_client, tx_id)
    return algod_client.pending_transaction_info(tx_id)


def group_and_sign(signers, txns):
    assert len(signers) == len(txns)

    signed_group = []
    gid = transaction.calculate_group_id(txns)

    for signer, t in zip(signers, txns):
        t.group = gid
        signed_group.append(sign(signer, t))

    return signed_group


def search_algorelm_calls(indexer_client: indexer.IndexerClient):
    nexttoken = ""
    numtx = 1
    calls = []
    while numtx > 0:
        result = indexer_client.search_transactions(
            limit=1000,
            next_page=nexttoken,
            application_id=ALGOREALM_APP_ID,
            min_round=ALGOREALM_FIRST_BLOCK,
        )
        calls += result["transactions"]
        numtx = len(result["transactions"])
        if numtx > 0:
            # pointer to the next chunk of requests
            nexttoken = result["next-token"]
    return calls


def search_algorelm_nft_txns(indexer_client: indexer.IndexerClient, nft_id: int):
    nexttoken = ""
    numtx = 1
    txns = []
    while numtx > 0:
        result = indexer_client.search_asset_transactions(
            asset_id=nft_id,
            limit=1000,
            next_page=nexttoken,
            txn_type="axfer",
            min_round=ALGOREALM_FIRST_BLOCK,
        )
        txns += result["transactions"]
        numtx = len(result["transactions"])
        if numtx > 0:
            # pointer to the next chunk of requests
            nexttoken = result["next-token"]
    return txns


def history(indexer_client: indexer.IndexerClient):
    attempts = 1
    algorealm_calls = None
    while attempts <= MAX_CONNECTION_ATTEMPTS:
        try:
            algorealm_calls = search_algorelm_calls(indexer_client)
            break
        except IndexerHTTPError:
            print(
                f"Indexer Client connection attempt "
                f"{attempts}/{MAX_CONNECTION_ATTEMPTS}"
            )
            print("Trying to contact Indexer Client again...")
            time.sleep(CONNECTION_ATTEMPT_DELAY_SEC)
        finally:
            attempts += 1
    if not algorealm_calls:
        quit("❌ Unable to connect to Indexer Client. Check your API token!")

    claims_history = []
    name = ""
    claim = ""
    for call in algorealm_calls:
        call_args = call["application-transaction"]["application-args"]
        # Check is an NFT claim call
        if len(call_args) == 2:
            block = call["confirmed-round"]
            nft = call_args[0].encode()
            donation = call["global-state-delta"][0]["value"]["uint"]
            # Check is a different claimer (2 elements in the state delta)
            if len(call["global-state-delta"]) == 2:
                name = base64.b64decode(
                    call["global-state-delta"][1]["value"]["bytes"]
                ).decode()
            if nft == base64.b64encode(b"Crown"):
                claim = (
                    f"👑 {name} claimed the Crown of Entropy\n"
                    f"on Block: {block} donating: {donation} microALGOs "
                    f"to the Rewards Pool.\n\n"
                )
            elif nft == base64.b64encode(b"Sceptre"):
                claim = (
                    f"🪄 {name} claimed the Sceptre of Proof\n"
                    f"on Block: {block} donating: {donation} microALGOs "
                    f"to the Rewards Pool.\n\n"
                )
            else:
                pass

            claims_history += [claim]

        else:
            pass

    return claims_history


def current_owner(indexer_client: indexer.IndexerClient, nft_id: int):
    attempts = 1
    nft_txns = None
    while attempts <= MAX_CONNECTION_ATTEMPTS:
        try:
            nft_txns = search_algorelm_nft_txns(indexer_client, nft_id)
            break
        except IndexerHTTPError:
            print(
                f"Indexer Client connection attempt "
                f"{attempts}/{MAX_CONNECTION_ATTEMPTS}"
            )
            print("Trying to contact Indexer Client again...")
            time.sleep(CONNECTION_ATTEMPT_DELAY_SEC)
        finally:
            attempts += 1
    if not nft_txns:
        quit("❌ Unable to connect to Indexer Client. Check your API token!")

    nft_txns.reverse()
    for txn in nft_txns:
        if txn["asset-transfer-transaction"]["amount"] == 1:
            return txn["asset-transfer-transaction"]["receiver"]


def opt_in(
    algod_client: algod.AlgodClient,
    user: Account,
    nft_id: int,
):
    nft_name = algod_client.asset_info(nft_id)["params"]["name"]
    optin = ""
    while not optin:
        optin = str(
            input(f"Do you want to opt-in the {nft_name} (ID: {nft_id})? (Y/n) ")
        )
        print("")
        if optin.lower() == "y":
            params = algod_client.suggested_params()

            opt_in_txn = transaction.AssetOptInTxn(
                sender=user.address,
                sp=params,
                index=nft_id,
            )
            return sign_send_wait(algod_client, user, opt_in_txn)

        elif optin.lower() == "n":
            return
        else:
            optin = ""


def claim_nft(
    algod_client: algod.AlgodClient,
    indexer_client: indexer.IndexerClient,
    claimer: Account,
    claim_arg: str,
    new_majesty: str,
    donation_amount: int,
    nft_id: int,
):
    params = algod_client.suggested_params()

    claim_txn = transaction.ApplicationNoOpTxn(
        sender=claimer.address,
        sp=params,
        index=ALGOREALM_APP_ID,
        app_args=[claim_arg.encode(), new_majesty.encode()],
    )

    donation_txn = transaction.PaymentTxn(
        sender=claimer.address,
        sp=params,
        receiver=REWARDS_POOL,
        amt=donation_amount,
    )

    nft_transfer = transaction.AssetTransferTxn(
        sender=ALGOREALM_LAW.address,
        sp=params,
        receiver=claimer.address,
        amt=1,
        index=nft_id,
        revocation_target=current_owner(indexer_client, nft_id),
    )

    signed_group = group_and_sign(
        [claimer, claimer, ALGOREALM_LAW],
        [claim_txn, donation_txn, nft_transfer],
    )

    nft_name = algod_client.asset_info(nft_id)["params"]["name"]

    print(
        f"Claiming the {nft_name} as {new_majesty}, "
        f"donating {donation_amount / 10 ** 6} ALGO...\n"
    )
    try:
        gtxn_id = algod_client.send_transactions(signed_group)
        wait_for_confirmation(algod_client, gtxn_id)
    except AlgodHTTPError:
        quit(
            "\n☹️  Were you too stingy? Only generous hearts will rule over "
            "Algorand Realm!\n️"
        )


def proof_asa_amount_eq_txn(
    algod_client: algod.AlgodClient,
    sender: Account,
    asa_id: int,
    asa_amount: int,
):
    params = algod_client.suggested_params()

    proof_txn = transaction.ApplicationNoOpTxn(
        sender=sender.address,
        sp=params,
        index=ASA_STATE_OBSERVER_APP_ID,
        app_args=["AsaAmountEq".encode(), asa_amount],
        foreign_assets=[asa_id],
        accounts=[sender.address],
    )
    return proof_txn


def claim_card(algod_client: algod.AlgodClient, claimer: Account):
    params = algod_client.suggested_params()

    proof_crown_ownership = proof_asa_amount_eq_txn(
        algod_client=algod_client,
        sender=claimer,
        asa_id=CROWN_ID,
        asa_amount=1,
    )

    proof_sceptre_ownership = proof_asa_amount_eq_txn(
        algod_client=algod_client,
        sender=claimer,
        asa_id=SCEPTRE_ID,
        asa_amount=1,
    )

    nft_card_xfer = transaction.AssetTransferTxn(
        sender=CARD_CONTRACT.address,
        sp=params,
        receiver=claimer.address,
        amt=1,
        index=CARD_ID,
        revocation_target=CARD_CONTRACT.address,
    )

    signed_group = group_and_sign(
        [claimer, claimer, CARD_CONTRACT],
        [proof_crown_ownership, proof_sceptre_ownership, nft_card_xfer],
    )

    try:
        gtxn_id = algod_client.send_transactions(signed_group)
        wait_for_confirmation(algod_client, gtxn_id)
    except AlgodHTTPError:
        quit(
            "\nOnly the generous heart of the Great Majesty of Algorand "
            "can break the spell!\n"
            "Conquer both the 👑 Crown of Entropy and the 🪄 Sceptre "
            "of Proof first!\n"
        )


def card_order(
    algod_client: algod.AlgodClient,
    buyer: Account,
    seller: Account,
    price: int,
):
    params = algod_client.suggested_params()

    proof_crown_ownership = proof_asa_amount_eq_txn(
        algod_client=algod_client,
        sender=seller,
        asa_id=CROWN_ID,
        asa_amount=1,
    )

    proof_sceptre_ownership = proof_asa_amount_eq_txn(
        algod_client=algod_client,
        sender=seller,
        asa_id=SCEPTRE_ID,
        asa_amount=1,
    )

    nft_card_payment = transaction.PaymentTxn(
        sender=buyer.address,
        sp=params,
        receiver=seller.address,
        amt=price,
    )

    royalty_amount = math.ceil(price * ROYALTY_PERC / 100)

    royalty_1_payment = transaction.PaymentTxn(
        sender=seller.address,
        sp=params,
        receiver=ROYALTY_COLLECTOR_1.address,
        amt=royalty_amount,
    )

    royalty_2_payment = transaction.PaymentTxn(
        sender=seller.address,
        sp=params,
        receiver=ROYALTY_COLLECTOR_2.address,
        amt=royalty_amount,
    )

    nft_card_xfer = transaction.AssetTransferTxn(
        sender=CARD_CONTRACT.address,
        sp=params,
        receiver=buyer.address,
        amt=1,
        index=CARD_ID,
        revocation_target=seller.address,
    )

    trade_gtxn = [
        proof_crown_ownership,
        proof_sceptre_ownership,
        nft_card_payment,
        royalty_1_payment,
        royalty_2_payment,
        nft_card_xfer,
    ]

    transaction.assign_group_id(trade_gtxn)
    signed_nft_card_payment = trade_gtxn[2].sign(buyer.private_key)
    trade_gtxn[2] = signed_nft_card_payment
    trade_gtxn[5] = transaction.LogicSigTransaction(trade_gtxn[5], CARD_CONTRACT.lsig)
    transaction.write_to_file(trade_gtxn, "trade_raw.gtxn", overwrite=True)

    print("📝 Partially signed trade group transaction saved as: 'trade.gtxn'\n")

    return trade_gtxn


def notify(
    algod_client: algod.AlgodClient, user: Account, seller: Account, trade_gtxn: list
):
    params = algod_client.suggested_params()

    note = {
        "buy_order": "AlgoRealm Special Card",
        "asset_id": CARD_ID,
        "algo_amount": trade_gtxn[2].transaction.amt / 10**6,
        "algo_royalty": (trade_gtxn[3].amt + trade_gtxn[4].amt) / 10**6,
        "last_valid_block": trade_gtxn[2].transaction.last_valid_round,
    }

    bytes_note = msgpack.packb(note)

    notification_txn = transaction.PaymentTxn(
        sender=user.address,
        sp=params,
        receiver=seller.address,
        amt=0,
        note=bytes_note,
    )

    signed_txn = sign(user, notification_txn)
    tx_id = signed_txn.transaction.get_txid()
    print("✉️  Sending buy order notification to the Seller...\n")
    algod_client.send_transactions([signed_txn])
    wait_for_confirmation(algod_client, tx_id)
    print("\n📄 Buy order notification:\n" "https://algoexplorer.io/tx/" + tx_id)


def verify_buy_order(seller_address: str):
    trade_gtxn = transaction.retrieve_from_file("trade_raw.gtxn")

    # Check TXN 0: Crown Proof of Ownership
    try:
        assert trade_gtxn[0].type == "appl"
        assert trade_gtxn[0].index == ASA_STATE_OBSERVER_APP_ID
        assert trade_gtxn[0].app_args[0] == b"AsaAmountEq"
        assert trade_gtxn[0].app_args[1] == b"\x00\x00\x00\x00\x00\x00\x00\x01"
        assert trade_gtxn[0].foreign_assets[0] == CROWN_ID
        assert trade_gtxn[0].accounts[0] == seller_address
        assert trade_gtxn[0].sender == seller_address
        assert trade_gtxn[0].fee <= 1000
        assert trade_gtxn[0].rekey_to is None
    except AssertionError:
        _, _, tb = sys.exc_info()
        tb_info = traceback.extract_tb(tb)
        filename, line, func, text = tb_info[-1]
        quit("Transaction 0 - Crown Proof of Ownership is invalid: {}".format(text))

    # Check TXN 1: Sceptre Proof of Ownership
    try:
        assert trade_gtxn[1].type == "appl"
        assert trade_gtxn[1].index == ASA_STATE_OBSERVER_APP_ID
        assert trade_gtxn[1].app_args[0] == b"AsaAmountEq"
        assert trade_gtxn[1].app_args[1] == b"\x00\x00\x00\x00\x00\x00\x00\x01"
        assert trade_gtxn[1].foreign_assets[0] == SCEPTRE_ID
        assert trade_gtxn[1].accounts[0] == seller_address
        assert trade_gtxn[1].sender == seller_address
        assert trade_gtxn[1].fee <= 1000
        assert trade_gtxn[1].rekey_to is None
    except AssertionError:
        _, _, tb = sys.exc_info()
        tb_info = traceback.extract_tb(tb)
        filename, line, func, text = tb_info[-1]
        quit("Transaction 1 - Sceptre Proof of Ownership is invalid: {}".format(text))

    # Check TXN 2: Card Payment
    try:
        assert trade_gtxn[2].transaction.type == "pay"
        assert trade_gtxn[2].transaction.receiver == seller_address
    except AssertionError:
        _, _, tb = sys.exc_info()
        tb_info = traceback.extract_tb(tb)
        filename, line, func, text = tb_info[-1]
        quit("Transaction 2 - Card Payment is invalid: {}".format(text))

    # Check TXN 3: Royalty 1 Payment
    try:
        assert trade_gtxn[3].type == "pay"
        assert trade_gtxn[3].sender == seller_address
        assert trade_gtxn[3].receiver == ROYALTY_COLLECTOR_1.address
        assert trade_gtxn[3].fee <= 1000
        assert trade_gtxn[3].rekey_to is None
    except AssertionError:
        _, _, tb = sys.exc_info()
        tb_info = traceback.extract_tb(tb)
        filename, line, func, text = tb_info[-1]
        quit("Transaction 3 - Royalty 1 Payment is invalid: {}".format(text))

    # Check TXN 4: Royalty 3 Payment
    try:
        assert trade_gtxn[4].type == "pay"
        assert trade_gtxn[4].sender == seller_address
        assert trade_gtxn[4].receiver == ROYALTY_COLLECTOR_2.address
        assert trade_gtxn[4].fee <= 1000
        assert trade_gtxn[4].rekey_to is None
    except AssertionError:
        _, _, tb = sys.exc_info()
        tb_info = traceback.extract_tb(tb)
        filename, line, func, text = tb_info[-1]
        quit("Transaction 4 - Royalty 2 Payment is invalid: {}".format(text))

    # Check TXN 5: Card Transfer
    try:
        assert trade_gtxn[5].transaction.type == "axfer"
        assert trade_gtxn[5].transaction.index == CARD_ID
        assert trade_gtxn[5].transaction.amount == 1
        assert trade_gtxn[5].transaction.sender == CARD_CONTRACT.address
        assert trade_gtxn[5].transaction.receiver == trade_gtxn[2].transaction.sender
        assert trade_gtxn[5].transaction.revocation_target == seller_address
        assert trade_gtxn[5].transaction.fee <= 1000
        assert trade_gtxn[5].transaction.rekey_to is None
    except AssertionError:
        _, _, tb = sys.exc_info()
        tb_info = traceback.extract_tb(tb)
        filename, line, func, text = tb_info[-1]
        quit("Transaction 5 - Card Transfer is invalid: {}".format(text))

    return trade_gtxn


def order_summary(algod_client: algod.AlgodClient, trade_gtxn: list):

    current_round = algod_client.status()["last-round"]
    last_valid_round = trade_gtxn[2].transaction.last_valid_round
    remaning_rounds = last_valid_round - current_round
    if remaning_rounds <= 0:
        remaning_rounds = "Buy order expired!"

    return f"""
    * =========================== ORDER SUMMARY =========================== *

       BUYER:\t{trade_gtxn[2].transaction.sender}
       SELLER:\t{trade_gtxn[2].transaction.receiver}
       AMOUNT:\t{trade_gtxn[2].transaction.amt / 10 ** 6} ALGO
       ROYALTY:\t{(trade_gtxn[3].amt + trade_gtxn[4].amt) / 10 ** 6} ALGO

       BUY-ORDER VALIDITY REMAINING BLOCKS: {remaning_rounds}

    * ===================================================================== *
    """


def sell_card(algod_client: algod.AlgodClient, user: Account):
    trade_gtxn = transaction.retrieve_from_file("trade_raw.gtxn")

    signed_crown_proof = trade_gtxn[0].sign(user.private_key)
    signed_sceptre_proof = trade_gtxn[1].sign(user.private_key)
    signed_royalty_1 = trade_gtxn[3].sign(user.private_key)
    signed_royalty_2 = trade_gtxn[4].sign(user.private_key)

    trade_gtxn[0] = signed_crown_proof
    trade_gtxn[1] = signed_sceptre_proof
    trade_gtxn[3] = signed_royalty_1
    trade_gtxn[4] = signed_royalty_2

    print(
        f"🤝 Selling the AlgoRealm Special Card for "
        f"{trade_gtxn[2].transaction.amt / 10 ** 6} ALGO:\n"
    )
    try:
        gtxn_id = algod_client.send_transactions(trade_gtxn)
    except AlgodHTTPError:
        quit("You must hold the 👑 Crown and the 🪄 Scepter to sell the Card!\n")
    else:
        return wait_for_confirmation(algod_client, gtxn_id)


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
                      |  Verifiability of randomness,           |
                      |  Since genesis block,                   |
                      |  Brings Consensus over realm vastness,  |
                      |  So Algorand never fork.                |
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

    # Clients
    header = {"User-Agent": "algosdk"}

    algod_client = algod.AlgodClient(
        algod_token="", algod_address=ALGOD_ADDRESS, headers=header
    )

    indexer_client = indexer.IndexerClient(
        indexer_token="", indexer_address=INDEXER_ADDRESS, headers=header
    )

    if args["verify-order"]:
        summary = order_summary(
            algod_client, verify_buy_order(args["<seller-address>"])
        )
        return print(summary)

    if args["dynasty"]:
        print(
            r"""
                                   *** DYNASTY ***
            """
        )
        return print(*["\n", *history(indexer_client)])

    # Checking mnemonic format
    try:
        assert len(args["<mnemonic>"].split()) == 25
    except AssertionError:
        quit(
            "The mnemonic phrase must contain 25 words, "
            'formatted as: "word_1 word_2 ... word_25"\n'
        )

    private_key = mnemonic.to_private_key(args["<mnemonic>"])

    user = Account(account.address_from_private_key(private_key), private_key)

    if args["claim-crown"]:
        opt_in(algod_client, user, CROWN_ID)

        name = args["<majesty-name>"]

        claim_nft(
            algod_client=algod_client,
            indexer_client=indexer_client,
            claimer=user,
            claim_arg="Crown",
            new_majesty=name,
            donation_amount=int(args["<microalgos>"]),
            nft_id=CROWN_ID,
        )
        print(f"\n👑 Glory to {name}, the Randomic Majesty of Algorand! 🎉\n")

    elif args["claim-sceptre"]:
        opt_in(algod_client, user, SCEPTRE_ID)

        name = args["<majesty-name>"]

        claim_nft(
            algod_client=algod_client,
            indexer_client=indexer_client,
            claimer=user,
            claim_arg="Sceptre",
            new_majesty=name,
            donation_amount=int(args["<microalgos>"]),
            nft_id=SCEPTRE_ID,
        )
        print(f"\n🪄 Glory to {name}, the Verifiable Majesty of Algorand! 🎉\n")

    elif args["claim-card"]:
        if algod_client.status()["last-round"] <= ALGOREALM_CARD_FIRST_BLOCK:
            return print(
                "🔐 The spell can be broken starting from the block "
                f"{ALGOREALM_CARD_FIRST_BLOCK}... ⏳\n"
            )

        algorelm_card_contract = algod_client.account_info(CARD_CONTRACT.address)

        assets = algorelm_card_contract["assets"]

        card_nft = list(filter(lambda asset: asset["asset-id"] == CARD_ID, assets))[0]

        if card_nft["amount"] == 0:
            return print(
                "🔓 The enchanted coffer is empty! "
                "The AlgoRealm Special Card has been claimed!\n"
            )

        opt_in(algod_client, user, CARD_ID)

        print("\n✨ Whispering words of wisdom...")
        claim_card(algod_client=algod_client, claimer=user)
        print(
            f"\n � The spell has been broken! "
            f"The AlgoRealm Special Card is yours! 🎉\n"
        )

    if args["buy-order"]:
        opt_in(algod_client, user, CARD_ID)

        amount = int(args["<microalgos>"])

        print(f"✏️  Placing order of: {util.microalgos_to_algos(amount)} ALGO\n")

        seller = Account(address=current_owner(indexer_client, CARD_ID), private_key="")

        trade_gtxn = card_order(
            algod_client=algod_client, buyer=user, seller=seller, price=amount
        )

        if args["--notify"]:
            notify(algod_client, user, seller, trade_gtxn)

        return print(
            "\n📦 Send `trade.gtxn` file to the Seller to finalize the trade!\n"
        )

    if args["sell-card"]:
        sell_card(algod_client, user)

    else:
        quit("\nError: read AlgoRealm '--help'!\n")


if __name__ == "__main__":
    main()
