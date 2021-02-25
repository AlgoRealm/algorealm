```
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

## Majesties of Algorand

Only generous hearts will rule over Algorand realm.

Who are the Majesties of the Algorand realm?

```bash
$ ./goal app read --app-id 137491307 --global
```

Show how generous is your heart donating some ALGO to the [Rewards Pool](https://developer.algorand.org/docs/reference/algorand-networks/mainnet/#rewardspool-address) and claim the title of **Randomic Majesty of Algorand** or **Verifiable Majesty of Algorand**.

The more generous you are, the harder will be to be dethroned.

## Claim the Crown of Entropy

[Crown of Entropy](https://algoexplorer.io/asset/137493252) for the Randomic Majesty of Algorand

```bash
$ ./goal asset send -f YOUR_ADDRESS -t YOUR_ADDRESS --assetid 137493252 -a 0

$ ./goal app call --app-id 137491307 -f YOUR_ADDRESS --app-arg "str:Crown" --app-arg "str:YOUR_NAME" -o crown_claim.txn

$ ./goal clerk send -f YOUR_ADDRESS -t 737777777777777777777777777777777777777777777777777UFEJ2CI -a YOUR_DONATION -o crown_donation.txn

$ ./goal asset send -f CROWN_OWNER_ADDRESS -t YOUR_ADDRESS --assetid 137493252 -a 1 --clawback L64GYN3IM763NDQJQD2IX35SCWQZRHWEMX55JTOUJ2PMHL6ZCMHLR4OJMU -o crown_transfer.txn

$ cat crown_claim.txn crown_donation.txn crown_transfer.txn > claim.txn

$ ./goal clerk group -i claim.txn -o claim.gtxn

$ ./goal clerk split -i claim.gtxn -o unsigned_claim.txn

$ ./goal clerk sign -i unsigned_claim-0.txn -o claim-0.stxn

$ ./goal clerk sign -i unsigned_claim-1.txn -o claim-1.stxn

$ ./goal clerk sign -i unsigned_claim-2.txn -p algorealm_law.teal -o claim-2.stxn

$ cat claim-0.stxn claim-1.stxn claim-2.stxn > claim.sgtxn

$ ./goal clerk rawsend -f claim.sgtxn
```

## Claim the Sceptre of Proof

[Sceptre of Proof](https://algoexplorer.io/asset/137494385) for the Verifiable Majesty of Algorand

```bash
$ ./goal asset send -f YOUR_ADDRESS -t YOUR_ADDRESS --assetid 137494385 -a 0

$ ./goal app call --app-id 137491307 -f YOUR_ADDRESS --app-arg "str:Sceptre" --app-arg "str:YOUR_NAME" -o sceptre_claim.txn

$ ./goal clerk send -f YOUR_ADDRESS -t 737777777777777777777777777777777777777777777777777UFEJ2CI -a YOUR_DONATION -o sceptre_donation.txn

$ ./goal asset send -f SCEPTRE_OWNER_ADDRESS -t YOUR_ADDRESS --assetid 137494385 -a 1 --clawback L64GYN3IM763NDQJQD2IX35SCWQZRHWEMX55JTOUJ2PMHL6ZCMHLR4OJMU -o sceptre_transfer.txn

$ cat sceptre_claim.txn sceptre_donation.txn sceptre_transfer.txn > claim.txn

$ ./goal clerk group -i claim.txn -o claim.gtxn

$ ./goal clerk split -i claim.gtxn -o unsigned_claim.txn

$ ./goal clerk sign -i unsigned_claim-0.txn -o claim-0.stxn

$ ./goal clerk sign -i unsigned_claim-1.txn -o claim-1.stxn

$ ./goal clerk sign -i unsigned_claim-2.txn -p algorealm_law.teal -o claim-2.stxn

$ cat claim-0.stxn claim-1.stxn claim-2.stxn > claim.sgtxn

$ ./goal clerk rawsend -f claim.sgtxn
```

## Tip the Dev

If you enjoyed AlgoRealm or find it useful as free and open source learning example, consider tipping the Dev:

`XODGWLOMKUPTGL3ZV53H3GZZWMCTJVQ5B2BZICFD3STSLA2LPSH6V6RW3I`

