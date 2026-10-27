"""PORTLGuardLite dashboard: Flask + web3.py.

Reads contract state and events through web3.py (server side).
Transactions (pause / unpause / protectedAction) are signed in the browser
with MetaMask, so no private key ever touches the server.
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from web3 import Web3

load_dotenv()

ROOT = Path(__file__).parent
RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
CHAIN_ID = os.getenv("CHAIN_ID", "")  # optional hint shown in the UI

ABI = json.loads((ROOT / "build" / "PORTLGuardLite.json").read_text())["abi"]

app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider(RPC_URL))


def get_contract():
    if not CONTRACT_ADDRESS:
        raise RuntimeError("CONTRACT_ADDRESS is not set. Run deploy.py first.")
    return w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/config")
def config():
    return jsonify(address=CONTRACT_ADDRESS, abi=ABI, rpc=RPC_URL, chainId=CHAIN_ID)


@app.get("/api/status")
def status():
    try:
        c = get_contract()
        return jsonify(
            connected=w3.is_connected(),
            address=c.address,
            owner=c.functions.owner().call(),
            paused=c.functions.paused().call(),
            block=w3.eth.block_number,
        )
    except Exception as exc:  # surface config/connection problems to the UI
        return jsonify(error=str(exc)), 500


@app.get("/api/events")
def events():
    try:
        c = get_contract()
        items = []
        for name in ("SecurityAlert", "Paused", "Unpaused"):
            for ev in getattr(c.events, name).get_logs(from_block=0):
                args = dict(ev["args"])
                items.append(
                    {
                        "event": name,
                        "block": ev["blockNumber"],
                        "tx": ev["transactionHash"].hex(),
                        "user": args.get("user") or args.get("by"),
                        "action": args.get("action", ""),
                        "_order": (ev["blockNumber"], ev["logIndex"]),
                    }
                )
        items.sort(key=lambda e: e.pop("_order"), reverse=True)
        return jsonify(events=items[:100])
    except Exception as exc:
        return jsonify(error=str(exc)), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
