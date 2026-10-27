# PORTLGuard Lite: contract + Python web app

A small Flask dashboard (web3.py) for the `PORTLGuardLite` smart contract.
It shows the contract status, owner and recent events. Pause, unpause and the
protected action are signed in your browser with MetaMask, so no private key
is stored on the server.

> Note: this code was written but **not run** in the build environment (it had
> no access to PyPI or the Solidity compiler). Follow the steps below and send
> me any error you hit.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python compile_contract.py       # writes build/PORTLGuardLite.json
```

## Run locally (easiest)

1. Start a local chain in another terminal, e.g. `anvil` (Foundry) or `npx hardhat node`.
2. Deploy: `python deploy.py` (writes `CONTRACT_ADDRESS` to `.env`).
3. Start the app: `python app.py`, then open http://127.0.0.1:5000
4. In MetaMask, add the local network (RPC `http://127.0.0.1:8545`, chain id 31337 for anvil/hardhat)
   and import the first test account, which is the contract owner.

## Run on a testnet (e.g. Sepolia)

Create `.env`:

```
RPC_URL=https://your-sepolia-rpc-url
PRIVATE_KEY=0x...        # a throwaway test wallet, never a real one
```

Then run `python deploy.py` and `python app.py`. Switch MetaMask to Sepolia.

## Files

| File | Purpose |
|---|---|
| `contracts/PORTLGuardLite.sol` | The contract (completed from your paste) |
| `compile_contract.py` | Compiles the contract to ABI + bytecode |
| `deploy.py` | Deploys and saves the address in `.env` |
| `app.py` | Flask server: `/api/status`, `/api/events`, `/api/config` |
| `templates/index.html` | The dashboard (MetaMask via ethers.js) |

## About the contract

- Only the owner can `pause()` and `unpause()`.
- `protectedAction()` works for anyone, but only while not paused, and emits `SecurityAlert`.
- There is no `transferOwnership`, so the deploying wallet stays owner forever. Add one if you need to hand over control.

## PORTLG standalone dashboard (additional uploaded file)

`index.html` is the separate static dashboard supplied for Portaldot V3. It uses ethers.js and the hardcoded PORTLGuardLite contract address `0x44406CD3e7ccE420c316D015FEE74303F16629E5`. Open it via a local static web server; it does not depend on Flask.

`templates/index.html` is the original Flask dashboard used by `app.py`. Both are retained deliberately; the Flask version requires a compiled ABI in `build/` and environment configuration. They are alternative frontends, **not yet a unified app**.

This repository contains the PORTLGuardLite security demonstration only. It does **not** implement functional token swapping or cross-chain bridging. Deployment and network functionality must be independently verified. Never commit `.env`, private keys, or wallet backup files.
