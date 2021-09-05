"""
AlgoRealm Dynasty

Usage:
  algorealm_dynasty.py <purestake-api-token>
  algorealm_dynasty.py local-host <api-token> [--indexer-address=<ia>]
  algorealm_dynasty.py [--help]

Commands:
  local-host   Use your local Indexer.

Options:
  -i <ia> --indexer-address=<ia>    [default: http://localhost:8980/]
  -h --help
"""


import sys
from docopt import docopt
import time
import base64
from algosdk.v2client import indexer
from algosdk.error import IndexerHTTPError


MAX_CONNECTION_ATTEMPTS = 10
CONNECTION_ATTEMPT_DELAY_SEC = 2


def search_algorelm_calls(indexer_client):
    nexttoken = ""
    numtx = 1
    calls = []
    while numtx > 0:
        result = indexer_client.search_transactions(
            limit=1000,
            next_page=nexttoken,
            application_id=137491307,
            min_round=13578170,
        )
        calls += result['transactions']
        numtx = len(result['transactions'])
        if numtx > 0:
            # pointer to the next chunk of requests
            nexttoken = result['next-token']
    return calls


def history(indexer_client):
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
        quit("Unable to connect to Indexer Client.")

    claims_history = []
    for call in algorealm_calls:
        title = base64.b64decode(
            call['global-state-delta'][1]['key']).decode()
        name = base64.b64decode(
            call['global-state-delta'][1]['value']['bytes']).decode()
        donation = call['global-state-delta'][0]['value']['uint']
        block = call['confirmed-round']

        claims_history += [
            {
                'title': title,
                'name': name,
                'donation': donation,
                'block': block,
            }
        ]
    return claims_history


def main():
    if len(sys.argv) == 1:
        # Display help if no arguments, see:
        # https://github.com/docopt/docopt/issues/420#issuecomment-405018014
        sys.argv.append('--help')

    args = docopt(__doc__)

    if args['local-host']:
        token = args['<api-token>']
        header = None
        indexer_address = args['--indexer-address']
    else:
        token = args['<purestake-api-token>']
        header = {'X-Api-key': token}
        indexer_address = "https://mainnet-algorand.api.purestake.io/idx2"

    indexer_client = indexer.IndexerClient(
        indexer_token=token,
        indexer_address=indexer_address,
        headers=header
    )

    dynasty = history(indexer_client)

    print(r"""
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
                                  *** DYNASTY ***                              
    """)

    for majesty in dynasty:
        if majesty['title'] == 'RandomicMajestyOfAlgorand':
            print(f"👑 {majesty['name']} claimed the Crown of Entropy")
            print(f"on Block: {majesty['block']} "
                  f"donating: {majesty['donation']} microALGOs "
                  f"to the Rewards Pool.\n")
        elif majesty['title'] == 'VerifiableMajestyOfAlgorand':
            print(f"🪄 {majesty['name']} claimed the Sceptre of Proof")
            print(f"on Block: {majesty['block']} "
                  f"donating: {majesty['donation']} microALGOs "
                  f"to the Rewards Pool.\n")
        else:
            quit("Error: Invalid AlgoRealm Majesty Title.")


if __name__ == "__main__":
    main()
