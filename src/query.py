import base64
import math
import time
from operator import itemgetter

from algosdk.error import IndexerHTTPError
from algosdk.v2client.indexer import IndexerClient

from const import CONNECTION_ATTEMPT_DELAY_SEC, MAX_CONNECTION_ATTEMPTS


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


def claims_history(
    client: IndexerClient,
    algorealm_app_id: int,
    algorealm_first_round: int,
) -> list[dict]:
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

    claims = []
    for call in calls:
        call_args = call["application-transaction"]["application-args"]
        # Check is an NFT claim call
        if len(call_args) == 2:
            claim = {
                "block": call["confirmed-round"],
                "nft": base64.b64decode(call_args[0]).decode(),
                "name": base64.b64decode(call_args[1]).decode(),
                "donation": call["global-state-delta"][0]["value"]["uint"],
            }
            if claim["nft"] == "Crown":
                claim["symbol"] = "👑"
                claim["nft_name"] = "Crown of Entropy"
                claim["title"] = "Randomic Majesty"
            else:
                claim["symbol"] = "🪄"
                claim["nft_name"] = "Sceptre of Proof"
                claim["title"] = "Verifiable Majesty"
            claims += [claim]
    return claims


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


def dynasty(claims: list[dict]) -> list:
    majesty_claims = []
    for claim in claims:
        majesty = (
            f"{claim['symbol']} {claim['name']} became the {claim['title']} "
            f"on Block: {claim['block']}\n"
            f"claiming the {claim['nft_name']} with a donation of:\n"
            f"{claim['donation']} microALGOs to the Rewards Pool.\n\n"
        )
        majesty_claims += [majesty]
    return majesty_claims


def longevity(
    claims: list[dict], latest_block: int, majesty_selector: str
) -> list[dict]:
    assert majesty_selector == "Crown" or majesty_selector == "Sceptre"

    majesty_claims = []
    for claim in claims:
        if claim["nft"] == majesty_selector:
            majesty_claims += [claim]

    claim_block = [claim["block"] for claim in majesty_claims]
    majesty_longevity = [
        new - old for new, old in zip(claim_block[1:], claim_block[:-1])
    ]
    majesty_longevity.append(latest_block - claim_block[-1])

    for claim, blocks in zip(majesty_claims, majesty_longevity):
        claim["longevity"] = blocks
    return sorted(majesty_claims, key=itemgetter("longevity"), reverse=True)


def braveness(claims: list[dict], majesty_selector: str) -> list[dict]:
    assert majesty_selector == "Crown" or majesty_selector == "Sceptre"

    majesty_claims = []
    for claim in claims:
        if claim["nft"] == majesty_selector:
            majesty_claims += [claim]
    claim_donation = [claim["donation"] for claim in majesty_claims]

    majesty_braveness = [1]
    for new, old in zip(claim_donation[1:], claim_donation[:-1]):
        majesty_braveness.append(math.log(new) - math.log(old))

    for claim, points in zip(majesty_claims, majesty_braveness):
        claim["braveness"] = round(points, 3)
    return sorted(majesty_claims, key=itemgetter("braveness"), reverse=True)
