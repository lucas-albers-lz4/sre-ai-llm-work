---
source_url: https://docs.litellm.ai/docs/mcp_aws_sigv4
source_type: docs
title: "MCP - AWS SigV4 Auth — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-10-28
last_checked: 2026-10-28
status: current
confidence_overall: emerging
issue: "#1902"
---

# MCP - AWS SigV4 Auth (LiteLLM Docs)

> LiteLLM's MCP Gateway supports outbound AWS SigV4 authentication to MCP servers hosted on AWS Bedrock AgentCore via an `httpx.Auth` subclass (`MCPSigV4Auth`) that signs every request with per-request SigV4 signatures using the boto3 credential chain, supports STS AssumeRole, requires URL-encoded AgentCore ARNs, skips startup health checks for SigV4-authenticated servers, and requires the `botocore` dependency.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, "MCP - AWS SigV4 Auth" page under the MCP Gateway docs)
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation. Authoritative for the surface LiteLLM exposes (config fields, auth mechanism, operational guidance), but documents capability not measured reliability. Claims stay at "the gateway documents this surface."
- **Scope**: Covers setup (UI/config), config reference for `aws_sigv4` auth, how SigV4 signing works, temporary credentials (STS), IAM role assumption (AssumeRole), and troubleshooting. Focuses specifically on connecting to AWS Bedrock AgentCore MCP servers via SigV4; does not cover general MCP auth patterns beyond this surface.

## Extracted Claims

### Claim 1: MCP outbound auth uses `auth_type: "aws_sigv4"` to sign every outgoing MCP request per-request with AWS Signature Version 4 (no static header reuse), handled automatically by an `httpx.Auth` subclass (`MCPSigV4Auth`)
- **Evidence**: "Why SigV4?" section states AWS uses per-request signing protocol including request body in cryptographic signature; "LiteLLM's `aws_sigv4` auth type handles this automatically: every outgoing MCP request is signed with your AWS credentials before it's sent." "How It Works" states LiteLLM uses `MCPSigV4Auth` that computes SHA-256 of request body, creates SigV4 signature using credentials/URL/headers/body hash, adds signed `Authorization` and `x-amz-date` headers.
- **Confidence**: emerging
- **Quote**: "LiteLLM uses an `httpx.Auth` subclass (`MCPSigV4Auth`) that hooks into the HTTP request lifecycle: 1. For every outgoing MCP request, the auth handler computes a SHA-256 hash of the request body 2. It creates a SigV4 signature using your AWS credentials, the request URL, headers, and body hash 3. The signed `Authorization` and `x-amz-date` headers are added to the request 4. AWS validates the signature and processes the MCP request"
- **Our assessment**: Distinct mechanism from static-header auth types (`api_key`, `bearer_token`); signing is per-request and body-aware. Confirms the `auth_type` enum expansion noted in `docs-litellm-gateway-auth-reference.md` Claim 2.

### Claim 2: Config requires `url` (AgentCore runtime ARN URL-encoded), `transport: "http"`, `auth_type: "aws_sigv4"`, and `aws_region_name` (required); `aws_service_name` defaults to `bedrock-agentcore`. Other fields optional with boto3 credential chain fallback.
- **Evidence**: Quick Start UI table and config.yaml examples plus Config Reference table.
- **Confidence**: emerging
- **Quote**: "| Field | Required | Description |\n|---|---|---|\n| `url` | Yes | AgentCore MCP server URL (with URL-encoded ARN) |\n| `transport` | Yes | Must be `\"http\"` |\n| `auth_type` | Yes | Must be `\"aws_sigv4\"` |\n| `aws_region_name` | Yes | AWS region (e.g., `us-east-1`) |\n| `aws_service_name` | No | AWS service name for signing. Defaults to `bedrock-agentcore` |"
- **Our assessment**: URL must contain URL-encoded ARN (explicit footgun documented). Region required for signing; service name defaults to AgentCore's expected value.

### Claim 3: Credential sources follow boto3 chain with explicit overrides; `aws_access_key_id`/`aws_secret_access_key`/`aws_session_token` support `os.environ/VAR_NAME` and fall back to boto3 credential chain if omitted. When editing existing SigV4 server, leave credential fields blank to keep current values.
- **Evidence**: UI table states "Falls back to boto3 credential chain if blank" for access keys; editing note says leave fields blank to keep current values.
- **Confidence**: emerging
- **Quote**: "**Editing credentials:** When editing an existing SigV4 server, leave credential fields blank to keep the current values. Only fields you fill in will be updated."
- **Our assessment**: Operational detail about credential update semantics (blank-on-edit preserves existing values) — important for avoiding accidental credential rotation.

