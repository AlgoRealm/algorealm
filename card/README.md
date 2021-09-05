# AlgoRealm Card on AlgoWorld NFT

The [AlgoRealm Card](https://algoexplorer.io/asset/321172366) is a unique [AlgoWorld NFT](https://algoworld.io/) Special Card, securely stored in an enchanted coffer. 

Only the generous heart of the [Great Majesty of Algorand](https://github.com/cusma/algorealm) will ever able to break the spell, claim the **unique Special Card** and trade it!



## How to claim the AlgoRealm Card?

### Role: Card Claimer
As **Card Claimer**, you previously need to conquer both the [Crown of Entropy](https://github.com/cusma/algorealm#claim-the-crown-of-entropy) and the [Sceptre of Proof](https://github.com/cusma/algorealm#claim-the-sceptre-of-proof), ascending to [AlgoRealm's throne](https://algoexplorer.io/application/137491307).

The AlgoRealm Card can be claimed **starting from block 16,250,000**: hold strong both the Crown and the Sceptre and keep the throne until there!

#### Card Claim's Unsigned Transactions
Save the `algorealm_card_contract.teal` into your node directory.

1. Wear the Crown of Entropy
```shell
./goal app call
--app-id 321230622
--from YOUR_ADDRESS
--app-account YOUR_ADDRESS
--app-arg "str:AsaAmountEq"
--app-arg "int:1"
--foreign-asset 137493252
--out proof_crown.txn
```

2. Brandish the Sceptre of Proof
```shell
./goal app call
--app-id 321230622
--from YOUR_ADDRESS
--app-account YOUR_ADDRESS
--app-arg "str:AsaAmountEq"
--app-arg "int:1"
--foreign-asset 137494385
--out proof_sceptre.txn
```

3. Claim the AlgoRealm Special Card
```shell
./goal asset send
--from ZTQNLH7QZ3J5ZDRS5VFBICPLOEFOGPNK5D6GV4VXAFPOCZJMMCBIRDSBWU
--to YOUR_ADDRESS
--assetid 321172366
--amount 1
--clawback ZTQNLH7QZ3J5ZDRS5VFBICPLOEFOGPNK5D6GV4VXAFPOCZJMMCBIRDSBWU
--out transfer_card.txn
```

#### Create the Unsigned Claim Group Transaction
```shell
cat proof_crown.txn proof_sceptre.txn transfer_card.txn > claim.txn
```
```shell
./goal clerk group -i claim.txn -o claim.gtxn
```

#### Split the Unsigned Claim Group Transaction
```shell
./goal clerk split -i claim.gtxn -o unsigned_claim.txn
```

#### Sign the Claim Group Transaction
```shell
./goal clerk sign -i unsigned_claim-0.txn -o claim-0.stxn
```
```shell
./goal clerk sign -i unsigned_claim-1.txn -o claim-1.stxn
```
```shell
./goal clerk sign -i unsigned_claim-2.txn -p algorealm_card_contract.teal -o claim-2.stxn
```

#### Submit the Claim Group Transaction
```shell
cat claim-0.stxn claim-1.stxn claim-2.stxn > claim.sgtxn
```
```shell
./goal clerk rawsend -f claim.sgtxn
```



## How to trade the AlgoRealm Card?

The AlgoRealm Card can be traded between a **Seller** and a **Buyer**, for ALGO, at a price freely agreed between the parties. AlgoRealm and AlgoWorld NFT both collect a 5% royalty on the trades.

As **Seller**, you can sell your AlgoRealm Card if and only if [you still sit on AlgoRealm's throne](https://algoexplorer.io/application/137491307), both as Randomic Majesty of Algorand and Verifiable Majesty of Algorand.

So, if you have been dethroned, you need to conquer again both the [Crow of Entropy](https://algoexplorer.io/asset/137493252) and the [Sceptre of Proof](https://algoexplorer.io/asset/137494385) to be able to sell your AlgoRealm Card.

As **Buyer**, you can submit a buy order proposal to the **Seller**, as *Unsigned Trade Group Transaction*, without any counterparty risk. As **Seller** you will only sign the buy order proposal after your personal review of the *Unsigned Trade Group Transaction*, sent by the **Buyer** and submit it to the blockchain.



### Trading role: Buyer

As **Buyer** you must first Opt-In the AlgoRealm Card.

#### Opt-In AlgoRealm Special Card

```shell
./goal asset send
--from BUYER_ADDRESS
--to BUYER_ADDRESS
--assetid 321172366
--amount 0
```

#### Placing buy orders as Unsigned Trade Group Transaction

As **Buyer** you create a buy order proposal as *Unsigned Trade Group Transaction* of 6 transactions, to be reviewed an eventually signed by the **Seller**.

To generate a buy order proposal you need to fill in the following parameters:

1. `BUYER_ADDRESS`: your address
2. `SELLER_ADDRESS`: the address of the current owner of the AlgoRealm Card
3. `MICROALGO_ORDER_PRICE`: the value, in microALGOs, of your buy order proposal
4. `5%_MICROALGO_ORDER_PRICE:`: the value, in microALGOs, of the royalty (equal to the 5% of buy order's value, rounded up)

#### Write Unsigned Card Trade's Standalone Transactions

1. Proof of ownership: the **Seller** must own the Crown of Entropy

```shell
./goal app call
--app-id 321230622
--from SELLER_ADDRESS
--app-account SELLER_ADDRESS
--app-arg "str:AsaAmountEq"
--app-arg "int:1"
--foreign-asset 137493252
--out proof_crown.txn
```

2. Proof of ownership: the **Seller** must own the Sceptre of Proof

```shell
./goal app call
--app-id 321230622
--from SELLER_ADDRESS
--app-account SELLER_ADDRESS
--app-arg "str:AsaAmountEq"
--app-arg "int:1"
--foreign-asset 137494385
--out proof_sceptre.txn
```

3. Buy order proposal

```shell
./goal clerk send
--from BUYER_ADDRESS
--to SELLER_ADDRESS
--amount MICROALGO_ORDER_PRICE
--out buy_order_proposal.txn
```

4. Royalty Payment to Rightholder 1

```shell
./goal clerk send
--from SELLER_ADDRESS
--to H7N65NZIWBOKFDSRNPLLDGN72HVFKXT4RRSY7M66B6Y2PFLQFKLPLHU5JU
--amount 5%_MICROALGO_ORDER_PRICE
--out royalty_1.txn
```

5. Royalty Payment to Rightholder 2

```shell
./goal clerk send
--from SELLER_ADDRESS
--to 2PDM3E7WLVPMEKCCMNTHM3FCZNZM4CSJQUOC4SWHMFPAR3N4NXBLCQKHPE
--amount 5%_MICROALGO_ORDER_PRICE
--out royalty_2.txn
```

6. AlgoRealm Card Transfer

```shell
./goal asset send
--from SELLER_ADDRESS
--to BUYER_ADDRESS
--assetid 321172366
--amount 1
--clawback ZTQNLH7QZ3J5ZDRS5VFBICPLOEFOGPNK5D6GV4VXAFPOCZJMMCBIRDSBWU
--out transfer_card.txn
```

#### Create Unsigned Trade Group Transaction

```shell
cat proof_crown.txn proof_sceptre.txn buy_order_proposal.txn royalty_1.txn royalty_2.txn transfer_card.txn > trade.txn
```

```shell
./goal clerk group -i trade.txn -o trade.gtxn
```

#### Split the Unsigned Trade Group Transaction

```shell
./goal clerk split -i trade.gtxn -o unsigned_trade.txn
```

#### Sign just your Buy Order Proposal Transaction

```shell
./goal clerk sign -i unsigned_trade-2.txn -o trade-2.stxn
```

As **Buyer**, you will send both the unsigned `trade.gtxn` and the signed `trade-2.stxn` to the **Seller**.

Note that you have no counterparty risk, since `trade-2.stxn` can only be approved by the consensus protocol as part of the whole *Trade Group Transaction* you just created.



### Trading role: Seller

As **Seller**, you review the buy order proposal placed by the **Buyer** as *Unsigned Trade Group Transaction*. If you agree on the buy order proposal, you sign the AlgoRealm Card *Unsigned Trade Group Transaction* and submit it to the blockchain. 

Remember that, in doing so, there is no counterparty risk for both parties.

Before being able to sign the rest of the trade you must **save** the `algorealm_card_contract.teal` into your node directory.

#### Inspect the Unsigned Trade Group Transaction

As **Seller**, you need to inspect the `trade.gtxn`, verifying the transactions' details proposed by the **Buyer**. Note that you must be able to autonomously verify the *Unsigned Trade Group Transaction* correctness.

```shell
./goal clerk inspect trade.gtxn
```

As **Seller**, if you approve the *Unsigned Trade Group Transaction*, you can complete the signing process of the *Trade Group Transaction* and submit it to the blockchain.

#### Split the Unsigned Trade Group Transaction

```shell
./goal clerk split -i trade.gtxn -o unsigned_trade.txn
```

#### Sign rest of Trade Transactions
```shell
./goal clerk sign -i unsigned_trade-0.txn -o trade-0.stxn
```
```shell
./goal clerk sign -i unsigned_trade-1.txn -o trade-1.stxn
```
 As **Seller**, you do not sign the `unsigned_trade-2.txn` (already signed and sent by the **Buyer** as `trade-2.stxn`).

```shell
./goal clerk sign -i unsigned_trade-3.txn -o trade-3.stxn
```
```shell
./goal clerk sign -i unsigned_trade-4.txn -o trade-4.stxn
```
```shell
./goal clerk sign -i unsigned_trade-5.txn -p algorealm_card_contract.teal -o trade-5.stxn
```

#### Submit the Trade Group Transaction
```shell
cat trade-0.stxn trade-1.stxn trade-2.stxn trade-3.stxn trade-4.stxn trade-5.stxn > trade.sgtxn
```
```shell
./goal clerk rawsend -f trade.sgtxn
```

