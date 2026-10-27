"""Deploy PORTLGuardLite and write CONTRACT_ADDRESS to .env.

Local node (anvil / hardhat node, accounts unlocked, no key needed):
    python deploy.py

Real network (e.g. Sepolia):
    set RPC_URL and PRIVATE_KEY in .env, then:  python deploy.py
"""
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

ROOT = Path(__file__).parent
load_dotenv()


def load_build():
    path = ROOT / "build" / "PORTLGuardLite.json"
    if not path.exists():
        sys.exit("Run `python compile_contract.py` first.")
    return json.loads(path.read_text())


def write_env(key: str, value: str):
    env = ROOT / ".env"
    lines = env.read_text().splitlines() if env.exists() else []
    lines = [l for l in lines if not l.startswith(f"{key}=")]
    lines.append(f"{key}={value}")
    env.write_text("\n".join(lines) + "\n")


def main():
    build = load_build()
    rpc = os.getenv("RPC_URL", "http://127.0.0.1:8545")
    w3 = Web3(Web3.HTTPProvider(rpc))
    if not w3.is_connected():
        sys.exit(f"Cannot connect to {rpc}. Start a node (e.g. `anvil` or `npx hardhat node`) or set RPC_URL.")

    key = os.getenv("PRIVATE_KEY")
    contract = w3.eth.contract(abi=build["abi"], bytecode=build["bytecode"])

    if key:
        acct = w3.eth.account.from_key(key)
        tx = contract.constructor().build_transaction(
            {"from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address)}
        )
        signed = acct.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    else:  # local dev node with unlocked accounts
        tx_hash = contract.constructor().transact({"from": w3.eth.accounts[0]})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Deployed at", receipt.contractAddress)
    write_env("CONTRACT_ADDRESS", receipt.contractAddress)
    write_env("RPC_URL", rpc)


if __name__ == "__main__":
    main()
