# INTEGRATIONS — Velvet Bloom external services

## Principle
The MVP needs NO external service and NO paid service. No real payment is taken.
This document records that decision and the future options, so nobody adds a paid
integration by accident.

## 1. Payments — NOT integrated (deliberate)
Purpose if ever needed: real checkout. Selected: none. Checkout is Demo/COD only:
the order is recorded, stock is reduced, and no money moves. A future payment
integration would have to validate amount/currency/order ownership/status on the
server and verify provider-signed webhooks, and must never trust a frontend
'success' screen. Do not connect a real paid service or perform a real transaction
without explicit approval — none is given here.

## 2. Email — NOT integrated
No signup verification, order email or notification is sent. Future email (if
wanted) would use a transactional provider with server-side credentials; not built.

## 3. Storage — NOT integrated
No product images are stored; products are described by text notes. No file upload
exists, so no storage permissions, private-file or CDN concerns arise.

## 4. AI / LLM — NOT integrated (see MCP.md)
No LLM API is called. The chatbot, finder, DNA matcher and sentiment are local
Python rules. Future LLM use is optional, server-side only, with fallback to the
rule-based chatbot.

## 5. Maps, SMS, analytics, social — NOT integrated
None are needed for the demo. No tracking scripts are included in any template.

## 6. Failure behaviour
Because there are no external calls, there is no external outage mode: every page
works offline on localhost. The only failure mode is local (DB file, port, venv) —
see SETUP.md troubleshooting.

## 7. Costs and limits
Cost: Rs 0 / $0 for the MVP (Flask + SQLite + local Python only). Any future
provider cost must be verified from current provider documentation before approval;
no cost figure is invented here.

## 8. Staging/production checklist (future only)
Set VELVET_SECRET_KEY, change the demo admin password, enable HTTPS, add rate
limiting and CSRF protection, audit-log admin actions, back up velvet.db, and only
then consider a payment provider — with its own sandbox test first.
