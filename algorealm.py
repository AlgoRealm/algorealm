"""
AlgoRealm, only generous heart will ever rule over Algorand. (by cusma)

Usage:
  algorealm.py poem
  algorealm.py dynasty <purestake-api-token>
  algorealm.py claim-crown <purestake-api-token> <mnemonic> <majesty-name> <microalgos>
  algorealm.py claim-sceptre <purestake-api-token> <mnemonic> <majesty-name> <microalgos>
  algorealm.py claim-card <purestake-api-token> <mnemonic>
  algorealm.py [--help]

Commands:
  poem             AlgoRealm's poem.
  dynasty          The Glorious Dynasty of Algorand's Majesties.
  claim-crown      Claim the Crown of Entropy, become the Randomic Majesty.
  claim-sceptre    Claim the Sceptre of Proof, become the Verifiable Majesty.
  claim-card       Brake the spell and claim the AlgoRealm Card by AlgoWorld.

Options:
  -h --help
"""

import sys
from docopt import docopt
import time
import base64
import dataclasses

from algosdk.v2client import algod, indexer
from algosdk.error import AlgodHTTPError, IndexerHTTPError
from algosdk.future import transaction
from algosdk import mnemonic, account


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

INDEXER_ADDRESS = "https://mainnet-algorand.api.purestake.io/idx2"
ALGOD_ADDRESS = "https://mainnet-algorand.api.purestake.io/ps2"

REWARDS_POOL = '737777777777777777777777777777777777777777777777777UFEJ2CI'

ALGOREALM_FIRST_BLOCK = 13578170
ALGOREALM_APP_ID = 137491307
CROWN_ID = 137493252
SCEPTRE_ID = 137494385

ALGOREALM_LAW_BYTECODE = \
    'AiAIAwbr5sdBAQSE9sdB8f7HQegHJgEg/v////////////////////////////////////' \
    '////8yBCISMwAQIxIzABgkEhAQMwEQJRIzAQAzAAASEDMBBygSEBAzAhAhBBIzAhQzAQAS' \
    'EDMCESEFEjMCESEGEhEQMwISJRIQMwIBIQcOEDMCFTIDEhAzAiAyAxIQEA=='

ALGOREALM_LAW_LSIG = transaction.LogicSig(
    base64.decodebytes(ALGOREALM_LAW_BYTECODE.encode())
)

ALGOREALM_LAW = Account(
    address=ALGOREALM_LAW_LSIG.address(),
    private_key=None,
    lsig=ALGOREALM_LAW_LSIG,
)

ALGOREALM_CARD_FIRST_BLOCK = 16250000
ASA_STATE_OBSERVER_APP_ID = 321230622
ALGOREALM_CARD_ID = 321172366
ALGOREALM_CARD_CONTRACT_BYTECODE = \
    'AyAOAQMGBOgHnq6WmQGE9sdB8f7HQQVkjueSmQGQ6d8HAM7i0wcmAwtBc2FBbW91bnRFcS' \
    'A/2+63KLBcoo5Ra9axmb/R6lVefIxlj7PeD7GnlXAqliDTxs2T9l1ewihCY2Z2bKLLcs4K' \
    'SYUcLkrHYV4I7bxtwjIEIhJAAaIyBCMSQAD4MgQkEkAAAQAzABAkEjMBECQSEDMCECISED' \
    'MDECISEDMEECISEDMFECUSEDMFASEEDhAzBSAyAxIQMwUVMgMSEDMAGCEFEjcAGgAoEhA3' \
    'ABwBMwAAEhA3ADAAIQYSEDcAGgEiFhIQEDMBGCEFEjcBGgAoEhA3ARwBMwEAEhA3ATAAIQ' \
    'cSEDcBGgEiFhIQEDMAADMCBxIQMwEAMwIHEhAzAgAzBRQSEDMDADMCBxIQMwMHKRIQMwQA' \
    'MwIHEhAzBAcqEhAzAwgzBAgSEDMDCDMCCCEICyEJCg8QMwURIQoSEDMFEiISEDMFEzMCBx' \
    'IQMwUUMwIAEhBCANczABAkEjMBECQSEDMCECUSEDMCASEEDhAzAiAyAxIQMwIVMgMSEDMA' \
    'GCEFEjcAGgAoEhA3ABwBMwAAEhA3ADAAIQYSEDcAGgEiFhIQEDMBGCEFEjcBGgAoEhA3AR' \
    'wBMwEAEhA3ATAAIQcSEDcBGgEiFhIQEDMAADMCFBIQMwEAMwIUEhAzAgIhCw0QMwIRIQoS' \
    'EDMCEiISEDMCADMCExIQQgA0MRAlEjEBIQQOEDETMgMSEDEVMgMSEDEgMgMSEDERIQoSED' \
    'ESIQwSEDEAMRQSEDEEIQ0MEA=='

