import base64
import time

from algosdk.error import IndexerHTTPError
from algosdk.v2client.indexer import IndexerClient

from constants import CONNECTION_ATTEMPT_DELAY_SEC, MAX_CONNECTION_ATTEMPTS


def algorelm_calls(
    client: IndexerClient,
    algorealm_app_id: int,
    algorealm_first_round: int,
) -> list:
    """
    Search for all the Application Calls to AlgoRealm.

    Args:
        client: Algorand Indexer Client
        algorealm_app_id: AlgoRealm Application ID
        algorealm_first_round: AlgoRealm first round on blockchain

    Returns:
        List of all the Application Calls to AlgoRealm.
    """
    nexttoken = ""
    numtx = 1
    calls = []
    while numtx > 0:
        result = client.search_transactions(
            limit=1000,
            next_page=nexttoken,
            application_id=algorealm_app_id,
            min_round=algorealm_first_round,
        )
        calls += result["transactions"]
        numtx = len(result["transactions"])
        if numtx > 0:
            nexttoken = result["next-token"]
    return calls


def algorelm_nft_txns(
    client: IndexerClient,
    nft_id: int,
    algorealm_first_round: int,
) -> list:
    """
    Search for all the Asset Transfer transactions involving AlgoRealm NFTs.
    Args:
        client: Algorand Indexer Client
        nft_id: AlgoRealm NFT ID (Crown or Sceptre)
        algorealm_first_round: AlgoRealm first round on blockchain

    Returns:
        List of all the Asset Transfer transactions involving AlgoRealm NFTs.
    """
    nexttoken = ""
    numtx = 1
    nft_txns = []
    while numtx > 0:
        result = client.search_asset_transactions(
            asset_id=nft_id,
            limit=1000,
            next_page=nexttoken,
            txn_type="axfer",
            min_round=algorealm_first_round,
        )
        nft_txns += result["transactions"]
        numtx = len(result["transactions"])
        if numtx > 0:
            nexttoken = result["next-token"]
    return nft_txns


def history(
    client: IndexerClient,
    algorealm_app_id: int,
    algorealm_first_round: int,
) -> list:
    """
    Retrieve the AlgoRealm Majesties claims history from chain.

    Args:
        client: Algorand Indexer Client
        algorealm_app_id: AlgoRealm Application ID
        algorealm_first_round: AlgoRealm first round on blockchain

    Returns:
        Historical list of claims.
    """
    attempts = 1
    calls = None
    while attempts <= MAX_CONNECTION_ATTEMPTS:
        try:
            calls = algorelm_calls(
                client=client,
                algorealm_app_id=algorealm_app_id,
                algorealm_first_round=algorealm_first_round,
            )
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
    if not calls:
        quit("❌ Unable to connect to Indexer Client!")

    claims_history = []
    name = ""
    claim = ""
    for call in calls:
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


def current_owner(
    client: IndexerClient,
    nft_id: int,
    algorealm_first_round: int,
) -> str:
    """
    Retrieve the current owner of an NFT.

    Args:
        client: Algorand Indexer Client
        nft_id: AlgoRealm NFT (Crown, Sceptre, Card)
        algorealm_first_round: AlgoRealm first round on blockchain

    Returns:
        Address of current NFT owner.
    """
    attempts = 1
    nft_txns = None
    while attempts <= MAX_CONNECTION_ATTEMPTS:
        try:
            nft_txns = algorelm_nft_txns(
                client=client,
                nft_id=nft_id,
                algorealm_first_round=algorealm_first_round,
            )
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
        quit("❌ Unable to connect to Indexer Client!")

    nft_txns.reverse()
    for txn in nft_txns:
        if txn["asset-transfer-transaction"]["amount"] == 1:
            return txn["asset-transfer-transaction"]["receiver"]
