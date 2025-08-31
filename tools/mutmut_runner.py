from __future__ import annotations

import os
import sys
import pytest


def main() -> int:
    args = [
        "-c",
        "/dev/null",
        "-q",
        "tests/unit/test_api_llm_chat_contract.py",
        "tests/unit/test_api_llm_endpoints_contract.py",
        "tests/unit/test_tce_endpoints_contract.py",
        "tests/unit/test_server_misc_endpoints.py",
        "tests/unit/test_llm_providers_openrouter.py",
    ]
    sys.path.insert(0, os.getcwd())
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(main())
