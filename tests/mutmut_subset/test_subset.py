# Aggregates a stable subset of unit tests for mutation runs.
# This avoids collecting legacy/experimental tests during mutmut preprocessing.

from tests.unit.test_api_llm_chat_contract import *  # noqa: F401,F403
from tests.unit.test_api_llm_endpoints_contract import *  # noqa: F401,F403
from tests.unit.test_tce_endpoints_contract import *  # noqa: F401,F403
from tests.unit.test_server_misc_endpoints import *  # noqa: F401,F403
from tests.unit.test_llm_providers_openrouter import *  # noqa: F401,F403
