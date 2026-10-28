# MCP — Model Context Protocol / AI tool connections (Velvet Bloom)

## Decision: NOT required for the current MVP — and why
The MVP's 'AI' is deliberately rule-based Python (scoring, note similarity,
keyword chatbot, word-list sentiment). It needs no external model, no tool server
and no MCP connection. Adding MCP would add a dependency, a credential and a trust
boundary for zero MVP benefit, so it is documented as not required rather than built.

## If an LLM is ever added (future, optional only)
1. User need: only the chatbot (and optionally description generation) would gain
   from an LLM; recommendations already work without one.
2. Tools/data: one LLM API, given ONLY the matching catalog rows (name, price,
   stock, notes) and the user's question — never the whole DB, never passwords.
3. Trust boundaries: model output is data, never instructions; it must not change
   orders, prices, stock or roles. Server-side checks in AUTH.md still apply.
4. Auth/secrets: API key in a server-side env var only, never in frontend JS, never
   in git. Rotate if leaked. No key exists in this MVP.
5. Consent: an LLM answer is informational only; checkout, admin edits and deletes
   always require the user's own form POST, never a model action.
6. Schemas/timeouts/retries: a future integration must set a short timeout, one
   retry, and fall back to the current rule-based chatbot on any failure.
7. Prompt injection: treat retrieved/model text as data; never let a chat message
   override prices, roles or system rules; validate any product name the model
   returns against the catalog before showing it.
8. Privacy: minimise data sent to the provider (question + matched catalog rows
   only); do not send addresses, emails or order history.
9. Config: local dummy examples only; production key via env var, server-side.
10. Tests: mock the LLM in tests; verify catalog-only answers, fallback on failure,
    and that a model can never set a price or role.

## Conclusion
MCP/LLM: not built, not needed for MVP, documented here so a future builder does
not add it 'because it is available'. The rule-based chatbot is the MVP chatbot.
