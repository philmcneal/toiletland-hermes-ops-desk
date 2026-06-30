const fallbackQueue = [
  {
    "id": "earn-001",
    "lane": "Earn",
    "title": "Fit-check customer without sending anything",
    "source": "Redacted customer asks: ‘Will a warm-water seat fit my skirted toilet, and is there a lower-risk option under my budget?’ [name/email/order removed]",
    "summary": "Turn a messy product-fit question into a margin-safe recommendation and Phil-style reply draft.",
    "business_impact": "Saves the sale while preventing a bad fit recommendation.",
    "risk": "medium",
    "status": "needs-owner",
    "source_type": "redacted email snippet",
    "approval_required": true,
    "recommended_action": "Draft a human reply recommending a compatible bidet lane, explain fit caveats, and ask for a toilet photo before final purchase if uncertain.",
    "proof_assets": [
      "earn-fit-check-redacted",
      "earn-phil-draft-redacted"
    ],
    "reasoning": [
      "Customer wants fit confidence, not a generic product dump.",
      "Recommendation should avoid overpromising compatibility from incomplete info.",
      "Owner approval is required before any customer-facing send."
    ]
  },
  {
    "id": "operate-001",
    "lane": "Operate",
    "title": "Fulfillment/tracking dry-run for a ready order",
    "source": "Redacted order event: paid order is ready for fulfillment. All customer identifiers, address, order number, and tracking number are fake.",
    "summary": "Prepare WooCommerce status/tracking-sync preview and local audit entry without touching live WooCommerce.",
    "business_impact": "Cuts fulfillment follow-up time without mutating WooCommerce.",
    "risk": "low",
    "status": "ready-demo",
    "source_type": "redacted order/log snippet",
    "approval_required": true,
    "recommended_action": "Show a dry-run tracking sync: label found, status update prepared, audit row generated, live update disabled.",
    "proof_assets": [
      "operate-tracking-sync-redacted",
      "audit-log-redacted"
    ],
    "reasoning": [
      "The demo proves operational viability without booking labels or mutating WooCommerce.",
      "Fake IDs keep customer/order data out of the recording.",
      "Audit preview shows what would happen after owner approval."
    ]
  },
  {
    "id": "spend-001",
    "lane": "Spend",
    "title": "Stripe revenue + Google Ads growth loop blocked by approval gate",
    "source": "Redacted repair case: customer may owe extra shipping or a bench diagnosis may require extra parts. Dollar amounts, customer identity, and vendor identity are fixture-only.",
    "summary": "Display a Stripe Skills dry-run rail and Google Ads draft loop: collect repair revenue, approve parts spend, then draft profitable ad-budget changes without live API calls.",
    "business_impact": "Shows a closed commerce loop: earn money with Stripe, control spend, then reinvest only when margin and owner approval clear.",
    "risk": "high",
    "status": "blocked-owner",
    "source_type": "redacted vendor/provisioning note",
    "approval_required": true,
    "recommended_action": "Open the Payments rail: draft Stripe Payment Link / Checkout / spend payloads, then show the Google Ads growth draft that remains blocked until Phu approves live ad spend.",
    "proof_assets": [
      "stripe-payment-link-payload",
      "stripe-checkout-payload",
      "parts-spend-policy",
      "google-ads-budget-draft",
      "owner-approval-audit-row"
    ],
    "reasoning": [
      "The sponsor-fit story is agentic commerce: earn/collect revenue, control spend, and decide where growth dollars go.",
      "Stripe conversion/spend signals become evidence for Google Ads budget drafts, not automatic ad spend.",
      "The demo uses test fixtures only: no Stripe key, no live Payment Link, no Checkout Session, no charge, no purchase, no Google Ads API call, and no campaign publish."
    ]
  },
  {
    "id": "warranty-001",
    "lane": "Warranty",
    "title": "Warranty Command Center — internal dashboard first",
    "source": "Redacted warranty board fixture: multiple cases need symptom triage, repair path, parts/refurb inventory, supplier/RMA gates, and owner approval. No real names, emails, addresses, or order IDs are present.",
    "summary": "Turn warranty mental debt into a controlled internal command center before any customer, supplier, WooCommerce, shipping, or refund action.",
    "business_impact": "Makes overdue warranty pressure visible without touching live customers or vendors.",
    "risk": "high",
    "status": "needs-owner",
    "source_type": "redacted warranty Kanban fixture",
    "approval_required": true,
    "recommended_action": "Open the Warranty Command Center below: triage fake cases by symptom, repair path, part/refurb gate, supplier/RMA gate, and local audit trail. Keep all live actions disabled.",
    "proof_assets": [
      "warranty-board-redacted",
      "symptom-to-part-map-redacted",
      "parts-inventory-redacted",
      "repair-bench-checklist"
    ],
    "reasoning": [
      "The real business bottleneck is not one email; it is case state, repair state, inventory, and approval state scattered across tools.",
      "Internal dashboard first prevents exposing messy status to customers before the workflow is reliable.",
      "Every risky action remains owner-gated: reply, label, supplier escalation, refund, replacement, or refurb match."
    ]
  }
];

const fallbackAudit = [
  {
    "at": "2026-06-24 13:22 PDT",
    "actor": "Hermes",
    "item_id": "earn-001",
    "event": "Queued fit-check task from redacted fixture",
    "outcome": "needs-owner"
  },
  {
    "at": "2026-06-24 13:23 PDT",
    "actor": "Hermes",
    "item_id": "operate-001",
    "event": "Prepared fulfillment/tracking dry-run preview",
    "outcome": "ready-demo"
  },
  {
    "at": "2026-06-24 13:24 PDT",
    "actor": "Hermes",
    "item_id": "spend-001",
    "event": "Blocked spend/provisioning behind owner approval",
    "outcome": "blocked-owner"
  },
  {
    "at": "2026-06-24 14:22 PDT",
    "actor": "Hermes",
    "item_id": "warranty-command-center",
    "event": "Loaded redacted warranty command center fixtures: case queue, repair path, parts/refurb gate, supplier/RMA gate",
    "outcome": "needs-owner"
  },
  {
    "at": "2026-06-24 14:24 PDT",
    "actor": "Hermes",
    "item_id": "payment-approval-rail",
    "event": "Prepared Stripe Skills dry-run payment/spend approval rail; live Stripe API and credentials disabled",
    "outcome": "blocked-owner"
  },
  {
    "at": "2026-06-28 00:00 PDT",
    "actor": "Hermes",
    "item_id": "email-command-center",
    "event": "Loaded fake/redacted Email Command Center fixtures: read-only triage, draft-only replies, disabled send and mark-read controls",
    "outcome": "needs-owner"
  },
  {
    "at": "2026-06-28 00:01 PDT",
    "actor": "Hermes",
    "item_id": "agent-pulse",
    "event": "Rendered sanitized Agent Pulse schedule proposal from fixture data; no live cron or Telegram target touched",
    "outcome": "proposal-only"
  },
  {
    "at": "2026-06-29 13:15 PDT",
    "actor": "Hermes",
    "item_id": "stripe-skill-dry-run",
    "event": "Rendered test-fixture Stripe Skill payloads for Payment Link, Checkout quote, and parts spend approval; no API request sent",
    "outcome": "proposal-only"
  },
  {
    "at": "2026-06-29 13:35 PDT",
    "actor": "Hermes",
    "item_id": "stripe-google-ads-growth-loop",
    "event": "Rendered Stripe→Google Ads dry-run revenue loop: paid/approved Stripe signals can draft campaign budget and keyword changes; live Ads API and ad spend disabled",
    "outcome": "proposal-only"
  }
];

