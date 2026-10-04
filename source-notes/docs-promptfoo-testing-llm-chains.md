---
source_url: https://www.promptfoo.dev/docs/configuration/testing-llm-chains
source_type: docs
title: "Promptfoo: Testing LLM Chains — Script Provider, Custom Provider, End-to-End vs Unit Testing"
author: "Promptfoo (vendor documentation)"
date_published:
date_extracted: 2026-10-04
last_checked: 2026-10-04
status: current
confidence_overall: emerging
issue: "#1575"
---

# Promptfoo: Testing LLM Chains

> Promptfoo's documented approach for testing multi-step LLM chains: break into unit tests per step or test end-to-end by wrapping the chain behind a script provider (`exec:python ...`) or a custom JavaScript provider that shells out to an external chain implementation.

## Source Context

- **Type**: docs (vendor documentation)
- **Author credibility**: Promptfoo, vendor of the eval/red-team tool. First-party documentation of product patterns/config shapes.
- **Scope**: Describes two strategies for testing chains (unit tests per step vs end-to-end with single input/output), how to use the `exec` script provider to run an external script (e.g., LangChain `LLMMathChain`) that takes a prompt and prints output, and how to write a custom provider (`callApi(prompt, context)`) that spawns a subprocess (e.g., Python chain) and returns `{ output }`. Also notes call-count semantics (`# prompts * # test cases`), the `_conversation` built-in for referencing prior test-case outputs, and a link to RAG guidance. The page gives concrete `promptfooconfig.yaml` examples and a small Python example.
- **Last updated**: Oct 4, 2026 (page footer says "Last updated on Oct 4, 2026 by Michael") — current as of extraction.

## Extracted Claims

### Claim 1: Two complementary strategies for testing LLM chains — unit test each step vs end-to-end test with single input/output
- **Evidence**: The page states: "At a high level, you have these options: Break the chain into separate calls, and test those. This is useful if your testing strategy is closer to unit tests, rather than end to end tests. Test the full end-to-end chain, with a single input and single output. This is useful if you only care about the end result, and are not interested in how the LLM chain got there."
- **Confidence**: settled (documented pattern)
- **Quote**: "At a high level, you have these options:\n\n- Break the chain into separate calls, and test those. This is useful if your testing strategy is closer to unit tests, rather than end to end tests.\n- Test the full end-to-end chain, with a single input and single output. This is useful if you only care about the end result, and are not interested in how the LLM chain got there."
- **Our assessment**: This is a straightforward framing (unit vs e2e for chained behavior). Relevant to Ch05 (LLM-Ops Reliability) as a regression gating split for agent/chain pipelines; also maps loosely to Ch03 (Runbooks/Agents) thinking about test granularity.

### Claim 2: Script provider (`exec:`) allows testing external chains by running a script that takes a prompt/input and prints the chain’s final result
- **Evidence**: Example shows `providers: - openai:chat:gpt-5.4 - exec:python langchain_example.py` and `langchain_example.py` reads `sys.argv[1]` as the prompt and does `print(llm_math.run(prompt))`. The config’s `prompts: file://prompt.txt` contains `{{question}}`, and test cases provide `vars.question`.
- **Confidence**: settled
- **Quote**: "To test your chained LLMs, provide a script that takes a prompt input and outputs the result of the chain. This approach is language-agnostic." and the example config shows `- exec:python langchain_example.py`.
- **Our assessment**: Concrete harnessing pattern: wrap an external chain (LangChain) behind an `exec` script provider so promptfoo can evaluate it alongside other providers. No metrics/thresholds given, just the wiring.

### Claim 3: Custom provider via `callApi(prompt, context)` can shell out to an external implementation (even non-JS) and return `{ output }`
- **Evidence**: Provides `chainProvider.js` that uses Node `spawn('python', ['./path_to_your_python_chain.py', prompt])`, collects `stdout`, rejects on `stderr` or non-zero exit (`python script exited with code ${code}`), and resolves `{ output }`. Config references `./chainProvider.js`.
- **Confidence**: settled
- **Quote**: "A custom provider is a short Javascript file that defines a `callApi` function. This function can invoke your chain. Even if your chain is not implemented in Javascript, you can write a custom provider that shells out to Python." and shows rejection on stderr and on non-zero exit code.
- **Our assessment**: Explicit error-handling behavior in the custom provider example (reject on non-zero exit; reject on stderr). This is the documented failure handling for this pattern.

### Claim 4: Call count semantics are explicit: the script/custom provider runs once per (prompt × test case)
- **Evidence**: In the custom provider example: "In this case, the script will be called *# prompts* * *# test cases* = 2 * 2 = 4 times."
- **Confidence**: settled
- **Quote**: "promptfoo will pass the full constructed prompts to `chainProvider.js` and the Python script, with variables substituted. In this case, the script will be called *# prompts* * *# test cases* = 2 * 2 = 4 times."
- **Our assessment**: Important operational note for CI/runtime budgeting (cost/latency) when testing chains; explicitly stated.

