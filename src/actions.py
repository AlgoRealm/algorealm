import base64
import math
import sys
import traceback
from getpass import getpass

import msgpack
from algosdk.account import address_from_private_key
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    AtomicTransactionResponse,
    LogicSigTransactionSigner,
    TransactionWithSigner,
)
from algosdk.constants import MNEMONIC_LEN
from algosdk.future.transaction import (
    ApplicationNoOpTxn,
    AssetOptInTxn,
    AssetTransferTxn,
    LogicSigAccount,
    LogicSigTransaction,
    PaymentTxn,
    Transaction,
    wait_for_confirmation,
    write_to_file,
)
from algosdk.mnemonic import to_private_key
from algosdk.util import microalgos_to_algos
from algosdk.v2client.algod import AlgodClient

from const import (
    ASA_STATE_OBSERVER_APP_ID,
    CARD_ID,
    CROWN_ID,
    REWARDS_POOL,
    ROYALTY_PERC,
    SCEPTRE_ID,
)


def get_user() -> AccountTransactionSigner:
    """
    Returns:
        Algorand User Account
    """
    mnemonic_phrase = getpass(prompt="Mnemonic (word_1 word_2 ... word_25):")
    try:
        assert len(mnemonic_phrase.split()) == MNEMONIC_LEN
    except AssertionError:
        quit('\n⚠️ Enter mnemonic phrase, formatted as: "word_1 ... word_25"')
    return AccountTransactionSigner(to_private_key(mnemonic_phrase))


def get_contract_account(program) -> LogicSigTransactionSigner:
    """
    Args:
        program: TEAL bytecode

    Returns:
        Algorand Contract Account
    """
    return LogicSigTransactionSigner(
        lsig=LogicSigAccount(base64.decodebytes(program.encode()))
    )


def opt_in_algorealm_nft(
    client: AlgodClient,
    user: AccountTransactionSigner,
    nft_id: int,
) -> AtomicTransactionResponse:
    """
    Opt-In AlgoRealm NFT

    Args:
        client: Algod Client
        user: Algorand User Account
        nft_id: AlgoRealm NFT ID (Crown, Sceptre, Card)

    Returns:
        Execute NFT Opt-In transaction
    """

    user_address = address_from_private_key(user.private_key)

    atc = AtomicTransactionComposer()
    params = client.suggested_params()

    opt_in_nft_txn = AssetOptInTxn(
        sender=user_address,
        sp=params,
        index=nft_id,
    )
    atc.add_transaction(
        TransactionWithSigner(
            txn=opt_in_nft_txn,
            signer=user,
        )
    )
    return atc.execute(client=client, wait_rounds=4)


def claim_algorealm_nft(
    client: AlgodClient,
    algorealm_app_id: int,
    algorealm_law: LogicSigTransactionSigner,
    user: AccountTransactionSigner,
    current_owner: str,
    claim_select: str,
    majesty_name: str,
    donation_amount: int,
    nft_id: int,
) -> AtomicTransactionResponse:
    """
    Claim AlgoRealm Majesty Title and NFT

    Args:
        client: Algod Client
        algorealm_app_id: AlgoRealm Application ID
        algorealm_law: AlgoRealm Contract Account
        user: Algorand User Account
        current_owner: Address of current NFT owner (Crown, Sceptre)
        claim_select: Title selector (Crown, Sceptre)
        majesty_name: New Majesty nickname
        donation_amount: New Majesty donation to the Rewards Pool
        nft_id: AlgoRealm NFT ID (Crown, Sceptre)

    Returns:

    """
    assert claim_select == "Crown" or claim_select == "Sceptre"

    user_address = address_from_private_key(user.private_key)

    atc = AtomicTransactionComposer()
    params = client.suggested_params()

    claim_nft_txn = ApplicationNoOpTxn(
        sender=user_address,
        sp=params,
        index=algorealm_app_id,
        app_args=[claim_select.encode(), majesty_name.encode()],
    )
    atc.add_transaction(
        TransactionWithSigner(
            txn=claim_nft_txn,
            signer=user,
        )
    )

    donation_txn = PaymentTxn(
        sender=user_address,
        sp=params,
        receiver=REWARDS_POOL,
        amt=donation_amount,
    )
    atc.add_transaction(
        TransactionWithSigner(
            txn=donation_txn,
            signer=user,
        )
    )

    nft_transfer = AssetTransferTxn(
        sender=algorealm_law.lsig.address(),
        sp=params,
        receiver=user_address,
        amt=1,
        index=nft_id,
        revocation_target=current_owner,
    )
    atc.add_transaction(
        TransactionWithSigner(
            txn=nft_transfer,
            signer=algorealm_law,
        )
    )
    return atc.execute(client=client, wait_rounds=4)


def proof_asa_amount_eq_txn(
    client: AlgodClient,
    owner_address: str,
    asa_id: int,
    asa_amount: int,
) -> ApplicationNoOpTxn:

    params = client.suggested_params()

    method = "AsaAmountEq"

    return ApplicationNoOpTxn(
        sender=owner_address,
        sp=params,
        index=ASA_STATE_OBSERVER_APP_ID,
        app_args=[method.encode(), asa_amount],
        foreign_assets=[asa_id],
        accounts=[owner_address],
    )