const fallbackWarrantyCases = [
  {
    "id": "warranty-case-001",
    "title": "BB-2000 no-spray warranty triage",
    "brand": "BioBidet",
    "model_family": "BB-2000",
    "symptom": "Nozzle extends, but no water sprays after filter/nozzle cleaning. Customer/order identity is fixture-only.",
    "status": "needs-owner",
    "severity": "high",
    "customer_state": "Evidence request draft prepared: serial sticker, short video, current address confirmation.",
    "next_gate": "Phu chooses repair intake vs tested refurb swap after evidence is reviewed.",
    "approval_copy": "Approve draft-only evidence request",
    "repair_path": [
      "Verify order/warranty and exact seat type before any promise.",
      "Ask for serial, short video, and current shipping address.",
      "Map likely solenoid/internal valve path if wand extends with no spray.",
      "Offer repair intake or tested refurb swap only after Phu approval."
    ],
    "parts": [
      "1ZBB2000-SLNOID",
      "1ZBB2000-NOZZLE only if track/nozzle issue",
      "tested BB-2000 refurb candidate"
    ],
    "proof_assets": [
      "redacted-customer-thread",
      "symptom-to-part-reference",
      "warranty-kanban-card-redacted"
    ],
    "timeline": [
      "Fixture email summarized locally",
      "Hermes classified symptom and evidence gap",
      "No email sent; owner approval required"
    ],
    "audit_note": "Internal warranty queue only; no customer email, label, or WooCommerce action."
  },
  {
    "id": "warranty-case-002",
    "title": "DLS/Horizon power-failure service recovery",
    "brand": "BioBidet",
    "model_family": "DLS / Horizon",
    "symptom": "No power after outlet check; overdue follow-up risk. Names, order numbers, and addresses are removed.",
    "status": "needs-owner",
    "severity": "high",
    "customer_state": "Service-recovery draft is ready, but needs Phu approval before contact.",
    "next_gate": "Decide whether to request PCB repair path, repair intake, or replacement/refurb path.",
    "approval_copy": "Approve service-recovery draft only",
    "repair_path": [
      "Confirm DLS/Horizon family and warranty coverage.",
      "Avoid making customer repeat basic outlet diagnostics.",
      "Use PCB/internal fuse path first if repair bench is chosen.",
      "Verify current address before any replacement or label."
    ],
    "parts": [
      "1ZDLS-MPCB / 1ZMEG-DLSMNPCB",
      "DLS/Horizon refurb candidate",
      "repair intake label draft only"
    ],
    "proof_assets": [
      "redacted-overdue-thread",
      "repair-path-reference",
      "address-verification-checklist"
    ],
    "timeline": [
      "Fixture case marked urgent",
      "Hermes found likely repair family",
      "External reply blocked until owner approval"
    ],
    "audit_note": "Service-recovery path visible, but no message leaves the machine."
  },
  {
    "id": "warranty-case-003",
    "title": "Supplier RMA / send-in repair gate",
    "brand": "H4H / Ultra-Nova",
    "model_family": "Ultra-Nova family",
    "symptom": "Supplier repair/RMA path exists, but customs, label, and customer instructions need owner sign-off.",
    "status": "blocked-owner",
    "severity": "medium",
    "customer_state": "RMA checklist prepared with fake reference codes and no real destination data.",
    "next_gate": "Phu approves exact boxed contents, customs values, and whether to book label.",
    "approval_copy": "Approve RMA checklist only",
    "repair_path": [
      "Verify boxed contents and accessories before label.",
      "Confirm customs/declared value assumptions.",
      "Prepare supplier/customer tracking drafts only.",
      "Book no label until Phu explicitly approves."
    ],
    "parts": [
      "supplier-RMA-placeholder",
      "customs-checklist",
      "label-dry-run-artifact"
    ],
    "proof_assets": [
      "redacted-rma-thread",
      "dry-run-label-json-redacted",
      "supplier-policy-note"
    ],
    "timeline": [
      "RMA path recognized",
      "Hermes generated preflight checklist",
      "Booking controls disabled"
    ],
    "audit_note": "No Freightcom, supplier, or customer system is touched."
  },
  {
    "id": "warranty-case-004",
    "title": "Returned-unit refurb inventory intake",
    "brand": "BioBidet",
    "model_family": "BB-2000 / DLS / Horizon",
    "symptom": "Returned seats need physical ID, model confirmation, repair status, and refurb readiness before reuse.",
    "status": "ready-demo",
    "severity": "medium",
    "customer_state": "Physical-bench checklist generated; case is not tied to a real customer in demo data.",
    "next_gate": "Phu labels boxes, photos stickers/accessories, and runs bench test before matching to any customer.",
    "approval_copy": "Approve inventory checklist only",
    "repair_path": [
      "Assign internal inventory ID to each physical unit.",
      "Photograph model/serial sticker, box label, accessories, and seat shape.",
      "Bench test power, wash, heat, dryer, nozzle movement, and leaks.",
      "Only mark refurb-ready after repair and sustained testing."
    ],
    "parts": [
      "physical-inventory-id",
      "bench-test-checklist",
      "refurb-ready gate"
    ],
    "proof_assets": [
      "redacted-bench-photo-slot",
      "inventory-csv-redacted",
      "repair-log-redacted"
    ],
    "timeline": [
      "Returned-unit lead created",
      "Hermes blocks premature customer match",
      "Bench verification required"
    ],
    "audit_note": "Inventory control stays local until physical verification exists."
  }
];