ALGOREALM_CARD_CONTRACT_LSIG = transaction.LogicSig(
    base64.decodebytes(ALGOREALM_CARD_CONTRACT_BYTECODE.encode())
)

ALGOREALM_CARD_CONTRACT = Account(
    address=ALGOREALM_CARD_CONTRACT_LSIG.address(),
    private_key=None,
    lsig=ALGOREALM_CARD_CONTRACT_LSIG,
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


def sign_send_wait(
        algod_client: algod.AlgodClient,
        account: Account,
        txn):
    """Sign a transaction, submit it, and wait for its confirmation."""
    signed_txn = sign(account, txn)
    tx_id = signed_txn.transaction.get_txid()
    transaction.write_to_file([signed_txn], "/tmp/txn.signed", overwrite=True)
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

    transaction.write_to_file(signed_group, "/tmp/txn.signed", overwrite=True)
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
            # min_round=ALGOREALM_FIRST_BLOCK,
        )
        calls += result['transactions']
        numtx = len(result['transactions'])
        if numtx > 0:
            # pointer to the next chunk of requests
            nexttoken = result['next-token']
    return calls


def search_algorelm_nft_txns(
        indexer_client: indexer.IndexerClient,
        nft_id: int
):
    nexttoken = ""
    numtx = 1
    txns = []
    while numtx > 0:
        result = indexer_client.search_asset_transactions(
            asset_id=nft_id,
            limit=1000,
            next_page=nexttoken,
            txn_type='axfer',
            min_round=ALGOREALM_FIRST_BLOCK,
        )
        txns += result['transactions']
        numtx = len(result['transactions'])
        if numtx > 0:
            # pointer to the next chunk of requests
            nexttoken = result['next-token']
    return txns


def history(indexer_client: indexer.IndexerClient):
    attempts = 1
    algorealm_calls = None
    while attempts <= MAX_CONNECTION_ATTEMPTS:
        try:
            algorealm_calls = search_algorelm_calls(indexer_client)
            break
        except IndexerHTTPError:
            print(f'Indexer Client connection attempt '
                  f'{attempts}/{MAX_CONNECTION_ATTEMPTS}')
            print('Trying to contact Indexer Client again...')
            time.sleep(CONNECTION_ATTEMPT_DELAY_SEC)
        finally:
            attempts += 1
    if not algorealm_calls:
        quit("❌ Unable to connect to Indexer Client. Check your API token!")

    claims_history = []
    name = ''
    claim = ''
    for call in algorealm_calls:
        call_args = call['application-transaction']['application-args']
        # Check is an NFT claim call
        if len(call_args) == 2:
            block = call['confirmed-round']
            nft = call_args[0].encode()
            donation = call['global-state-delta'][0]['value']['uint']
            # Check is a different claimer (2 elements in the state delta)
            if len(call['global-state-delta']) == 2:
                name = base64.b64decode(
                    call['global-state-delta'][1]['value']['bytes']).decode()
            if nft == base64.b64encode(b"Crown"):
                claim = f"👑 {name} claimed the Crown of Entropy\n" \
                        f"on Block: {block} donating: {donation} microALGOs " \
                        f"to the Rewards Pool.\n\n"
            elif nft == base64.b64encode(b"Sceptre"):
                claim = f"🪄 {name} claimed the Sceptre of Proof\n" \
                        f"on Block: {block} donating: {donation} microALGOs " \
                        f"to the Rewards Pool.\n\n"
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
            print(f'Indexer Client connection attempt '
                  f'{attempts}/{MAX_CONNECTION_ATTEMPTS}')
            print('Trying to contact Indexer Client again...')
            time.sleep(CONNECTION_ATTEMPT_DELAY_SEC)
        finally:
            attempts += 1
    if not nft_txns:
        quit("Unable to connect to Indexer Client. Check your API token!")

    nft_txns.reverse()
    for txn in nft_txns:
        if txn['asset-transfer-transaction']['amount'] == 1:
            return txn['asset-transfer-transaction']['receiver']