### Claim 4: IAM role assumption via `aws_role_name` (ARN) triggers `sts:AssumeRole` using ambient/source credentials before signing; `aws_session_name` appears in CloudTrail and auto-generates if omitted. Can combine with explicit source keys.
- **Evidence**: AssumeRole section shows config with `aws_role_name`, states LiteLLM uses ambient credentials (pod role/instance profile/env vars) to call `sts:AssumeRole` then signs with assumed role's temp credentials; shows combining with explicit access keys as source identity.
- **Confidence**: emerging
- **Quote**: "For production environments where your LiteLLM instance authenticates via an IAM role (e.g., EKS pod role, EC2 instance profile), you can configure `aws_role_name` to have LiteLLM call `sts:AssumeRole` before signing MCP requests: ... LiteLLM uses the ambient credentials (pod role, instance profile, or env vars) to call `sts:AssumeRole`, then signs MCP requests with the assumed role's temporary credentials. You can also combine `aws_role_name` with explicit access keys. The keys are then used as the source identity for the AssumeRole call:"
- **Our assessment**: Production pattern for EKS/EC2; session name surfaces in CloudTrail for audit. Tip states for most K8s deployments only `aws_role_name` and `aws_region_name` needed (pod role provides source creds).

### Claim 5: SigV4-authenticated MCP servers skip the standard health check on proxy startup (expected behavior); tools remain usable and signing still works when invoked.
- **Evidence**: Troubleshooting section "Health check errors on startup": "SigV4-authenticated MCP servers skip the standard health check on proxy startup. This is expected, and the proxy will still sign requests correctly when tools are invoked."
- **Confidence**: emerging
- **Quote**: "SigV4-authenticated MCP servers skip the standard health check on proxy startup. This is expected, and the proxy will still sign requests correctly when tools are invoked."
- **Our assessment**: Reliability edge — operators get no readiness probe for these upstreams at startup; tool calls are the only liveness signal. Important operational gotcha.

### Claim 6: `botocore` is required for SigV4 auth; missing it produces `"botocore not found"` error. Install via `uv add botocore`.
- **Evidence**: Troubleshooting section states botocore required for SigV4 credential handling.
- **Confidence**: emerging
- **Quote**: "\"botocore not found\" error\n\nInstall the `botocore` package:\n\n```bash\nuv add botocore\n```\n\n`botocore` is used for SigV4 credential handling and is required when using `aws_sigv4` auth."
- **Our assessment**: Concrete dependency requirement for deployment planning.

### Claim 7: Common failures: 403 from region mismatch/expired creds/missing session token/wrong service name; AssumeRole AccessDenied from trust policy/IRSA annotation issues — check CloudTrail for AssumeRole call details.
- **Evidence**: Troubleshooting lists 403 causes and AssumeRole AccessDenied causes with remediation (check trust policy, IRSA service account annotation, CloudTrail).
- **Confidence**: emerging
- **Quote**: "### 403 Forbidden from AWS\n- Verify your AWS credentials are valid and not expired\n- Check that `aws_region_name` matches the region in your AgentCore URL\n- Ensure `aws_service_name` is set to `bedrock-agentcore`\n- If using STS credentials, confirm `aws_session_token` is set and not expired\n\n### AssumeRole AccessDenied\nIf you get `AccessDenied` when using `aws_role_name`:\n- Verify the role ARN is correct\n- Check that the trust policy on the target role allows your source identity to assume it\n- If running on EKS, ensure the pod's service account is annotated with the correct IAM role\n- Check CloudTrail for the failed `sts:AssumeRole` call to see the exact error"
- **Our assessment**: Concrete operational troubleshooting checklist for production deployments.

### Claim 8: AgentCore runtime ARN must be URL-encoded in the URL; example shows colon and slash encoding changes.
- **Evidence**: URL encoding admonition with concrete example transformation.
- **Confidence**: emerging
- **Quote**: "The AgentCore runtime ARN must be URL-encoded in the `url` field. For example:\n\n```\narn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/my-mcp-server\n```\n\nbecomes:\n\n```\narn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A123456789012%3Aruntime%2Fmy-mcp-server\n```"
- **Our assessment**: Concrete config footgun called out explicitly.

## Concrete Artifacts