const fallbackPaymentRequests = [
  {
    "id": "pay-001",
    "title": "Collect extra warranty shipping with Stripe Payment Link draft",
    "kind": "Stripe Payment Link draft",
    "amount_label": "CA$18.95 fixture amount",
    "status": "needs-owner",
    "risk": "high",
    "processor": "Stripe Skills dry-run adapter — Payment Link payload prepared; live API disabled",
    "customer_or_vendor_state": "Customer approved repair intake, but return shipping/box supplies are not covered. Identity and order data are fixture-only.",
    "reason": "Hermes prepares the Stripe Payment Link request, customer-facing explanation, line items, metadata, and idempotency key, but cannot create or send the live link until Phu approves.",
    "approval_copy": "Approve Stripe Payment Link draft only",
    "line_items": [
      "Return-shipping contribution — CA$14.95 fixture",
      "Repair intake packaging/admin — CA$4.00 fixture"
    ],
    "guardrails": [
      "Stripe live API disabled — test fixture only",
      "No Stripe Payment Link created",
      "No customer message sent",
      "No card charged or stored",
      "Owner must approve amount, reason, wording, and destination before any live call",
      "No Google Ads campaign published",
      "No ad spend committed"
    ],
    "disabled_actions": [
      "Create live Stripe Payment Link",
      "Send customer request",
      "Charge card",
      "Refund/void",
      "Publish Google Ads change",
      "Increase ad budget"
    ],
    "proof_assets": [
      "redacted-repair-thread",
      "stripe-payment-link-payload-fixture",
      "draft-payment-request-preview",
      "owner-approval-audit-row",
      "google-ads-growth-loop-fixture",
      "owner-ad-spend-approval-row"
    ],
    "audit_note": "Stripe Skill payload is rendered and audit-ready; money movement stays disabled in demo mode.",
    "stripe_skill": {
      "skill": "stripe.payment_link.draft",
      "mode": "test_fixture_no_api_call",
      "proposed_call": "payment_links.create",
      "currency": "cad",
      "amount_cents": 1895,
      "idempotency_key": "demo-pay-001-owner-approval-required",
      "payload": {
        "line_items": [
          {
            "name": "Return-shipping contribution",
            "unit_amount": 1495,
            "quantity": 1
          },
          {
            "name": "Repair intake packaging/admin",
            "unit_amount": 400,
            "quantity": 1
          }
        ],
        "metadata": {
          "demo": "hermes-business-hackathon",
          "toiletland_case": "fixture-pay-001",
          "approval_required": "true",
          "live_connectors": "off"
        },
        "after_completion": {
          "type": "redirect",
          "redirect_url": "https://toiletland.ca/demo/thank-you?fixture=pay-001"
        }
      }
    },
    "growth_loop": {
      "label": "Stripe → Google Ads recovery loop",
      "mode": "test_fixture_no_api_call",
      "signal": "If the owner-approved Stripe Payment Link is paid, Hermes records a CA$18.95 repair-shipping recovery signal instead of treating warranty work as pure cost.",
      "proposed_call": "google_ads.campaign_budget.mutate + google_ads.campaign_criterion.mutate",
      "proposed_action": "Draft a CA$25/day high-intent Search test for bidet repair/replacement demand while blocking warranty-sensitive terms until the owner approves.",
      "budget_label": "CA$25/day fixture budget",
      "roas_guardrail": "Publish only if Stripe payment clears, gross-margin target is ≥35%, high-risk warranty backlog is ≤8, and Phu approves the ad spend.",
      "payload": {
        "customer_id": "demo-google-ads-customer-redacted",
        "campaign": "Toiletland high-intent bidet repair/replacement — fixture",
        "conversion_source": "stripe.payment_link.paid fixture",
        "operations": [
          {
            "type": "campaign_budget",
            "daily_budget_cad": 25,
            "status": "draft_owner_approval_required"
          },
          {
            "type": "search_terms",
            "include": [
              "bidet repair canada",
              "bidet seat replacement",
              "warm water bidet service"
            ]
          },
          {
            "type": "negative_keywords",
            "add": [
              "free warranty replacement",
              "broken bidet warranty",
              "complaint refund"
            ]
          },
          {
            "type": "conversion_label",
            "value_source": "stripe_amount_cents",
            "currency": "CAD"
          }
        ],
        "safety": {
          "owner_approval_required": true,
          "live_connectors": "off",
          "no_api_call": true,
          "no_ad_spend": true,
          "max_daily_budget_cad": 25
        }
      }
    }
  },
  {
    "id": "pay-002",
    "title": "Approve parts spend through Stripe Skills spend rail",
    "kind": "Stripe spend approval draft",
    "amount_label": "CA$42.00 fixture amount",
    "status": "blocked-owner",
    "risk": "high",
    "processor": "Stripe Skills dry-run adapter — parts spend/provisioning request prepared; live purchase disabled",
    "customer_or_vendor_state": "Bench diagnosis suggests solenoid/nozzle kit may be needed. Vendor identity, SKU cost, and quantity are fixture-only.",
    "reason": "Hermes maps the repair diagnosis to a Stripe-style spend approval packet with amount, vendor category, policy reason, and metadata. It cannot pay a vendor, provision a service, or buy inventory without owner approval.",
    "approval_copy": "Approve Stripe spend draft only",
    "line_items": [
      "Solenoid/nozzle repair kit — CA$32.00 fixture",
      "Inbound shipping estimate — CA$10.00 fixture"
    ],
    "guardrails": [
      "Stripe live API disabled — test fixture only",
      "No vendor checkout opened or paid",
      "No payment credential used",
      "No purchase order sent",
      "Inventory count remains fixture-only",
      "Owner can reject if margin/stock does not justify it",
      "No Google Ads campaign published",
      "No ad spend committed"
    ],
    "disabled_actions": [
      "Approve live Stripe spend",
      "Open vendor checkout",
      "Pay invoice",
      "Create PO",
      "Update inventory",
      "Publish Google Ads change",
      "Increase ad budget"
    ],
    "proof_assets": [
      "symptom-to-part-map-redacted",
      "stripe-spend-payload-fixture",
      "parts-cost-preview",
      "owner-spend-policy",
      "google-ads-growth-loop-fixture",
      "owner-ad-spend-approval-row"
    ],
    "audit_note": "Parts spend payload is prepared for a Stripe Skill handoff, but live spend stays blocked until owner approval.",
    "stripe_skill": {
      "skill": "stripe.spend_approval.draft",
      "mode": "test_fixture_no_api_call",
      "proposed_call": "spend_approval.create",
      "currency": "cad",
      "amount_cents": 4200,
      "idempotency_key": "demo-pay-002-owner-approval-required",
      "payload": {
        "spend_type": "repair_parts",
        "merchant_category": "bidet repair parts supplier",
        "line_items": [
          {
            "name": "Solenoid/nozzle repair kit",
            "unit_amount": 3200,
            "quantity": 1
          },
          {
            "name": "Inbound shipping estimate",
            "unit_amount": 1000,
            "quantity": 1
          }
        ],
        "policy": {
          "owner_approval_required": true,
          "max_fixture_amount_cents": 4200,
          "reason": "bench diagnosis suggests part may be needed"
        },
        "metadata": {
          "demo": "hermes-business-hackathon",
          "toiletland_case": "fixture-pay-002",
          "live_connectors": "off"
        }
      }
    },
    "growth_loop": {
      "label": "Stripe spend → Ads inventory guard",
      "mode": "test_fixture_no_api_call",
      "signal": "If parts spend is approved, Hermes knows which repair capacity exists before buying traffic into a stockout.",
      "proposed_call": "google_ads.campaign_criterion.mutate",
      "proposed_action": "Draft campaign pauses or negative keywords for models whose repair parts are not owner-approved or bench-ready.",
      "budget_label": "CA$0 until parts gate clears",
      "roas_guardrail": "No ads for repair promises until parts spend, margin, and bench capacity are approved.",
      "payload": {
        "customer_id": "demo-google-ads-customer-redacted",
        "conversion_source": "stripe.spend_approval.approved fixture",
        "operations": [
          {
            "type": "pause_ad_group",
            "reason": "parts approval not cleared"
          },
          {
            "type": "negative_keywords",
            "add": [
              "same day bidet repair",
              "guaranteed repair"
            ]
          }
        ],
        "safety": {
          "owner_approval_required": true,
          "live_connectors": "off",
          "no_api_call": true,
          "no_ad_spend": true
        }
      }
    }
  },
  {
    "id": "pay-003",
    "title": "Draft Stripe Checkout quote for paid repair upgrade",
    "kind": "Stripe Checkout quote draft",
    "amount_label": "CA$79.00 fixture estimate",
    "status": "quote-only",
    "risk": "medium",
    "processor": "Stripe Skills dry-run adapter — Checkout Session payload prepared; no live session created",
    "customer_or_vendor_state": "Out-of-warranty unit can be repaired if the customer accepts paid upgrade. All identifiers are fake/redacted.",
    "reason": "Hermes prepares a Stripe Checkout-style repair quote with line items, consent copy, and metadata, then waits for Phu before any customer-facing payment collection starts.",
    "approval_copy": "Approve Stripe Checkout quote draft only",
    "line_items": [
      "Out-of-warranty repair labour — CA$49.00 fixture",
      "Replacement internal component — CA$20.00 fixture",
      "Return shipping estimate — CA$10.00 fixture"
    ],
    "guardrails": [
      "Stripe live API disabled — test fixture only",
      "No promise of repair success before bench check",
      "No live Checkout Session or Payment Link",
      "No email/SMS sent",
      "No refund/replacement triggered",
      "Clear customer consent required",
      "No Google Ads campaign published",
      "No ad spend committed"
    ],
    "disabled_actions": [
      "Create live Stripe Checkout Session",
      "Email quote",
      "Collect deposit",
      "Book return label",
      "Publish Google Ads change",
      "Increase ad budget"
    ],
    "proof_assets": [
      "repair-estimate-template",
      "stripe-checkout-payload-fixture",
      "customer-consent-checklist",
      "audit-preview",
      "google-ads-growth-loop-fixture",
      "owner-ad-spend-approval-row"
    ],
    "audit_note": "Stripe Checkout payload preview is safe for judges; customer payment collection remains disabled.",
    "stripe_skill": {
      "skill": "stripe.checkout_session.draft",
      "mode": "test_fixture_no_api_call",
      "proposed_call": "checkout.sessions.create",
      "currency": "cad",
      "amount_cents": 7900,
      "idempotency_key": "demo-pay-003-owner-approval-required",
      "payload": {
        "mode": "payment",
        "line_items": [
          {
            "name": "Out-of-warranty repair labour",
            "unit_amount": 4900,
            "quantity": 1
          },
          {
            "name": "Replacement internal component",
            "unit_amount": 2000,
            "quantity": 1
          },
          {
            "name": "Return shipping estimate",
            "unit_amount": 1000,
            "quantity": 1
          }
        ],
        "consent_required": true,
        "metadata": {
          "demo": "hermes-business-hackathon",
          "toiletland_case": "fixture-pay-003",
          "approval_required": "true",
          "live_connectors": "off"
        }
      }
    },
    "growth_loop": {
      "label": "Checkout quote → remarketing draft",
      "mode": "test_fixture_no_api_call",
      "signal": "If a paid repair Checkout quote is accepted, Hermes can classify it as profitable service demand instead of abandoned support load.",
      "proposed_call": "google_ads.asset_group_signal.mutate",
      "proposed_action": "Draft a remarketing / Performance Max signal for paid repair upgrades, excluding unresolved warranty customers.",
      "budget_label": "CA$15/day fixture remarketing cap",
      "roas_guardrail": "Only publish if accepted Stripe quotes beat 2.5× ROAS and unresolved warranty pressure is below threshold.",
      "payload": {
        "customer_id": "demo-google-ads-customer-redacted",
        "conversion_source": "stripe.checkout.session.completed fixture",
        "operations": [
          {
            "type": "audience_signal",
            "name": "paid repair upgrade intent fixture"
          },
          {
            "type": "campaign_budget",
            "daily_budget_cad": 15,
            "status": "draft_owner_approval_required"
          },
          {
            "type": "exclusion",
            "audience": "unresolved warranty cases"
          }
        ],
        "safety": {
          "owner_approval_required": true,
          "live_connectors": "off",
          "no_api_call": true,
          "no_ad_spend": true,
          "max_daily_budget_cad": 15
        }
      }
    }
  }
];

const fallbackEmailItems = [
  {
    id: "email-001",
    urgency: "red",
    category: "Warranty pressure",
    lane: "Warranty",
    subject: "Warranty follow-up needs service recovery",
    from_label: "Redacted customer thread",
    received: "Today · 08:42 PT",
    status: "needs-owner",
    summary: "Customer is waiting on a warranty response. Hermes prepared a careful evidence/service-recovery draft.",
    source_snippet: "Fixture email with customer identifiers removed.",
    suggested_skill: "warranty-audit",
    draft_reply: "Draft-only evidence request prepared. No email is sent in demo mode.",
    owner_gate: "Phu approves response path before send.",
    business_impact: "Prevents overdue warranty pressure without making promises.",
    proof_assets: ["redacted-warranty-email", "case-thread-history"],
    disabled_actions: ["Send customer email", "Mark thread read", "Book label", "Refund / replace"]
  }
];

const fallbackAgentPulse = {
  fixture_only: true,
  live_connectors: false,
  safety: ["LIVE CONNECTORS OFF", "NO EMAIL SENT", "NO WOO UPDATE", "NO LABEL BOOKED", "NO TRADES", "OWNER APPROVAL REQUIRED"],
  summary: { cron_health: "needs-tuning", quiet_watchdogs: 8, approval_required: 3, stale_market_theses: 5, next_command_brief: "07:30 PT" },
  recommended_schedule: [
    { id: "daily-command-brief", name: "Daily Command Brief", cadence: "07:30 PT daily", status: "proposed", owner_value: "One cockpit for email, ops, cron failures, stale market theses, and the first ugly action.", safety_gate: "Read-only summary; external actions remain draft-only." }
  ],
  tuning_recommendations: [],
  audit_events: []
};

