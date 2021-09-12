```
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
```

## Incipit

```
There was a time
When nothing but Entropy was there.
Then came the cryptographic Proof,
And took it care.

Verifiability of randomness,
Since genesis block,
Brings Consensus over realm vastness,
So Algorand never fork.
```

## Become a Majesty of Algorand

Only generous hearts will rule over Algorand realm.

Show how generous is your heart donating some ALGOs to the [Rewards Pool](https://developer.algorand.org/docs/reference/algorand-networks/mainnet/#rewardspool-address) and claim the title of **Randomic Majesty of Algorand** or **Verifiable Majesty of Algorand**.

The more generous you are, the harder will be to be dethroned.

Join [AlgoRealm channel](https://t.me/algorealm)!

## Play with AlgoRealm CLI

### 1. Setup

1. Download the `algorealm.py` script
2. Install the following dependencies:

```shell
$ pip3 install docopt --upgrade
$ pip3 install py-algorand-sdk --upgrade
```

3. Create an account on PureStake and [get your API token](https://developer.purestake.io/login)

### 2. How to play

Playing **AlgoRealm** from your CLI is pretty easy, just ask for help:

```shell
$ python3 algorealm.py -h
```

```shell
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
```

**NOTE:** keep your `<mnemonic>` safe! Although you will only use it on you local machine, is it strongly recommended to make use of a dedicated account just to play AlgoRealm!

### 3. AlgoRealm Dynasty

Who are the Majesties of the Algorand realm?

1. Discover it directly on [Algorand blockchain](https://algoexplorer.io/application/137491307)

2. Discover it with your node:
```shell
$ ./goal app read --app-id 137491307 --global
```

3. Discover it with the AlgoRealm CLI:
```shell
$ python3 algorealm.py dynasty <purestake-api-token>
```

```
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
                                                                                   
    
👑 jkbishbish claimed the Crown of Entropy
on Block: 13578171 donating: 2 microALGOs to the Rewards Pool.

🪄 jkbishbish claimed the Sceptre of Proof
on Block: 13578330 donating: 2 microALGOs to the Rewards Pool.

👑 tmc claimed the Crown of Entropy
on Block: 14936018 donating: 3 microALGOs to the Rewards Pool.

🪄 tmc claimed the Sceptre of Proof
on Block: 14936235 donating: 3 microALGOs to the Rewards Pool.

👑 nullun claimed the Crown of Entropy
on Block: 14989913 donating: 4 microALGOs to the Rewards Pool.

🪄 nullun claimed the Sceptre of Proof
on Block: 14989913 donating: 4 microALGOs to the Rewards Pool.
```

### 4. Claim the Crown of Entropy or the Sceptre of Proof

Chose your `<majesty-name>` and become part of the Dynasty! Remember that to dethrone the current Majesties you must donate to the Algorand's Rewards Pool more `<microalgos>` than the last donation.

```shell
$ python3 algorealm.py claim-crown <purestake-api-token> <mnemonic> <majesty-name> <microalgos>
```

```shell
$ python3 algorealm.py claim-sceptre <purestake-api-token> <mnemonic> <majesty-name> <microalgos>
```

**NOTE:** enter the the `<mnemonic>` formatting it as: `"word_1 word_2 word_3 ... word_25"`

### 5. Claim the AlgoRealm Special Card

The [AlgoRealm Card](https://algoexplorer.io/asset/321172366) is a unique [AlgoWorld NFT](https://algoworld.io/) Special Card, securely stored in an enchanted coffer.


 <img src="https://user-images.githubusercontent.com/65770425/132135850-c4193efe-5d21-4cd6-a9bb-ae72b3d5b357.png" alt="algorealm_card" width="250" />


Only the generous heart of the [Great Majesty of Algorand](https://github.com/cusma/algorealm) will ever able to break the spell, claim the **unique Special Card** and trade it! So, you previously need to conquer both the [Crown of Entropy](https://github.com/cusma/algorealm#claim-the-crown-of-entropy) and the [Sceptre of Proof](https://github.com/cusma/algorealm#claim-the-sceptre-of-proof), ascending to [AlgoRealm's throne](https://algoexplorer.io/application/137491307).

The AlgoRealm Card can be claimed **starting from block 16,250,000**: hold strong both the Crown and the Sceptre and keep the throne until there!

```shell
$ python3 algorealm.py claim-card <purestake-api-token> <mnemonic>
```

## Play with goal CLI

AlgoRealm could also be a good challenge to [run your own Algorand node](https://developer.algorand.org/docs/run-a-node/setup/install/) and familiarise the [goal CLI commands](https://developer.algorand.org/docs/reference/cli/goal/goal/).

### 1. Claim the Crown of Entropy

1. Save the [AlgoRealm Law](https://github.com/cusma/algorealm/blob/main/algorealm_law.teal) into your node directory.
2. Find out who owns the [Crown of Entropy](https://algoexplorer.io/asset/137493252) (keep the `CROWN_OWNER_ADDRESS`) and Opt-In.

```bash
$ ./goal asset send -f YOUR_ADDRESS -t YOUR_ADDRESS --assetid 137493252 -a 0
```

3. Write the unsigned `crown_claim.txn` Applicarion Call transaction passing `"str:YOUR_NAME"` as `--app-arg`.

```bash
$ ./goal app call --app-id 137491307 -f YOUR_ADDRESS --app-arg "str:Crown" --app-arg "str:YOUR_NAME" -o crown_claim.txn
```

4. Write the unsigned `crown_donation.txn` Payment transaction to the Rewards Pool specifying `YOUR_DONATION` in microALGOs. The claim will be successful if `YOUR_DONATION` is grater than the current one.

```bash
$ ./goal clerk send -f YOUR_ADDRESS -t 737777777777777777777777777777777777777777777777777UFEJ2CI -a YOUR_DONATION -o crown_donation.txn
```

5. Write the unsigned `crown_transfer.txn` Asset Transfer transaction form `CROWN_OWNER_ADDRESS` to `YOUR_ADDRESS`.

```bash
$ ./goal asset send -f CROWN_OWNER_ADDRESS -t YOUR_ADDRESS --assetid 137493252 -a 1 --clawback L64GYN3IM763NDQJQD2IX35SCWQZRHWEMX55JTOUJ2PMHL6ZCMHLR4OJMU -o crown_transfer.txn
```

6. Build the unsigned Group Transaction.

```bash
$ cat crown_claim.txn crown_donation.txn crown_transfer.txn > claim.txn

$ ./goal clerk group -i claim.txn -o claim.gtxn
```

7. Split the Group Transaction and sign the single transactions (no longer valid if submitted as standalone).

```bash
$ ./goal clerk split -i claim.gtxn -o unsigned_claim.txn

$ ./goal clerk sign -i unsigned_claim-0.txn -o claim-0.stxn

$ ./goal clerk sign -i unsigned_claim-1.txn -o claim-1.stxn

$ ./goal clerk sign -i unsigned_claim-2.txn -p algorealm_law.teal -o claim-2.stxn
```

8. Submit the signed Group Transaction: claim the Crown of Entropy and became the Randomic Majesty of Algorand!

```bash
$ cat claim-0.stxn claim-1.stxn claim-2.stxn > claim.sgtxn

$ ./goal clerk rawsend -f claim.sgtxn
```

### 2. Claim the Sceptre of Proof

1. Save the [AlgoRealm Law](https://github.com/cusma/algorealm/blob/main/algorealm_law.teal) into your node directory.
2. Find out who owns the [Sceptre of Proof](https://algoexplorer.io/asset/137494385) (keep the `SCEPTRE_OWNER_ADDRESS`) and Opt-In.

```bash
$ ./goal asset send -f YOUR_ADDRESS -t YOUR_ADDRESS --assetid 137494385 -a 0
```

3. Write the unsigned `sceptre_claim.txn` Applicarion Call transaction passing `"str:YOUR_NAME"` as `--app-arg`.

```bash
$ ./goal app call --app-id 137491307 -f YOUR_ADDRESS --app-arg "str:Sceptre" --app-arg "str:YOUR_NAME" -o sceptre_claim.txn
```

4. Write the unsigned `sceptre_donation.txn` Payment transaction to the Rewards Pool specifying `YOUR_DONATION` in microALGOs. The claim will be successful if `YOUR_DONATION` is grater than the current one.

```bash
$ ./goal clerk send -f YOUR_ADDRESS -t 737777777777777777777777777777777777777777777777777UFEJ2CI -a YOUR_DONATION -o sceptre_donation.txn
```

5. Write the unsigned `sceptre_transfer.txn` Asset Transfer transaction form `SCEPTRE_OWNER_ADDRESS` to `YOUR_ADDRESS`.

```bash
$ ./goal asset send -f SCEPTRE_OWNER_ADDRESS -t YOUR_ADDRESS --assetid 137494385 -a 1 --clawback L64GYN3IM763NDQJQD2IX35SCWQZRHWEMX55JTOUJ2PMHL6ZCMHLR4OJMU -o sceptre_transfer.txn
```

6. Build the unsigned Group Transaction.

```bash
$ cat sceptre_claim.txn sceptre_donation.txn sceptre_transfer.txn > claim.txn

$ ./goal clerk group -i claim.txn -o claim.gtxn
```

7. Split the Group Transaction and sign the single transactions (no longer valid if submitted as standalone).

```bash
$ ./goal clerk split -i claim.gtxn -o unsigned_claim.txn

$ ./goal clerk sign -i unsigned_claim-0.txn -o claim-0.stxn

$ ./goal clerk sign -i unsigned_claim-1.txn -o claim-1.stxn

$ ./goal clerk sign -i unsigned_claim-2.txn -p algorealm_law.teal -o claim-2.stxn
```

8. Submit the signed Group Transaction: claim the Sceptre of Proof and became the Verifiable Majesty of Algorand!

```bash
$ cat claim-0.stxn claim-1.stxn claim-2.stxn > claim.sgtxn

$ ./goal clerk rawsend -f claim.sgtxn
```

### 3. Claim the AlgoRealm Special Card

You can also claim and trade the **AlgoRealm Special Card** using the goal CLI [following these instructions](https://github.com/cusma/algorealm/tree/main/card#readme).

## Tip the Dev

If you enjoyed AlgoRealm or find it useful as free and open source learning example, consider tipping the Dev:

`XODGWLOMKUPTGL3ZV53H3GZZWMCTJVQ5B2BZICFD3STSLA2LPSH6V6RW3I`

Here you find the [AlgoRealm slide deck](https://docs.google.com/presentation/d/1pkE_VWuq_zPOtkc8tK8MYKPzdBwUQA8r5UgACpBpmvk/edit?usp=sharing) presented at Algorand's Office Hours!

Join [AlgoRealm channel](https://t.me/algorealm)!