def claim_card(
    client: AlgodClient,
    card_contract: LogicSigTransactionSigner,
    user: AccountTransactionSigner,
) -> AtomicTransactionResponse:

    user_address = address_from_private_key(user.private_key)

    atc = AtomicTransactionComposer()
    params = client.suggested_params()

    proof_crown_ownership = proof_asa_amount_eq_txn(
        client=client,
        owner_address=user_address,
        asa_id=CROWN_ID,
        asa_amount=1,
    )
    atc.add_transaction(TransactionWithSigner(txn=proof_crown_ownership, signer=user))

    proof_sceptre_ownership = proof_asa_amount_eq_txn(
        client=client,
        owner_address=user_address,
        asa_id=SCEPTRE_ID,
        asa_amount=1,
    )
    atc.add_transaction(TransactionWithSigner(txn=proof_sceptre_ownership, signer=user))

    nft_card_xfer = AssetTransferTxn(
        sender=card_contract.lsig.address(),
        sp=params,
        receiver=user_address,
        amt=1,
        index=CARD_ID,
        revocation_target=card_contract.lsig.address(),
    )
    atc.add_transaction(
        TransactionWithSigner(
            txn=nft_card_xfer,
            signer=card_contract,
        )
    )
    return atc.execute(client=client, wait_rounds=4)


def card_order(
    client: AlgodClient,
    card_contract: LogicSigTransactionSigner,
    buyer: AccountTransactionSigner,
    seller_address: str,
    royalty_collector_1_addr: str,
    royalty_collector_2_addr: str,
    price: int,
) -> list[Transaction]:

    buyer_address = address_from_private_key(buyer.private_key)

    proof_crown_ownership = proof_asa_amount_eq_txn(
        client=client,
        owner_address=seller_address,
        asa_id=CROWN_ID,
        asa_amount=1,
    )

    proof_sceptre_ownership = proof_asa_amount_eq_txn(
        client=client,
        owner_address=seller_address,
        asa_id=SCEPTRE_ID,
        asa_amount=1,
    )

    params = client.suggested_params()

    nft_card_payment = PaymentTxn(
        sender=buyer_address,
        sp=params,
        receiver=seller_address,
        amt=price,
    )

    royalty_amount = math.ceil(price * ROYALTY_PERC / 100)

    royalty_1_payment = PaymentTxn(
        sender=seller_address,
        sp=params,
        receiver=royalty_collector_1_addr,
        amt=royalty_amount,
    )

    royalty_2_payment = PaymentTxn(
        sender=seller_address,
        sp=params,
        receiver=royalty_collector_2_addr,
        amt=royalty_amount,
    )

    nft_card_xfer = AssetTransferTxn(
        sender=card_contract.lsig.address(),
        sp=params,
        receiver=buyer_address,
        amt=1,
        index=CARD_ID,
        revocation_target=seller_address,
    )

    trade_gtxn = [
        proof_crown_ownership,
        proof_sceptre_ownership,
        nft_card_payment,
        royalty_1_payment,
        royalty_2_payment,
        nft_card_xfer,
    ]

    sig_nft_card_payment = trade_gtxn[2].sign(buyer.private_key)
    sig_nft_card_xfer = LogicSigTransaction(trade_gtxn[5], card_contract.lsig)
    trade_gtxn[2] = sig_nft_card_payment
    trade_gtxn[5] = sig_nft_card_xfer
    write_to_file(trade_gtxn, "trade.gtxn", overwrite=True)

    return trade_gtxn


def notify(
    client: AlgodClient,
    user: AccountTransactionSigner,
    seller_address: str,
    trade_gtxn: list[Transaction],
) -> AtomicTransactionResponse:
    user_address = address_from_private_key(user.private_key)

    atc = AtomicTransactionComposer()
    params = client.suggested_params()

    note = {
        "buy_order": "AlgoRealm Special Card",
        "asset_id": CARD_ID,
        "algo_amount": microalgos_to_algos(trade_gtxn[2].amt),
        "algo_royalty": microalgos_to_algos(trade_gtxn[3].amt + trade_gtxn[4].amt),
        "last_valid_block": trade_gtxn[2].last_valid_round,
    }

    bytes_note = msgpack.packb(note)

    notification_txn = PaymentTxn(
        sender=user_address,
        sp=params,
        receiver=seller_address,
        amt=0,
        note=bytes_note,
    )
    atc.add_transaction(
        TransactionWithSigner(
            txn=notification_txn,
            signer=user,
        )
    )

    return atc.execute(client=client, wait_rounds=4)


def sell_card(
    client: AlgodClient,
    user: AccountTransactionSigner,
    trade_gtxn: list,
) -> dict:

    signed_crown_proof = trade_gtxn[0].sign(user.private_key)
    signed_sceptre_proof = trade_gtxn[1].sign(user.private_key)
    signed_royalty_1 = trade_gtxn[3].sign(user.private_key)
    signed_royalty_2 = trade_gtxn[4].sign(user.private_key)

    trade_gtxn[0] = signed_crown_proof
    trade_gtxn[1] = signed_sceptre_proof
    trade_gtxn[3] = signed_royalty_1
    trade_gtxn[4] = signed_royalty_2

    gtxn_id = client.send_transactions(trade_gtxn)
    return wait_for_confirmation(client, gtxn_id, wait_rounds=4)


def verify_buy_order(
    card_contract: LogicSigTransactionSigner,
    seller_address: str,
    royalty_collector_1_addr: str,
    royalty_collector_2_addr: str,
    trade_gtxn: list,
) -> list:
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
        assert trade_gtxn[3].receiver == royalty_collector_1_addr
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
        assert trade_gtxn[4].receiver == royalty_collector_2_addr
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
        assert trade_gtxn[5].transaction.sender == card_contract.lsig.address()
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


def order_summary(client: AlgodClient, trade_gtxn: list) -> str:
    current_round = client.status()["last-round"]
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