def opt_in(
        algod_client: algod.AlgodClient,
        user: Account,
        nft_id: int,
):
    optin = ''
    while not optin:
        optin = str(input(
            f"Do you want to opt-in the asset {nft_id}? (Y/n) "
        ))
        if optin.lower() == 'y':
            params = algod_client.suggested_params()

            opt_in_txn = transaction.AssetOptInTxn(
                sender=user.address,
                sp=params,
                index=nft_id,
            )
            return sign_send_wait(algod_client, user, opt_in_txn)

        elif optin.lower() == 'n':
            return
        else:
            optin = ''


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
        app_args=[claim_arg.encode(), new_majesty.encode()]
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

    try:
        gtxn_id = algod_client.send_transactions(signed_group)
        wait_for_confirmation(algod_client, gtxn_id)
    except AlgodHTTPError:
        quit("\n☹️  Were you too stingy? Only generous hearts will rule over "
             "Algorand Realm!\n️")


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
        sender=ALGOREALM_CARD_CONTRACT.address,
        sp=params,
        receiver=claimer.address,
        amt=1,
        index=ALGOREALM_CARD_ID,
        revocation_target=ALGOREALM_CARD_CONTRACT.address,
    )

    signed_group = group_and_sign(
        [claimer, claimer, ALGOREALM_CARD_CONTRACT],
        [proof_crown_ownership, proof_sceptre_ownership, nft_card_xfer],
    )

    try:
        gtxn_id = algod_client.send_transactions(signed_group)
        wait_for_confirmation(algod_client, gtxn_id)
    except AlgodHTTPError:
        quit("\nOnly the generous heart of the Great Majesty of Algorand "
             "can break the spell!\n"
             "Conquer both the 👑 Crown of Entropy and the 🪄 Sceptre "
             "of Proof first!\n")


def main():
    if len(sys.argv) == 1:
        # Display help if no arguments, see:
        # https://github.com/docopt/docopt/issues/420#issuecomment-405018014
        sys.argv.append('--help')

    args = docopt(__doc__)

    print(
        r"""
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
    )

    if args['poem']:
        return print(
            r"""
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
        )

    # Check user's inputs
    assert isinstance(args['<purestake-api-token>'], str)

    token = args['<purestake-api-token>']
    header = {'X-Api-key': token}

    algod_client = algod.AlgodClient(
        algod_token=token,
        algod_address=ALGOD_ADDRESS,
        headers=header
    )

    indexer_client = indexer.IndexerClient(
        indexer_token=token,
        indexer_address=INDEXER_ADDRESS,
        headers=header
    )

    if args['dynasty']:
        print(
            r"""
                                   *** DYNASTY ***
            """
        )
        return print(*['\n', *history(indexer_client)])

    try:
        assert len(args['<mnemonic>'].split()) == 25
    except AssertionError:
        quit('The mnemonic phrase must contain 25 words, '
             'formatted as: "word_1 word_2 ... word_25"\n')
    private_key = mnemonic.to_private_key(args['<mnemonic>'])

    user = Account(
        account.address_from_private_key(private_key),
        private_key
    )

    if args['claim-crown']:
        opt_in(algod_client, user, CROWN_ID)

        name = args['<majesty-name>']

        print("\n👑 Claiming the Corwn of Entropy...")
        claim_nft(
            algod_client=algod_client,
            indexer_client=indexer_client,
            claimer=user,
            claim_arg='Crown',
            new_majesty=name,
            donation_amount=int(args['<microalgos>']),
            nft_id=CROWN_ID,
        )
        print(f"\n🏰 Glory to {name}, the Randomic Majesty of Algorand! 🎉\n")

    elif args['claim-sceptre']:
        opt_in(algod_client, user, SCEPTRE_ID)

        name = args['<majesty-name>']

        print("\n🪄 Claiming the Sceptre of Proof...")
        claim_nft(
            algod_client=algod_client,
            indexer_client=indexer_client,
            claimer=user,
            claim_arg='Sceptre',
            new_majesty=name,
            donation_amount=int(args['<microalgos>']),
            nft_id=SCEPTRE_ID,
        )
        print(f"\n🏰 Glory to {name}, the Verifiable Majesty of Algorand! 🎉\n")

    elif args['claim-card']:
        if algod_client.status()["last-round"] <= ALGOREALM_CARD_FIRST_BLOCK:
            return print("🔐 The spell can be broken starting from the block "
                         f"{ALGOREALM_CARD_FIRST_BLOCK}... ⏳\n")

        algorelm_card_contract = algod_client.account_info(
            ALGOREALM_CARD_CONTRACT.address
        )

        assets = algorelm_card_contract['assets']

        card_nft = list(filter(
            lambda asset: asset['asset-id'] == ALGOREALM_CARD_ID, assets))[0]

        if card_nft['amount'] == 0:
            return print("🔓 The enchanted coffer is empty! "
                         "The AlgoRealm Special Card has been claimed!\n")

        opt_in(algod_client, user, ALGOREALM_CARD_ID)

        print("\n✨ Whispering words of wisdom...")
        claim_card(
            algod_client=algod_client,
            claimer=user
        )
        print(f"\n 📜 The spell has been broken! "
              f"The AlgoRealm Special Card is yours! 🎉\n")

    else:
        quit("\nError: read AlgoRealm '--help'!\n")


if __name__ == "__main__":
    main()
