# Optional local Qwen evidence-summary design

Status: approved and implemented on 2026-09-27. The user subsequently authorized all remaining phases and optional Mistral. Mistral uses the same bounded CLI selection, requires cloud consent and an environment credential, and never acts as automatic fallback. See the architecture addendum.

## Purpose

Help an examiner read a small evidence selection. Generated drafts require source-by-source human review. They are never signals, scores, compliance findings or review decisions. This command does not implement Phase 2 analytics.

## Recommended design

Add an explicitly invoked Python command and isolated local summarization adapter. Inputs: evidence root, immutable dataset ID, CSE ID, allowlisted record type, offset and limit (1–10). Verify artifact integrity before reading through the existing repository. Reject empty or oversized selections. Never read ground-truth labels.

Call only fixed loopback Ollama with the installed `qwen3.5:2b` model. Disable proxy inheritance and redirects; never pull models or fall back to cloud. Supply no model tools. Bound request/response size, output tokens and timeout. Missing model/service, timeout, malformed output and incomplete generation fail visibly with nonzero exit status. Application startup and health remain independent of Ollama.

Return JSON with unverified draft text, model identity, dataset/input hashes, selection metadata, original records and evidence references. Construct references from the input, not from generated text. References identify the supplied evidence set; they do not certify sentence-level grounding. Do not mutate evidence, metadata, signals or decisions. The caller may redirect standard output to a local file.

Treat evidence text as untrusted data, never instructions. Prompt constraints cannot eliminate hallucination or prompt injection. Output is untrusted plain text and must never be executed. Missing fields stay missing; summaries must not infer absence of action from absence of evidence.

## Alternatives

An in-app interface adds API, concurrency, UI and deployment scope; the approved feature remains a CLI. Mistral was subsequently requested and implemented as an optional Internet-connected provider. No credential is committed or included in draft output.

## Verification

Test entity/table scoping, label exclusion, artifact integrity, input bounds, loopback-only transport, unavailable/timeout/malformed responses and absence of persistence side effects. Run actual local Qwen inference and inspect its draft alongside sources. Run the existing regression suite. Report AI offline operation as unverified unless actual egress-denied inference succeeds; Phase 1's offline report does not verify this extension.

## Compatibility and limits

No normal evidence API, frontend, startup dependency or canonical domain contract changes are needed. The initial adapter is a native command; Docker remains independent of Ollama. Generated prose is not covered by synthetic dataset determinism. Hardware performance must be measured locally. An accepted design will be recorded as an explicit architecture addendum before implementation.