### Config example (AssumeRole, recommended for production)
```yaml
mcp_servers:
  my_agentcore_mcp:
    url: "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/<url-encoded-ARN>/invocations"
    transport: "http"
    auth_type: "aws_sigv4"
    aws_role_name: "arn:aws:iam::123456789012:role/BedrockAgentCoreRole"
    aws_session_name: "litellm-prod"    # optional
    aws_region_name: "us-east-1"
    aws_service_name: "bedrock-agentcore"
```
(From source: LiteLLM docs MCP AWS SigV4 Auth - "Using IAM Role Assumption (AssumeRole)")

### Config example (STS temporary credentials)
```yaml
mcp_servers:
  my_agentcore_mcp:
    url: "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/<url-encoded-ARN>/invocations"
    transport: "http"
    auth_type: "aws_sigv4"
    aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID
    aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY
    aws_session_token: os.environ/AWS_SESSION_TOKEN
    aws_region_name: "us-east-1"
    aws_service_name: "bedrock-agentcore"
```
(From source: LiteLLM docs MCP AWS SigV4 Auth - "Using Temporary Credentials (STS)")

### Config example (AssumeRole with explicit source keys)
```yaml
mcp_servers:
  my_agentcore_mcp:
    url: "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/<url-encoded-ARN>/invocations"
    transport: "http"
    auth_type: "aws_sigv4"
    aws_role_name: os.environ/AWS_ROLE_ARN
    aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID
    aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY
    aws_region_name: "us-east-1"
```
(From source: LiteLLM docs MCP AWS SigV4 Auth - "Using IAM Role Assumption (AssumeRole)")

### Tool usage
```bash
curl http://localhost:4000/mcp-rest/tools/list \
  -H "Authorization: Bearer $LITELLM_API_KEY"
```
```bash
curl http://localhost:4000/mcp-rest/tools/call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -d '{
    "server_id": "my_agentcore_mcp",
    "name": "my_agentcore_mcp-your_tool_name",
    "arguments": {"key": "value"}
  }'
```
(From source: LiteLLM docs MCP AWS SigV4 Auth - "Use the MCP tools")

## Cross-References

- **Corroborates**: `source-notes/docs-litellm-gateway-auth-reference.md` (Claim 2) — confirms MCP uses first-class `auth_type` enum with `aws_sigv4` determining per-request SigV4 signature; this page is the dedicated deep-dive for that value explicitly marked "linked but not deep-dived" in the gateway auth reference.
- **Contradicts**: None identified.
- **Extends**: `source-notes/docs-litellm-gateway-auth-reference.md` — adds concrete operational details (AssumeRole chain, boto3 credential chain fallback, URL-encoded ARN footgun, health-check skip, botocore dependency, troubleshooting matrix) absent from the cross-reference page.
- **Novel**: Full operational surface for `aws_sigv4` MCP auth to Bedrock AgentCore (MCPSigV4Auth mechanism, credential source modes, AssumeRole patterns, startup health-check skip, botocore requirement, CloudTrail session naming, editing-credentials blank-on-edit semantics, region/service-name constraints, ARN URL-encoding). None of these details appear in existing notes.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add operational guidance for LiteLLM MCP Gateway connecting to Bedrock AgentCore via `auth_type: aws_sigv4` — cover dependency (`botocore`), URL-encoded ARN requirement, region/service-name correctness, health-check skip on startup (no readiness probe; tool calls are liveness signal), and troubleshooting (403 region/creds, AssumeRole AccessDenied/IRSA/trust policy/CloudTrail). Recommend production pattern using `aws_role_name` + ambient pod/instance role.
- **Chapter 06 (Security and Trust)**: Document SigV4 per-request signing (body SHA-256 + headers + URL) vs static-header auth, AssumeRole with session name surfacing in CloudTrail for audit, explicit-keys+role source identity, and credential-blank-on-edit semantics. Note trust policy and IRSA annotation requirements for AssumeRole flows.

## Extraction Notes

- Read the full page (HTML) via curl. Extracted all config tables, examples, mechanism description, AssumeRole variants, troubleshooting, and footnotes. Followed MINER.md §2a for quotes (verbatim). Cross-referenced against `docs-litellm-gateway-auth-reference.md` which explicitly notes this page is "linked but not deep-dived" — confirms this is complementary, not duplicative.
- Candidates from `miner-related-notes.md` reviewed; none were directly relevant to MCP AWS SigV4 auth surface. No contradictions found requiring filing.
