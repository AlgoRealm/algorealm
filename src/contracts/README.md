# AlgoRealm Depoloyment

The following procedure describe the AlgoRealm depoloyment process, which could
be useful in case of testing purposes. The deployment process consists in 4
steps: three for the artifacts creation and one for the artifacts binding.

### 1. AlgoRealm Test ASAs

#### Crown of Test

Creates the *Crown of Test* ASA with:

- Name: `Crown of Test`
- Unit Name: `CROWN`
- Total: `1`
- Decimals: `0`
- `manager` and the `clawback` addresses active;

Get the `TEST_CROWN_ID`.

#### Sceptre of Test

Creates the *Sceptre of Test* ASA with:

- Name: `Sceptre of Test`
- Unit Name: `SCEPTRE`
- Total: `1`
- Decimals: `0`
- `manager` and the `clawback` addresses active;

Get the `TEST_SCEPTRE_ID`.

### 2. AlgoRealm Test App

Depoloy the *AlgoRealm Test App* with:

- Approval Program: `algorealm_approval.teal` (compiling TEAL to AVM bytecode);
- Clear Program: `algorealm_clear.teal` (compiling TEAL to AVM bytecode);
- Global Ints: `2`;
- Global Bytes: `3`;
- Local Ints: `0`;
- Local Bytes: `0`;

Get the `TEST_ALGOREALM_APP_ID`.

### 3. AlgoRealm Test Law

Replace the `TMPL_` parameters in the `tmpl_algorealm_law.teal` Smart Signature
with the `TEST_` IDs obtained in the previous steps, specifically:

1. The `TEST_ALGOREALM_APP_ID` here:

```teal
// To the AlgoRealm App
gtxn 0 ApplicationID
int TMPL_ALGOREALM_APP_ID
```

2. The `TEST_CROWN_ID` and the `TEST_SCEPTRE_ID` here:

```teal
// Either of the Crown of Entropy
gtxn 2 XferAsset
int TMPL_CROWN_ASA_ID
==
// Or of the Sceptre of Proof
gtxn 2 XferAsset
int TMPL_SCEPTRE_ASA_ID
```

Save the updated TEAL source code as `algorealm_test_law.teal` and then compile
it to obtain the public key `TEST_ALGOREALM_ADDR` associated to the Smart
Signature.

Fund the `TEST_ALGOREALM_ADDR` with some ALGOs.

## 4. Bindings

Once all the artifacts are ready:

- `TEST_CROWN_ID`;
- `TEST_SCEPTRE_ID`;
- `TEST_ALGOREALM_APP_ID`;
- `TEST_ALGOREALM_ADDR`;

They must be **binded** as follows:

1. As a `manager`, set `TEST_ALGOREALM_ADDR` as `clawback` address of `TEST_CROWN_ID`;
2. As a `manager`, set `TEST_ALGOREALM_ADDR` as `clawback` address of `TEST_SCEPTRE_ID`;
3. Call the `TEST_ALGOREALM_APP_ID` passing the `TEST_ALGOREALM_ADDR` as first argument of the AppCall.

A new testing instance of AlgoRealm is now succesfully depolyed!
