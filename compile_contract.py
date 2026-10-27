"""Compile contracts/PORTLGuardLite.sol and write build/PORTLGuardLite.json (abi + bytecode)."""
import json
from pathlib import Path

import solcx

ROOT = Path(__file__).parent
SOURCE = ROOT / "contracts" / "PORTLGuardLite.sol"
BUILD = ROOT / "build"
SOLC_VERSION = "0.8.24"


def compile_contract() -> Path:
    solcx.install_solc(SOLC_VERSION)
    result = solcx.compile_files(
        [str(SOURCE)],
        output_values=["abi", "bin"],
        solc_version=SOLC_VERSION,
    )
    _, data = next(iter(result.items()))
    BUILD.mkdir(exist_ok=True)
    out = BUILD / "PORTLGuardLite.json"
    out.write_text(json.dumps({"abi": data["abi"], "bytecode": data["bin"]}, indent=2))
    return out


if __name__ == "__main__":
    print("Wrote", compile_contract())