### Claim 5: `_conversation` built-in allows referencing prior test-case outputs in chain-style eval contexts
- **Evidence**: "To reference the outputs of previous test cases, use the built-in [`_conversation` variable](/docs/configuration/chat/#using-the-conversation-variable)."
- **Confidence**: settled
- **Quote**: "To reference the outputs of previous test cases, use the built-in [`_conversation` variable](/docs/configuration/chat/#using-the-conversation-variable)."
- **Our assessment**: Identifies the state-passing mechanism available for multi-turn/chain scenarios in promptfoo tests.

## Concrete Artifacts

### Artifact 1: Script provider example (LangChain LLMMathChain)
```python
# langchain_example.py
import sys
import os
from langchain_openai import OpenAI
from langchain.chains.llm_math.base import LLMMathChain

llm = OpenAI(
    temperature=0,
    api_key=os.getenv('OPENAI_API_KEY'))
llm_math = LLMMathChain.from_llm(llm=llm)
prompt = sys.argv[1]
print(llm_math.run(prompt))
```

```yaml
prompts: file://prompt.txt
providers:
  - openai:chat:gpt-5.4
  - exec:python langchain_example.py
tests:
  - vars:
      question: What is the cube root of 389017?
  - vars:
      question: If you have 101101 in binary, what number does it represent in base 10?
  # ... additional test cases
```

(Attribution: from promptfoo docs "Testing LLM chains", https://www.promptfoo.dev/docs/configuration/testing-llm-chains)

### Artifact 2: Custom provider with subprocess and failure handling
```javascript
const { spawn } = require('child_process');

class ChainProvider {
  id() {
    return 'my-python-chain';
  }
  async callApi(prompt, context) {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', ['./path_to_your_python_chain.py', prompt]);
      let output = '';
      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      pythonProcess.stderr.on('data', (data) => {
        reject(data.toString());
      });
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(`python script exited with code ${code}`);
        } else {
          resolve({
            output,
          });
        }
      });
    });
  }
}

module.exports = ChainProvider;
```

(Attribution: from promptfoo docs "Testing LLM chains", https://www.promptfoo.dev/docs/configuration/testing-llm-chains)

## Cross-References

- **Corroborates**: 
  - `docs-promptfoo-configuration-guide.md` (overlap in config composition; this note adds chain-specific wiring patterns)
  - `docs-promptfoo-configuration-prompts.md` (template variables like `{{question}}`)
  - `docs-promptfoo-javascript-assertions.md` / `docs-promptfoo-python-assertions.md` (assertions on outputs; distinct topic)
- **Contradicts**: None observed.
- **Extends**: `docs-promptfoo-configuration-guide.md` by focusing specifically on chain-level testing (script/custom providers and unit-vs-e2e split). Builds on general provider/config concepts.
- **Novel**: The explicit documentation of testing LLM chains via `exec:` script provider and the custom provider subprocess pattern with specific failure handling (`stderr` rejection, non-zero exit code) and the stated call-count semantics (`# prompts * # test cases`) in this chain context. The built-in `_conversation` reference for prior test-case outputs as a chain state mechanism is also called out here.

## Guide Impact

- **Chapter 05 (LLM-Ops Reliability)**: Add concrete guidance on regression gating for LLM chains — recommend documenting the choice between unit-testing each chain step vs end-to-end testing. Include the promptfoo harness patterns: `exec:python <chain_script.py>` with the script taking input via `sys.argv[1]` and printing final output, and a custom JS provider using `spawn` with explicit handling of stderr/non-zero exit. Also capture the operational implication: evaluation runs the chain `# prompts × # test cases` times — relevant to CI runtime/cost budgeting.
- **Chapter 03 (Runbooks and Agents)**: For agent/chain pipelines, note the script-provider wrapper as a reusable pattern to exercise an external chain implementation as a testable unit in an eval harness; mention `_conversation` as a mechanism to reference prior test-case outputs when testing stateful chain behavior.

## Extraction Notes

- Page is vendor documentation; claims are documented product behavior/patterns (not measured empirical results). No metrics, no flake/timeout/gating thresholds, no incident data.
- Source is current (Oct 4, 2026). Example uses `openai:chat:gpt-5.4` (model name as shown in page).
- Read fully; extracted key config shapes, code artifacts, call semantics, and failure handling details.
- Related-notes candidates from lexical retrieval were mostly red-teaming and unrelated LiteLLM topics; none directly cover this chain-testing pattern, so cross-refs are limited to other promptfoo config notes.