const state = {
  queue: [],
  audit: [],
  warrantyCases: [],
  paymentRequests: [],
  emailItems: [],
  agentPulse: fallbackAgentPulse,
  selectedId: null,
  selectedWarrantyId: null,
  selectedPaymentId: null,
  selectedEmailId: null,
  lane: "All",
  currentTab: "Overview",
  usingApi: false,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

const prefersReducedMotion =
  window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Animated count-up; no-ops to a direct set when motion is reduced or value is unchanged.
function setNum(el, target) {
  if (!el) return;
  const suffix = el.dataset.suffix || "";
  const current = parseInt(el.textContent, 10) || 0;
  if (prefersReducedMotion || current === target) {
    el.textContent = `${target}${suffix}`;
    return;
  }
  const from = current;
  const start = performance.now();
  const duration = 600;
  const step = (now) => {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = `${Math.round(from + (target - from) * eased)}${suffix}`;
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

// Briefly replay the pop animation on an element (used when an approval state flips).
function flash(el) {
  if (!el || prefersReducedMotion) return;
  el.classList.remove("just-changed");
  void el.offsetWidth; // force reflow so the animation restarts
  el.classList.add("just-changed");
}

const CA = new Intl.NumberFormat("en-CA", { style: "currency", currency: "CAD" });
function parseAmount(label = "") {
  const match = label.replace(/,/g, "").match(/[\d]+(?:\.[\d]+)?/);
  return match ? parseFloat(match[0]) : 0;
}

function laneClass(lane = "") {
  return lane.toLowerCase();
}

function statusLabel(status = "") {
  return status
    .replace(/-/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function nowStamp() {
  const d = new Date();
  return d.toLocaleString([], {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function loadJson(path, fallback) {
  try {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error(`${path} returned ${response.status}`);
    return await response.json();
  } catch (error) {
    console.warn(`Using embedded fallback for ${path}:`, error.message);
    return fallback;
  }
}

// ===== Phase 1: optional local SQLite backend =====
// When the Python backend (control-room-demo/backend/server.py) is serving the
// page, the app reads from /api/* and posts owner decisions to durable SQLite.
// When the page is served by plain `python3 -m http.server`, /api/* is absent,
// detectApi() returns false, and the app keeps its original static behavior.
const API_BASE = "/api";

async function apiGet(path) {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`${API_BASE}${path} -> ${response.status}`);
  return response.json();
}

async function detectApi() {
  try {
    const health = await apiGet("/health");
    return !!(health && health.ok === true);
  } catch {
    return false;
  }
}

// Prefer the backend route; fall back to the static JSON file, then embedded data.
async function loadData(apiPath, staticPath, fallback) {
  if (state.usingApi) {
    try {
      return await apiGet(apiPath);
    } catch (error) {
      console.warn(`API ${apiPath} failed, using static fixture:`, error.message);
    }
  }
  return loadJson(staticPath, fallback);
}

function decisionTail(action = "") {
  if (action.startsWith("approved")) return "approve-draft";
  if (action.startsWith("rejected")) return "reject";
  return "hold"; // needs-owner / needs-bench-check
}

async function postDecision(id, tail, action, actor) {
  const response = await fetch(
    `${API_BASE}/approvals/${encodeURIComponent(id)}/${tail}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, actor }),
    }
  );
  if (!response.ok) throw new Error(`approval ${tail} -> ${response.status}`);
  return response.json();
}

// Send an owner decision to the backend, then refresh the durable audit log.
async function applyDecisionApi(item, action, actor, flashSelector) {
  const previous = item.status;
  let result;
  try {
    result = await postDecision(item.id, decisionTail(action), action, actor);
  } catch (error) {
    console.error("Backend decision failed; restoring previous state:", error.message);
    item.status = previous;
    render();
    return;
  }
  item.status = (result.item && result.item.status) || action;
  try {
    state.audit = await apiGet("/audit");
  } catch (error) {
    console.warn("Audit refresh failed; keeping cached audit:", error.message);
  }
  render();
  flash($(flashSelector));
}

// Reflect backend mode in the header without touching disabled live controls.
function markBackendActive() {
  const indicator = document.querySelector(".live-indicator");
  if (indicator && indicator.lastChild) {
    indicator.lastChild.textContent = " SQLite backend · fixtures";
  }
}

// ===== Phase 5: live READ-ONLY badge + redacted samples =====
// Purely additive. Renders ONLY when the backend has live_snapshots rows. With
// zero live rows (the default, and the state of the recorded demo/video) the UI
// is visually unchanged: the fixture demo keeps working exactly as before.
async function loadLiveStatus() {
  if (!state.usingApi) return null;
  try {
    return await apiGet("/live/status");
  } catch (error) {
    console.warn("Live read-only status unavailable:", error.message);
    return null;
  }
}

async function renderLiveReadonly(status) {
  const ingestion = status && status.ingestion;
  const live = status && status.live_readonly;
  const count = ingestion ? ingestion.snapshot_count : 0;
  if (!count) return; // no live rows -> leave the fixture demo untouched

  const byConnector = ingestion.snapshots_by_connector || {};

  // Header badge (inserted once). Reuses the existing .pill styling.
  const right = document.querySelector(".topbar-right");
  if (right && !document.querySelector(".live-readonly-badge")) {
    const badge = document.createElement("span");
    badge.className = "pill live-readonly-badge";
    badge.title =
      "Live connectors are READ-ONLY. Stored data is redacted (raw_stored=0). " +
      "No email/Woo/Stripe mutation is ever taken.";
    badge.textContent = `LIVE READ-ONLY - ${count} redacted`;
    right.insertBefore(badge, right.firstChild);
  }

  // Redacted proof panel, inserted right under the header (created once).
  let strip = document.querySelector("#live-readonly-strip");
  if (!strip) {
    const header = document.querySelector(".topbar");
    strip = document.createElement("section");
    strip.id = "live-readonly-strip";
    strip.className = "live-proof-panel";
    if (header && header.parentNode) {
      header.parentNode.insertBefore(strip, header.nextSibling);
    }
  }

  let snaps = [];
  let runs = [];
  try {
    snaps = await apiGet("/live/snapshots");
    runs = await apiGet("/live/connector-runs");
  } catch (error) {
    console.warn("Live snapshots unavailable:", error.message);
  }

  const safeSnaps = Array.isArray(snaps) ? snaps : [];
  const emailSnaps = safeSnaps.filter((s) => s.connector === "email").slice(0, 3);
  const wooSnaps = safeSnaps.filter((s) => s.connector === "woocommerce").slice(0, 3);
  const recentRuns = (Array.isArray(runs) ? runs : []).slice(0, 2);

  const el = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };

  strip.innerHTML = "";
  const head = el("div", "live-proof-head");
  const copy = el("div");
  copy.append(
    el("span", "card-label", "Live read-only proof"),
    el("h3", "live-proof-title", "Real Toiletland signals, redacted before storage"),
    el("p", "live-proof-sub", "Email and WooCommerce were fetched read-only, transformed into local SQLite snapshots, and stripped of raw customer/order data before display.")
  );
  const stamp = el("span", "pill live-proof-pill", "LOCAL SQLITE - MUTATIONS OFF");
  head.append(copy, stamp);
  strip.appendChild(head);

  const metrics = el("div", "live-proof-metrics");
  [
    [String(count), "redacted snapshots"],
    [String(byConnector.email || 0), "email snapshots"],
    [String(byConnector.woocommerce || 0), "Woo snapshots"],
    ["0", "raw records stored"],
    ["0", "live mutations"]
  ].forEach(([value, label]) => {
    const card = el("div", "live-metric");
    card.append(el("strong", "", value), el("span", "", label));
    metrics.appendChild(card);
  });
  strip.appendChild(metrics);

  const grid = el("div", "live-proof-grid");
  const emailCol = el("section", "live-proof-col");
  emailCol.appendChild(el("h4", "", "Read-only email samples"));
  if (!emailSnaps.length) emailCol.appendChild(el("p", "muted-sm", "No email snapshots available."));
  emailSnaps.forEach((snap) => {
    const r = snap.redacted || {};
    const card = el("article", "live-snapshot-card email-live-card");
    card.append(
      el("strong", "", r.subject || "Email subject redacted"),
      el("span", "", `${r.from_domain || "[redacted]"} - ${r.body_chars || 0} chars sampled`),
      el("p", "", "Body preview withheld for the recording. The snapshot was redacted and stored locally only.")
    );
    emailCol.appendChild(card);
  });

  const wooCol = el("section", "live-proof-col");
  wooCol.appendChild(el("h4", "", "Read-only Woo order signals"));
  if (!wooSnaps.length) wooCol.appendChild(el("p", "muted-sm", "No Woo snapshots available."));
  wooSnaps.forEach((snap) => {
    const r = snap.redacted || {};
    const card = el("article", "live-snapshot-card woo-live-card");
    card.append(
      el("strong", "", `${String(r.status || "status unknown").toUpperCase()} - ${r.currency || "CAD"} ${r.total || "0.00"}`),
      el("span", "", `${r.line_items_count || 0} line item(s) - customer fields removed`),
      el("p", "", `Created ${r.date_created || "[redacted date]"}. No name, email, address, phone, or order id stored.`)
    );
    wooCol.appendChild(card);
  });
  grid.append(emailCol, wooCol);
  strip.appendChild(grid);

  const safety = el("div", "live-proof-safety");
  const methods = live && live.connectors ? live.connectors : {};
  const methodLine = [
    methods.email?.detail?.method || "IMAP EXAMINE + BODY.PEEK",
    methods.woocommerce?.detail?.method || "WooCommerce GET orders"
  ].join(" / ");
  [
    `Runs: ${ingestion.run_count || recentRuns.length} read-only connector run(s)`,
    `Storage: raw_stored=0, redacted_json only`,
    `Network method: ${methodLine}`,
    `Disabled: send, mark-read, move, delete, refund, order edit, Stripe charge, Ads publish`
  ].forEach((line) => safety.appendChild(el("span", "", line)));
  strip.appendChild(safety);
}

function loadLocalState() {
  const saved = localStorage.getItem("hermes-smb-operator-demo");
  if (!saved) return null;
  try {
    return JSON.parse(saved);
  } catch {
    return null;
  }
}

function saveLocalState() {
  localStorage.setItem(
    "hermes-smb-operator-demo",
    JSON.stringify({
      queue: state.queue,
      audit: state.audit,
      warrantyCases: state.warrantyCases,
      paymentRequests: state.paymentRequests,
      emailItems: state.emailItems,
      agentPulse: state.agentPulse,
      selectedId: state.selectedId,
      selectedWarrantyId: state.selectedWarrantyId,
      selectedPaymentId: state.selectedPaymentId,
      selectedEmailId: state.selectedEmailId,
      lane: state.lane,
      currentTab: state.currentTab,
    })
  );
}

function mergeById(baseItems, savedItems = []) {
  if (!savedItems.length) return structuredClone(baseItems);
  return baseItems.map((baseItem) => {
    const savedItem = savedItems.find((entry) => entry.id === baseItem.id) || {};
    return { ...baseItem, status: savedItem.status || baseItem.status };
  });
}

function renderCounts() {
  setNum($("#count-all"), state.queue.length);
  setNum($("#count-earn"), state.queue.filter((item) => item.lane === "Earn").length);
  setNum($("#count-operate"), state.queue.filter((item) => item.lane === "Operate").length);
  setNum($("#count-spend"), state.queue.filter((item) => item.lane === "Spend").length);
  setNum($("#count-warranty"), state.queue.filter((item) => item.lane === "Warranty").length);
  setNum($("#warranty-count"), state.warrantyCases.length);
  setNum($("#payment-count"), state.paymentRequests.length);
  setNum($("#email-count"), state.emailItems.length);
}

// ===== Tier 3: live data viz ("Ops at a glance") =====
const RISK_BUCKETS = [
  { key: "high", label: "High risk", color: "var(--danger)" },
  { key: "medium", label: "Medium", color: "var(--warning)" },
  { key: "low", label: "Low", color: "var(--success)" },
];

function renderOverview() {
  renderLaneLoad();
  renderRiskDonut();
  renderApprovalFunnel();
  renderSpend();
}

function renderLaneLoad() {
  const host = $("#viz-lane-load");
  if (!host) return;
  const lanes = [
    { key: "Earn", icon: "i-earn", cls: "earn" },
    { key: "Operate", icon: "i-operate", cls: "operate" },
    { key: "Spend", icon: "i-spend", cls: "spend" },
    { key: "Warranty", icon: "i-warranty", cls: "warranty" },
  ];
  const counts = lanes.map((l) => state.queue.filter((i) => i.lane === l.key).length);
  const max = Math.max(1, ...counts);
  host.innerHTML = lanes
    .map(
      (l, idx) => `
      <div class="viz-bar-row">
        <div class="viz-bar-head">
          <span class="viz-bar-label">
            <span class="ico-chip chip-ico ${l.cls}"><svg class="icon"><use href="#${l.icon}"/></svg></span>${l.key}
          </span>
          <span class="viz-bar-val">${counts[idx]}</span>
        </div>
        <div class="viz-track"><span class="viz-track-fill" style="width:${(counts[idx] / max) * 100}%"></span></div>
      </div>`
    )
    .join("");
}

function riskCounts() {
  const tally = { high: 0, medium: 0, low: 0 };
  const bump = (level) => {
    if (level && tally[level] !== undefined) tally[level] += 1;
  };
  state.queue.forEach((i) => bump(i.risk));
  state.warrantyCases.forEach((i) => bump(i.severity));
  state.paymentRequests.forEach((i) => bump(i.risk));
  state.emailItems.forEach((i) => bump(emailRisk(i.urgency)));
  return tally;
}

function renderRiskDonut() {
  const host = $("#viz-risk");
  const legend = $("#viz-risk-legend");
  if (!host || !legend) return;

  const counts = riskCounts();
  const total = RISK_BUCKETS.reduce((sum, b) => sum + counts[b.key], 0) || 1;
  const C = 2 * Math.PI * 42;
  let offset = 0;
  const segments = RISK_BUCKETS.filter((b) => counts[b.key] > 0)
    .map((b) => {
      const dash = (counts[b.key] / total) * C;
      const seg = `<circle class="donut-seg" cx="52" cy="52" r="42" fill="none" stroke="${b.color}" stroke-width="15" stroke-dasharray="${dash.toFixed(2)} ${(C - dash).toFixed(2)}" stroke-dashoffset="${(-offset).toFixed(2)}"/>`;
      offset += dash;
      return seg;
    })
    .join("");

  host.innerHTML = `
    <svg viewBox="0 0 104 104">
      <circle cx="52" cy="52" r="42" fill="none" stroke="#eef2f7" stroke-width="15"/>
      ${segments}
      <text x="52" y="49" transform="rotate(90 52 52)" text-anchor="middle" fill="var(--text)" font-family="var(--mono)" font-size="21" font-weight="600">${total}</text>
      <text x="52" y="64" transform="rotate(90 52 52)" text-anchor="middle" fill="var(--muted)" font-size="9" letter-spacing="1">ITEMS</text>
    </svg>`;

  legend.innerHTML = RISK_BUCKETS.map(
    (b) => `<li><span class="dot" style="background:${b.color}"></span>${b.label} <strong>${counts[b.key]}</strong></li>`
  ).join("");
}

function renderApprovalFunnel() {
  const host = $("#viz-approvals");
  if (!host) return;
  const statuses = [
    ...state.queue.map((i) => i.status),
    ...state.warrantyCases.map((i) => i.status),
    ...state.paymentRequests.map((i) => i.status),
    ...state.emailItems.map((i) => i.status),
  ];
  const cats = [
    { label: "Needs owner", color: "var(--warning)", test: (s) => /needs-owner|needs-bench/.test(s) },
    { label: "Blocked", color: "var(--danger)", test: (s) => s.includes("blocked") },
    { label: "Ready / quote", color: "var(--brand)", test: (s) => s.includes("ready") || s.includes("quote") },
    { label: "Decided", color: "var(--success)", test: (s) => s.includes("approved") || s.includes("rejected") },
  ];
  const total = Math.max(1, statuses.length);
  host.innerHTML = cats
    .map((c) => {
      const n = statuses.filter((s) => c.test(s || "")).length;
      return `
      <div class="viz-bar-row">
        <div class="viz-bar-head">
          <span class="viz-bar-label">${c.label}</span>
          <span class="viz-bar-val">${n}</span>
        </div>
        <div class="viz-track"><span class="viz-track-fill" style="width:${(n / total) * 100}%;background:${c.color}"></span></div>
      </div>`;
    })
    .join("");
}

function renderSpend() {
  const amountEl = $("#viz-spend-amount");
  const barEl = $("#viz-spend-bar");
  const subEl = $("#viz-spend-sub");
  if (!amountEl) return;
  const total = state.paymentRequests.reduce((sum, p) => sum + parseAmount(p.amount_label), 0);
  const gated = state.paymentRequests.filter((p) => /needs|blocked|quote/.test(p.status)).length;
  const n = state.paymentRequests.length || 1;
  amountEl.textContent = CA.format(total);
  if (barEl) barEl.style.width = `${(gated / n) * 100}%`;
  if (subEl) {
    subEl.textContent = `${gated} of ${state.paymentRequests.length} rails owner-gated · CA$0 charged · 0 links created`;
  }
}

function renderQueue() {
  const container = $("#queue-list");
  const template = $("#queue-card-template");
  container.innerHTML = "";

  const visible = state.lane === "All" ? state.queue : state.queue.filter((item) => item.lane === state.lane);

  visible.forEach((item, index) => {
    const node = template.content.firstElementChild.cloneNode(true);
    node.dataset.id = item.id;
    node.style.setProperty("--i", index);
    node.classList.toggle("active", item.id === state.selectedId);

    const laneBadge = node.querySelector(".lane-badge");
    laneBadge.textContent = item.lane;
    laneBadge.classList.add(laneClass(item.lane));

    node.querySelector(".status-badge").textContent = statusLabel(item.status);
    node.querySelector(".card-title").textContent = item.title;
    node.querySelector(".card-summary").textContent = item.summary;
    node.querySelector(".card-impact").textContent = item.business_impact || "Keeps owner control visible before action.";
    node.querySelector(".card-meta").textContent = `${item.source_type} • ${item.risk} risk • ${item.approval_required === false ? "demo only" : "owner approval"}`;

    node.addEventListener("click", () => {
      state.selectedId = item.id;
      saveLocalState();
      render();
      if (item.lane === "Warranty") switchTab("Warranty");
      else if (item.lane === "Spend") switchTab("Payments");
    });
    container.appendChild(node);
  });
}

function renderDetail() {
  const item = state.queue.find((entry) => entry.id === state.selectedId) || state.queue[0];
  if (!item) return;
  state.selectedId = item.id;

  $("#detail-empty").classList.add("hidden");
  $("#detail-card").classList.remove("hidden");

  const laneBadge = $("#detail-lane");
  laneBadge.textContent = item.lane;
  laneBadge.className = `lane-badge ${laneClass(item.lane)}`;

  const riskBadge = $("#detail-risk");
  riskBadge.textContent = `${item.risk} risk`;
  riskBadge.className = `risk-badge ${item.risk}`;

  $("#detail-title").textContent = item.title;
  $("#detail-summary").textContent = item.summary;
  $("#detail-source").textContent = item.source;
  $("#detail-action").textContent = item.recommended_action;
  $("#approval-state").textContent = statusLabel(item.status);

  const proofAssets = $("#detail-proof-assets");
  proofAssets.innerHTML = "";
  (item.proof_assets || []).forEach((asset) => proofAssets.appendChild(chip(asset)));

  const reasoning = $("#detail-reasoning");
  reasoning.innerHTML = "";
  (item.reasoning || []).forEach((line) => {
    const li = document.createElement("li");
    li.textContent = line;
    reasoning.appendChild(li);
  });
}

function chip(text) {
  const span = document.createElement("span");
  span.className = "proof-chip";
  span.textContent = text;
  return span;
}

function renderWarrantyCases() {
  const container = $("#warranty-case-list");
  const template = $("#warranty-case-template");
  container.innerHTML = "";

  state.warrantyCases.forEach((item, index) => {
    const node = template.content.firstElementChild.cloneNode(true);
    node.dataset.id = item.id;
    node.style.setProperty("--i", index);
    node.classList.toggle("active", item.id === state.selectedWarrantyId);
    node.querySelector(".warranty-brand").textContent = `${item.brand} · ${item.model_family}`;
    node.querySelector(".status-badge").textContent = statusLabel(item.status);
    node.querySelector(".card-title").textContent = item.title;
    node.querySelector(".card-summary").textContent = item.symptom;
    node.querySelector(".card-impact").textContent = item.next_gate;
    node.addEventListener("click", () => {
      state.selectedWarrantyId = item.id;
      saveLocalState();
      render();
    });
    container.appendChild(node);
  });
}

function renderWarrantyDetail() {
  const item = state.warrantyCases.find((entry) => entry.id === state.selectedWarrantyId) || state.warrantyCases[0];
  if (!item) return;
  state.selectedWarrantyId = item.id;

  $("#warranty-detail-brand").textContent = `${item.brand} · ${item.model_family}`;
  $("#warranty-detail-severity").textContent = `${item.severity} risk`;
  $("#warranty-detail-severity").className = `risk-badge ${item.severity}`;
  $("#warranty-detail-title").textContent = item.title;
  $("#warranty-detail-symptom").textContent = item.symptom;
  $("#warranty-next-gate").textContent = item.next_gate;
  $("#warranty-customer-state").textContent = item.customer_state;
  $("#warranty-approval-state").textContent = statusLabel(item.status);
  $("#warranty-approval-copy").textContent = `${item.approval_copy}. ${item.audit_note}`;

  renderList("#warranty-repair-path", item.repair_path || []);
  renderChips("#warranty-parts", item.parts || []);
  renderChips("#warranty-proof-assets", item.proof_assets || []);
  renderList("#warranty-timeline", item.timeline || []);
}

function renderChips(selector, values) {
  const container = $(selector);
  container.innerHTML = "";
  values.forEach((value) => container.appendChild(chip(value)));
}

function renderList(selector, values) {
  const container = $(selector);
  container.innerHTML = "";
  values.forEach((value) => {
    const li = document.createElement("li");
    li.textContent = value;
    container.appendChild(li);
  });
}

function renderStripeSkill(skill = {}) {
  const panel = $("#stripe-skill-panel");
  if (!panel) return;
  const hasSkill = skill && Object.keys(skill).length;
  panel.hidden = !hasSkill;
  if (!hasSkill) return;

  $("#stripe-skill-name").textContent = skill.skill || "Stripe Skill draft";
  $("#stripe-skill-mode").textContent = skill.mode || "test_fixture_no_api_call";
  $("#stripe-skill-call").textContent = skill.proposed_call || "draft only";
  $("#stripe-skill-idempotency").textContent = skill.idempotency_key || "owner-approval-required";
  $("#stripe-skill-amount").textContent = `${(skill.currency || "cad").toUpperCase()} ${((skill.amount_cents || 0) / 100).toFixed(2)}`;
  $("#stripe-skill-payload").textContent = JSON.stringify(skill.payload || {}, null, 2);
}

function renderGrowthLoop(loop = {}) {
  const panel = $("#growth-loop-panel");
  if (!panel) return;
  const hasLoop = loop && Object.keys(loop).length;
  panel.hidden = !hasLoop;
  if (!hasLoop) return;

  const payload = loop.payload || {};
  const safety = payload.safety || {};
  const conversionSource = payload.conversion_source || "fixture conversion signal";
  $("#growth-loop-label").textContent = loop.label || "Stripe → Google Ads dry-run";
  $("#growth-loop-mode").textContent = loop.mode || "test_fixture_no_api_call";
  $("#growth-loop-call").textContent = loop.proposed_call || "draft only";
  $("#growth-loop-signal").textContent = loop.signal || "Stripe signal becomes a growth draft.";
  $("#growth-loop-action").textContent = loop.proposed_action || "Draft growth action only.";
  $("#growth-loop-budget").textContent = loop.budget_label || "CA$0 live spend";
  $("#growth-loop-roas").textContent = loop.roas_guardrail || "Owner approval required before publishing.";
  $("#growth-loop-payload").textContent = JSON.stringify(payload, null, 2);

  const stepSignal = $("#growth-step-signal");
  const stepBudget = $("#growth-step-budget");
  const stepGate = $("#growth-step-gate");
  const stepSafety = $("#growth-step-safety");
  if (stepSignal) stepSignal.textContent = conversionSource;
  if (stepBudget) stepBudget.textContent = loop.budget_label || "CA$0 live spend";
  if (stepGate) stepGate.textContent = safety.no_ad_spend ? "Publish blocked" : "Owner approval required";
  if (stepSafety) stepSafety.textContent = safety.no_api_call ? "No API call · no ad spend" : "Fixture-only owner gate";
}

function renderPaymentRequests() {
  const container = $("#payment-request-list");
  container.innerHTML = "";

  state.paymentRequests.forEach((item, index) => {
    const node = document.createElement("button");
    node.className = "payment-request-card";
    node.dataset.id = item.id;
    node.style.setProperty("--i", index);
    node.classList.toggle("active", item.id === state.selectedPaymentId);

    const topline = document.createElement("span");
    topline.className = "queue-card-topline";
    const kind = document.createElement("span");
    kind.className = "warranty-brand";
    kind.textContent = item.kind;
    const status = document.createElement("span");
    status.className = "status-badge";
    status.textContent = statusLabel(item.status);
    topline.append(kind, status);

    const title = document.createElement("strong");
    title.className = "card-title";
    title.textContent = item.title;
    const summary = document.createElement("span");
    summary.className = "card-summary";
    summary.textContent = `${item.amount_label} · ${item.processor}`;
    const impact = document.createElement("span");
    impact.className = "card-impact";
    impact.textContent = item.reason;

    node.append(topline, title, summary, impact);
    node.addEventListener("click", () => {
      state.selectedPaymentId = item.id;
      saveLocalState();
      render();
    });
    container.appendChild(node);
  });
}

function renderPaymentDetail() {
  const item = state.paymentRequests.find((entry) => entry.id === state.selectedPaymentId) || state.paymentRequests[0];
  if (!item) return;
  state.selectedPaymentId = item.id;

  $("#payment-detail-kind").textContent = item.kind;
  $("#payment-detail-risk").textContent = `${item.risk} risk`;
  $("#payment-detail-risk").className = `risk-badge ${item.risk}`;
  $("#payment-detail-title").textContent = item.title;
  $("#payment-detail-amount").textContent = item.amount_label;
  $("#payment-detail-state").textContent = item.customer_or_vendor_state;
  $("#payment-detail-reason").textContent = item.reason;
  $("#payment-detail-processor").textContent = item.processor;
  renderStripeSkill(item.stripe_skill);
  renderGrowthLoop(item.growth_loop);
  $("#payment-approval-state").textContent = statusLabel(item.status);
  $("#payment-approval-copy").textContent = `${item.approval_copy}. ${item.audit_note}`;

  renderList("#payment-line-items", item.line_items || []);
  renderList("#payment-guardrails", item.guardrails || []);
  renderChips("#payment-proof-assets", item.proof_assets || []);

  const disabledActions = $("#payment-disabled-actions");
  disabledActions.innerHTML = "";
  (item.disabled_actions || []).forEach((label) => {
    const button = document.createElement("button");
    button.disabled = true;
    button.textContent = label;
    disabledActions.appendChild(button);
  });
}


function renderEmailMessages() {
  const container = $("#email-message-list");
  if (!container) return;
  container.innerHTML = "";

  state.emailItems.forEach((item, index) => {
    const node = document.createElement("button");
    node.className = "email-message-card";
    node.dataset.id = item.id;
    node.style.setProperty("--i", index);
    node.classList.toggle("active", item.id === state.selectedEmailId);

    const topline = document.createElement("span");
    topline.className = "queue-card-topline";
    const from = document.createElement("span");
    from.className = "email-from";
    from.textContent = item.from_label;
    const urgency = document.createElement("span");
    urgency.className = `email-urgency ${item.urgency}`;
    urgency.textContent = item.urgency;
    topline.append(from, urgency);

    const title = document.createElement("strong");
    title.className = "card-title";
    title.textContent = item.subject;
    const summary = document.createElement("span");
    summary.className = "card-summary";
    summary.textContent = `${item.category} · ${item.received}`;
    const impact = document.createElement("span");
    impact.className = "card-impact";
    impact.textContent = item.business_impact;

    node.append(topline, title, summary, impact);
    node.addEventListener("click", () => {
      state.selectedEmailId = item.id;
      saveLocalState();
      render();
    });
    container.appendChild(node);
  });
}

function renderEmailDetail() {
  const item = state.emailItems.find((entry) => entry.id === state.selectedEmailId) || state.emailItems[0];
  if (!item) return;
  state.selectedEmailId = item.id;

  $("#email-detail-category").textContent = `${item.category} · ${item.lane}`;
  $("#email-detail-urgency").textContent = `${item.urgency} email`;
  $("#email-detail-urgency").className = `risk-badge ${emailRisk(item.urgency)}`;
  $("#email-detail-subject").textContent = item.subject;
  $("#email-detail-summary").textContent = item.summary;
  $("#email-source-snippet").textContent = item.source_snippet;
  $("#email-suggested-skill").textContent = item.suggested_skill;
  $("#email-draft-reply").textContent = item.draft_reply;
  $("#email-owner-gate").textContent = item.owner_gate;
  $("#email-approval-state").textContent = statusLabel(item.status);
  renderChips("#email-proof-assets", item.proof_assets || []);

  const disabledActions = $("#email-disabled-actions");
  disabledActions.innerHTML = "";
  (item.disabled_actions || []).forEach((label) => {
    const button = document.createElement("button");
    button.disabled = true;
    button.textContent = label;
    disabledActions.appendChild(button);
  });
}

function renderAgentPulse() {
  const pulse = state.agentPulse || fallbackAgentPulse;
  const summary = pulse.summary || {};
  if ($("#pulse-next-brief")) $("#pulse-next-brief").textContent = summary.next_command_brief || "—";
  setNum($("#pulse-watchdogs"), summary.quiet_watchdogs || 0);
  setNum($("#pulse-approvals"), summary.approval_required || 0);
  setNum($("#pulse-stale"), summary.stale_market_theses || 0);

  const schedule = $("#pulse-schedule");
  if (schedule) {
    schedule.innerHTML = "";
    (pulse.recommended_schedule || []).slice(0, 4).forEach((item) => {
      const card = document.createElement("div");
      card.className = "pulse-card";
      const status = document.createElement("code");
      status.textContent = `${item.status} · ${item.cadence}`;
      const title = document.createElement("strong");
      title.textContent = item.name;
      const value = document.createElement("span");
      value.textContent = item.owner_value;
      const safety = document.createElement("span");
      safety.textContent = item.safety_gate;
      card.append(status, title, value, safety);
      schedule.appendChild(card);
    });
  }

  const safety = $("#pulse-safety");
  if (safety) {
    safety.innerHTML = "";
    (pulse.safety || []).forEach((rail) => {
      const span = document.createElement("span");
      span.textContent = rail;
      safety.appendChild(span);
    });
  }
}

function renderAudit() {
  const container = $("#audit-log");
  container.innerHTML = "";
  state.audit.slice().reverse().forEach((row, index) => {
    const div = document.createElement("div");
    div.className = `audit-row ${outcomeClass(row.outcome)}${index === 0 ? " newest" : ""}`;
    div.style.setProperty("--i", Math.min(index, 8));

    const at = document.createElement("code");
    at.textContent = row.at;
    const actor = document.createElement("strong");
    actor.textContent = row.actor;
    const event = document.createElement("span");
    event.textContent = row.event;
    const outcome = document.createElement("span");
    outcome.className = "au-out";
    outcome.textContent = `${row.item_id} · ${statusLabel(row.outcome)}`;

    div.append(at, actor, event, outcome);
    container.appendChild(div);
  });
}

function outcomeClass(outcome = "") {
  if (outcome.includes("approved") || outcome.includes("ready")) return "outcome-good";
  if (outcome.includes("blocked") || outcome.includes("needs") || outcome.includes("bench")) return "outcome-warn";
  if (outcome.includes("reject")) return "outcome-bad";
  return "outcome-neutral";
}

function renderLaneFilters() {
  $$(".chip[data-lane]").forEach((button) => {
    button.classList.toggle("active", button.dataset.lane === state.lane);
  });
}

// ===== Tabs =====
const TABS = ["Overview", "Email", "Triage", "Warranty", "Payments", "Audit"];

function switchTab(name, { save = true } = {}) {
  if (!TABS.includes(name)) name = "Overview";
  state.currentTab = name;
  $$(".tab").forEach((tab) => {
    const on = tab.dataset.tab === name;
    tab.classList.toggle("active", on);
    tab.setAttribute("aria-selected", on ? "true" : "false");
  });
  $$(".tab-panel").forEach((panel) => {
    panel.hidden = panel.dataset.panel !== name;
  });
  if (location.hash.slice(1) !== name) {
    history.replaceState(null, "", `#${name}`);
  }
  if (save) saveLocalState();
}

function renderTabCounts() {
  setNum($("#tab-count-email"), state.emailItems.length);
  setNum($("#tab-count-triage"), state.queue.length);
  setNum($("#tab-count-warranty"), state.warrantyCases.length);
  setNum($("#tab-count-payments"), state.paymentRequests.length);
}

function renderKpiStrip() {
  const total = state.paymentRequests.reduce((sum, p) => sum + parseAmount(p.amount_label), 0);
  const spendEl = $("#kpi-spend");
  if (spendEl) spendEl.textContent = CA.format(total);
  // charged / owner-gated / live-actions are constant in demo (all gated, nothing fired)
}

// ===== Overview: cross-lane "needs your attention" =====
const LANE_META = {
  Earn: { icon: "i-earn", cls: "earn" },
  Operate: { icon: "i-operate", cls: "operate" },
  Spend: { icon: "i-spend", cls: "spend" },
  Warranty: { icon: "i-warranty", cls: "warranty" },
  Email: { icon: "i-inbox", cls: "email" },
};
const RISK_ORDER = { high: 0, red: 0, medium: 1, yellow: 1, low: 2, green: 2 };

function emailRisk(urgency = "") {
  if (urgency === "red") return "high";
  if (urgency === "yellow") return "medium";
  return "low";
}

function needsOwner(status = "") {
  return /needs-owner|needs-bench|blocked|quote/.test(status);
}

function renderNeedsAttention() {
  const host = $("#needs-attention");
  if (!host) return;

  const items = [];
  state.queue.forEach((i) => {
    if (needsOwner(i.status)) {
      const tab = i.lane === "Spend" ? "Payments" : i.lane === "Warranty" ? "Warranty" : "Triage";
      items.push({ id: i.id, tab, lane: i.lane, title: i.title, risk: i.risk });
    }
  });
  state.warrantyCases.forEach((i) => {
    if (needsOwner(i.status)) items.push({ id: i.id, tab: "Warranty", lane: "Warranty", title: i.title, risk: i.severity });
  });
  state.paymentRequests.forEach((i) => {
    if (needsOwner(i.status)) items.push({ id: i.id, tab: "Payments", lane: "Spend", title: i.title, risk: i.risk });
  });
  state.emailItems.forEach((i) => {
    if (i.urgency !== "green" || needsOwner(i.status)) items.push({ id: i.id, tab: "Email", lane: "Email", title: i.subject, risk: i.urgency });
  });
  items.sort((a, b) => (RISK_ORDER[a.risk] ?? 3) - (RISK_ORDER[b.risk] ?? 3));

  if (!items.length) {
    host.innerHTML = `<div class="attention-empty">All clear. Nothing is waiting on Phu right now.</div>`;
    return;
  }

  host.innerHTML = "";
  items.slice(0, 6).forEach((it) => {
    const meta = LANE_META[it.lane] || LANE_META.Earn;
    const row = document.createElement("button");
    row.className = "attention-row";
    row.innerHTML = `
      <span class="ar-ico chip-ico ${meta.cls}"><svg class="icon"><use href="#${meta.icon}"/></svg></span>
      <span class="ar-body">
        <span class="ar-title"></span>
        <span class="ar-meta">${it.lane} · ${it.risk} risk · needs owner</span>
      </span>
      <span class="ar-go"><svg class="icon"><use href="#i-arrow-right"/></svg></span>`;
    row.querySelector(".ar-title").textContent = it.title;
    row.addEventListener("click", () => {
      if (it.tab === "Warranty") state.selectedWarrantyId = it.id;
      else if (it.tab === "Payments") state.selectedPaymentId = it.id;
      else if (it.tab === "Email") state.selectedEmailId = it.id;
      else state.selectedId = it.id;
      saveLocalState();
      render();
      switchTab(it.tab);
      window.scrollTo({ top: 0, behavior: prefersReducedMotion ? "auto" : "smooth" });
    });
    host.appendChild(row);
  });
}

function render() {
  renderCounts();
  renderKpiStrip();
  renderTabCounts();
  renderOverview();
  renderNeedsAttention();
  renderAgentPulse();
  renderLaneFilters();
  renderQueue();
  renderDetail();
  renderWarrantyCases();
  renderWarrantyDetail();
  renderPaymentRequests();
  renderPaymentDetail();
  renderEmailMessages();
  renderEmailDetail();
  renderAudit();
}

function setApproval(action) {
  const item = state.queue.find((entry) => entry.id === state.selectedId);
  if (!item) return;
  if (state.usingApi) return void applyDecisionApi(item, action, "Phu demo click", "#approval-state");
  item.status = action;
  state.audit.push({
    at: nowStamp(),
    actor: "Phu demo click",
    item_id: item.id,
    event: `Local-only approval state changed to ${statusLabel(action)}`,
    outcome: action,
  });
  saveLocalState();
  render();
  flash($("#approval-state"));
}

function setWarrantyApproval(action) {
  const item = state.warrantyCases.find((entry) => entry.id === state.selectedWarrantyId);
  if (!item) return;
  if (state.usingApi) return void applyDecisionApi(item, action, "Phu warranty demo click", "#warranty-approval-state");
  item.status = action;
  state.audit.push({
    at: nowStamp(),
    actor: "Phu warranty demo click",
    item_id: item.id,
    event: `Warranty Command Center state changed locally to ${statusLabel(action)}`,
    outcome: action,
  });
  saveLocalState();
  render();
  flash($("#warranty-approval-state"));
}

function setPaymentApproval(action) {
  const item = state.paymentRequests.find((entry) => entry.id === state.selectedPaymentId);
  if (!item) return;
  if (state.usingApi) return void applyDecisionApi(item, action, "Phu payment demo click", "#payment-approval-state");
  item.status = action;
  state.audit.push({
    at: nowStamp(),
    actor: "Phu payment demo click",
    item_id: item.id,
    event: `Stripe payment/parts approval rail changed locally to ${statusLabel(action)} — no live Stripe or payment API called`,
    outcome: action,
  });
  saveLocalState();
  render();
  flash($("#payment-approval-state"));
}


function setEmailApproval(action) {
  const item = state.emailItems.find((entry) => entry.id === state.selectedEmailId);
  if (!item) return;
  if (state.usingApi) return void applyDecisionApi(item, action, "Phu email demo click", "#email-approval-state");
  item.status = action;
  state.audit.push({
    at: nowStamp(),
    actor: "Phu email demo click",
    item_id: item.id,
    event: `Email Command Center changed locally to ${statusLabel(action)} — no email sent or marked read`,
    outcome: action,
  });
  saveLocalState();
  render();
  flash($("#email-approval-state"));
}

// In backend mode, "Reset demo" refreshes from SQLite rather than wiping the
// durable audit store. In static mode it restores the original fixtures locally.
async function reloadFromBackend() {
  try {
    state.queue = await apiGet("/queues");
    state.warrantyCases = await apiGet("/warranty-cases");
    state.paymentRequests = await apiGet("/payment-requests");
    state.emailItems = await apiGet("/emails");
    state.agentPulse = await apiGet("/agent-pulse");
    state.audit = await apiGet("/audit");
    render();
  } catch (error) {
    console.warn("Reload from backend failed:", error.message);
  }
}

function resetDemo(baseQueue, baseAudit, baseWarrantyCases, basePaymentRequests, baseEmailItems, baseAgentPulse) {
  if (state.usingApi) return void reloadFromBackend();
  localStorage.removeItem("hermes-smb-operator-demo");
  state.queue = structuredClone(baseQueue);
  state.audit = structuredClone(baseAudit);
  state.warrantyCases = structuredClone(baseWarrantyCases);
  state.paymentRequests = structuredClone(basePaymentRequests);
  state.emailItems = structuredClone(baseEmailItems);
  state.agentPulse = structuredClone(baseAgentPulse);
  state.selectedId = state.queue[0]?.id || null;
  state.selectedWarrantyId = state.warrantyCases[0]?.id || null;
  state.selectedPaymentId = state.paymentRequests[0]?.id || null;
  state.selectedEmailId = state.emailItems[0]?.id || null;
  state.lane = "All";
  saveLocalState();
  render();
}

async function init() {
  // Phase 1: prefer the local SQLite backend when present; otherwise the static
  // JSON fixtures keep working exactly as before (python3 -m http.server).
  state.usingApi = await detectApi();

  const baseQueue = await loadData("/queues", "data/queue-items.json", fallbackQueue);
  const baseAudit = await loadData("/audit", "data/audit-log.json", fallbackAudit);
  const baseWarrantyCases = await loadData("/warranty-cases", "data/warranty-cases.json", fallbackWarrantyCases);
  const basePaymentRequests = await loadData("/payment-requests", "data/payment-requests.json", fallbackPaymentRequests);
  const baseEmailItems = await loadData("/emails", "data/email-command-center.json", fallbackEmailItems);
  const baseAgentPulse = await loadData("/agent-pulse", "data/agent-ops-cron-fixture.json", fallbackAgentPulse);
  const saved = loadLocalState();

  if (state.usingApi) {
    // Backend SQLite is the source of truth for item status and the audit log.
    state.queue = structuredClone(baseQueue);
    state.audit = structuredClone(baseAudit);
    state.warrantyCases = structuredClone(baseWarrantyCases);
    state.paymentRequests = structuredClone(basePaymentRequests);
    state.emailItems = structuredClone(baseEmailItems);
    markBackendActive();
  } else {
    // Static demo: browser-local approvals merged over the fixtures (unchanged).
    state.queue = mergeById(baseQueue, saved?.queue || []);
    state.audit = saved?.audit ? structuredClone(saved.audit) : structuredClone(baseAudit);
    const requiredAuditRows = baseAudit.filter((row) => ["warranty-command-center", "payment-approval-rail", "stripe-google-ads-growth-loop"].includes(row.item_id));
    requiredAuditRows.forEach((row) => {
      if (!state.audit.some((entry) => entry.item_id === row.item_id && entry.event === row.event)) {
        state.audit.push(structuredClone(row));
      }
    });
    state.warrantyCases = mergeById(baseWarrantyCases, saved?.warrantyCases || []);
    state.paymentRequests = mergeById(basePaymentRequests, saved?.paymentRequests || []);
    state.emailItems = mergeById(baseEmailItems, saved?.emailItems || []);
  }
  state.agentPulse = structuredClone(baseAgentPulse);
  state.selectedId = state.queue.some((item) => item.id === saved?.selectedId) ? saved.selectedId : state.queue[0]?.id || null;
  state.selectedWarrantyId = state.warrantyCases.some((item) => item.id === saved?.selectedWarrantyId)
    ? saved.selectedWarrantyId
    : state.warrantyCases[0]?.id || null;
  state.selectedPaymentId = state.paymentRequests.some((item) => item.id === saved?.selectedPaymentId)
    ? saved.selectedPaymentId
    : state.paymentRequests[0]?.id || null;
  state.selectedEmailId = state.emailItems.some((item) => item.id === saved?.selectedEmailId)
    ? saved.selectedEmailId
    : state.emailItems[0]?.id || null;
  state.lane = ["All", "Earn", "Operate", "Spend", "Warranty"].includes(saved?.lane) ? saved.lane : "All";
  state.currentTab = TABS.includes(saved?.currentTab) ? saved.currentTab : "Overview";

  $$(".chip[data-lane]").forEach((button) => {
    button.addEventListener("click", () => {
      state.lane = button.dataset.lane;
      const visible = state.lane === "All" ? state.queue : state.queue.filter((item) => item.lane === state.lane);
      state.selectedId = visible[0]?.id || state.queue[0]?.id || null;
      saveLocalState();
      render();
    });
  });

  $$(".approval-buttons button[data-action]").forEach((button) => {
    button.addEventListener("click", () => setApproval(button.dataset.action));
  });

  $$(".approval-buttons button[data-warranty-action]").forEach((button) => {
    button.addEventListener("click", () => setWarrantyApproval(button.dataset.warrantyAction));
  });

  $$(".approval-buttons button[data-payment-action]").forEach((button) => {
    button.addEventListener("click", () => setPaymentApproval(button.dataset.paymentAction));
  });

  $$(".approval-buttons button[data-email-action]").forEach((button) => {
    button.addEventListener("click", () => setEmailApproval(button.dataset.emailAction));
  });

  $("#reset-demo").addEventListener("click", () => resetDemo(baseQueue, baseAudit, baseWarrantyCases, basePaymentRequests, baseEmailItems, baseAgentPulse));

  $$(".tab").forEach((tab) => {
    tab.addEventListener("click", () => switchTab(tab.dataset.tab));
  });
  window.addEventListener("hashchange", () => switchTab(location.hash.slice(1) || "Overview"));

  $("#run-triage").addEventListener("click", () => {
    switchTab("Triage");
    render();
  });

  const initialTab = TABS.includes(location.hash.slice(1)) ? location.hash.slice(1) : state.currentTab;
  render();
  switchTab(initialTab, { save: false });

  // Phase 5: additive live read-only badge/samples. Non-blocking; if the live
  // endpoint is absent or empty, the fixture demo is unchanged.
  loadLiveStatus().then(renderLiveReadonly).catch((error) => {
    console.warn("Live read-only render skipped:", error.message);
  });
}

init();
