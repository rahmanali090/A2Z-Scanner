A2Z SCANNER

SECTIONS 65–85 — MISSING RULES ADDENDUM

Purpose:
Sections 63–64 ke existing A2Z framework ko strengthen karna, especially signal lifecycle, anti-hindsight protection, data integrity, AI guardrails, risk/reward validation, system health, recovery, security aur complete auditability.

Operating Mode:
Alert-only / Paper-analysis by default.

Important:
Ye sections infrastructure aur validation rules define karte hain. Original A2Z signal-detection rules from Sections 1–62 ko invent nahi kiya jana chahiye.

---

SECTION 65 — SIGNAL LIFECYCLE & STATE MACHINE

Every detected setup must have an explicit state.

Allowed states

"DETECTED → DEVELOPING → CANDIDATE → CONFIRMED → MONITORING → UPGRADED/DOWNGRADED → INVALIDATED/EXPIRED"

Rules

1. Every state transition must be event-driven and timestamped.
2. A signal must not jump directly from "DETECTED" to "EXECUTE".
3. "CONFIRMED" means configured confirmation conditions were satisfied using information available at that decision time.
4. "INVALIDATED" overrides an earlier confirmation for current validity.
5. "EXPIRED" means the signal validity window ended without a valid continuation.
6. Every transition must store:
   - reason
   - triggering fields
   - source timestamps
   - data freshness
   - configuration version
7. A later state must never rewrite an earlier state.
8. State history must remain immutable.

---

SECTION 66 — CONFIDENCE IS NOT CERTAINTY

1. "CONFIDENCE" is an analytical score, not automatically a probability of profit.
2. The system must never display:
   "95% confidence = 95% chance of profit"
   unless that probability has been independently calibrated and explicitly defined.
3. Every confidence result must include:
   - supporting factors
   - weakening factors
   - missing data
   - conflicts
   - freshness issues
4. Confidence may increase only because of information that existed before the evaluation timestamp.
5. Later market movement must never retroactively increase confidence.
6. Material invalidation or data-quality degradation must trigger confidence recalculation.
7. If statistical calibration has not been demonstrated:
   "CONFIDENCE_CALIBRATION = UNCALIBRATED"

---

SECTION 67 — NO-TRADE / NO-SIGNAL CONDITIONS

The scanner must be able to explicitly output:

"NO_VALID_SIGNAL"

This is a valid system result.

Do not issue a trade-style confirmation when:

1. Critical Binance execution data is stale.
2. Critical Binance execution data is unavailable.
3. Required signal fields are missing.
4. Material cross-exchange conflict remains unresolved under configured rules.
5. Spread/liquidity risk exceeds configured limits.
6. Signal validity window has expired.
7. Duplicate/cooldown protection blocks the event.
8. Data timestamps cannot be trusted.
9. System clock integrity is uncertain.
10. Scanner is operating in unsafe/degraded recovery conditions.
11. The setup depends on information that arrived after the claimed signal time.
12. Required validation conditions cannot be reconstructed from stored evidence.

The reason for "NO_VALID_SIGNAL" must be logged.

---

SECTION 68 — SIGNAL DECAY & EXPIRY

1. Every confirmed setup receives:
   "SIGNAL_EXPIRY_TIMESTAMP"
2. Validity duration must be configurable by:
   - timeframe
   - signal type
   - market condition
3. If the setup is not valid within its configured window:
   "EXPIRED"
4. An expired signal must not be presented as fresh.
5. A new signal must not inherit:
   - old entry
   - old stop/invalidation
   - old target
   - old confidence
   - old catalyst
6. Material market-structure change starts a new evaluation window.

Signal age states

"FRESH"

"AGING"

"NEAR_EXPIRY"

"EXPIRED"

---

SECTION 69 — CHASE PROTECTION

The scanner must prevent hindsight entries.

1. Store first detection price.
2. Store confirmation price.
3. Store current price separately.
4. Calculate movement from:
   - first detection
   - confirmation
5. If price has already moved beyond the configured chase threshold:

"MOVE_EXTENDED — CHASE RISK"

6. The scanner must not move the original entry toward the current price simply to make the setup appear attractive.
7. A continuation after a major move must be treated as a new setup if the configured rules require it.
8. Every new setup gets:
   - new signal ID
   - new snapshot timestamp
   - new validation cycle
9. Telegram output must clearly separate:
   - original detection
   - confirmation
   - current market price

---

SECTION 70 — DUPLICATE & ALERT STORM CONTROL

1. Every signal receives a deterministic:
   "SIGNAL_FINGERPRINT"
2. Duplicate fingerprints are suppressed during configurable cooldown.
3. Repeated observations of one signal must not create unlimited duplicate alerts.
4. Existing signals should use:
   - "UPDATE"
   - "UPGRADE"
   - "DOWNGRADE"
   - "INVALIDATION"
5. Telegram alert rate must be controlled.
6. If alert volume exceeds configured safety limits:

"ALERT_STORM_PROTECTION = ACTIVE"

7. Alert-storm activation must be logged.
8. Alert-storm recovery must also be logged.
9. Health/system alerts must remain distinguishable from market alerts.

---

SECTION 71 — CLOCK & TIMESTAMP INTEGRITY

1. All internal timestamps must use UTC.
2. Preserve separately:
   - source event timestamp
   - collector/receipt timestamp
   - processing timestamp
   - decision timestamp
3. Detect significant system clock drift.
4. If clock integrity is uncertain:
   "DATA_QUALITY = DEGRADED"
5. Timestamps from different exchanges/sources must be normalized before comparison.
6. Every signal snapshot must retain all relevant timing fields.
7. Timestamp uncertainty must never be silently ignored.

---

SECTION 72 — DATA PROVENANCE & IMMUTABILITY

For every important market-data value store:

- source
- exchange
- endpoint/stream
- source timestamp
- receipt timestamp
- parser/version
- freshness state

Rules

1. Raw evidence must not be silently overwritten.
2. Corrections create a new audit event.
3. Missing values remain missing.
4. Estimated values must be explicitly labelled:

"ESTIMATED"

5. Fabricated values are forbidden.
6. Parser changes must have a version.
7. Configuration changes must not rewrite historical raw evidence.
8. The system must be able to identify where an important value came from.

---

SECTION 73 — MODEL / AI GUARDRAILS

If Claude, DeepSeek, or another AI model is used:

1. AI may summarize evidence.
2. AI may classify documented conditions.
3. AI may explain an already-generated result.
4. AI must not invent market data.
5. AI must not invent:
   - price
   - volume
   - OI
   - funding
   - order-book data
   - catalyst information
6. AI cannot convert:

"UNAVAILABLE → CONFIRMED"

7. AI cannot override Binance-authoritative execution data.
8. Deterministic validation rules have priority over AI output.
9. Every AI-assisted evaluation must store:
   - provider
   - model identifier
   - prompt/config version
   - input snapshot ID
   - output
   - timestamp
10. AI-generated interpretation must remain distinguishable from raw exchange facts.
11. If AI output conflicts with deterministic evidence, the conflict must be logged.

---

SECTION 74 — CATALYST & NEWS INTEGRITY

Catalyst sources should preserve:

- source
- URL/reference when available
- source timestamp
- collection timestamp
- verification state

Catalyst states

"NONE"

"POSSIBLE"

"UNVERIFIED"

"VERIFIED"

"CONFLICTED"

"POST_MOVE"

Rules

1. Official sources receive priority for factual verification.
2. Social chatter alone cannot be represented as verified fact.
3. Conflicting reliable sources must remain explicitly conflicting.
4. The system must not silently select one conflicting source.
5. A catalyst discovered after a major market move must not be used as evidence that the scanner predicted the move.
6. Later information must never contaminate the earlier signal snapshot.
7. Catalyst attribution must remain visible in the audit record.

---

SECTION 75 — RISK / REWARD SANITY CHECK

This is an analytical validation layer and is not a guarantee of outcome.

Before a trade-style alert is allowed:

1. Entry must be valid.
2. Invalidation/stop reference must be valid where required.
3. Target must be valid where required.
4. Risk distance must be positive and non-zero.
5. Reward distance must be calculable.
6. Configured minimum risk/reward requirements must be satisfied where applicable.
7. If valid stop/target information cannot be derived:

"RISK_REWARD_UNAVAILABLE"

8. The system must never manufacture a stop or target simply to satisfy a desired risk/reward ratio.
9. Invalid mathematical relationships must block the corresponding validation state.
10. All assumptions must be visible.

---

SECTION 76 — POST-SIGNAL MONITORING

After confirmation:

"CONFIRMED → MONITORING"

Monitoring continues until:

"INVALIDATED"

or

"EXPIRED"

or

"CLOSED_FOR_REVIEW"

Store

1. Maximum favorable movement after signal.
2. Maximum adverse movement after signal.
3. Time to favorable movement.
4. Time to invalidation.
5. Data-quality changes.
6. Cross-exchange changes.
7. Liquidity changes.
8. Catalyst changes.

Rules

1. Post-signal performance must never rewrite the original signal.
2. Original signal snapshot remains immutable.
3. Performance reporting must distinguish:
   - detected opportunity
   - confirmed setup
   - hypothetical/paper outcome
4. Historical outcome must not be used to pretend the original signal was stronger than it actually was.

---

SECTION 77 — BACKTEST / LIVE SEPARATION

1. Backtest and live environments must remain logically separate.
2. Live scanner must never use future candles.
3. Live scanner must never use future news.
4. Backtest must use information only available at each simulated timestamp.
5. Configuration versions must be pinned for reproducibility.
6. Future-known catalyst information must not leak backward.
7. Later exchange data must not be used to strengthen an earlier simulated signal.
8. Backtest results should include applicable:
   - fees
   - spread
   - slippage assumptions
9. Backtest performance is not a guarantee of future results.
10. Live results and backtest results must not be mixed in one performance metric without explicit labeling.

---

SECTION 78 — CONFIGURATION CHANGE CONTROL

Every material configuration change must store:

- previous value
- new value
- reason
- source/author
- timestamp
- configuration version

Examples:

- price-difference threshold
- relative-volume threshold
- OI threshold
- signal expiry
- liquidity bands
- confidence weights
- cooldown
- alert limit
- chase threshold
- freshness thresholds

Rule

A running signal retains the configuration version under which it was evaluated.

Historical signals must not silently change because the current configuration changed.

---

SECTION 79 — SYSTEM SAFETY / KILL SWITCH

Required controls:

"SCANNER_ENABLED"

"ALERTS_ENABLED"

"PAPER_MODE"

"MAINTENANCE_MODE"

"EMERGENCY_STOP"

Rules

1. Safe alert/paper mode is the default.
2. Critical infrastructure failure may pause new confirmations.
3. Existing signals remain auditable.
4. Emergency stop must stop new signal generation/alerts cleanly.
5. Restart must record:
   - reason
   - timestamp
   - previous state
   - recovery state
6. No hidden process may continue market-alert activity after emergency stop.
7. Safety controls must have explicit state values.

---

SECTION 80 — SECURITY & SECRETS

1. API keys must never be hard-coded into source code.
2. Telegram bot tokens are secrets.
3. Exchange API keys are secrets.
4. Secrets must come from:
   - environment variables
   - approved secret storage
5. ".env" must never be committed.
6. ".env.example" may contain variable names but never real secrets.
7. Logs must redact secrets.
8. If an API token is exposed, it must be rotated.
9. Database records must not store plaintext secret values.
10. Backups must not expose secret values.
11. Alert-only operation should not require trading/order permissions.
12. If account-data permissions are ever required, use the minimum permissions necessary.

---

SECTION 81 — HEALTH SCORE & DEGRADED MODES

System health is separate from market-signal confidence.

Health components

- Binance WebSocket
- Binance REST
- Bybit WebSocket
- Bybit REST
- database
- Telegram
- system clock
- rate-limit state
- data freshness

Overall system states

"HEALTHY"

"DEGRADED"

"RECOVERING"

"UNSAFE"

Rules

1. High market confidence cannot override unsafe infrastructure.
2. Critical infrastructure degradation must be visible in alerts.
3. Data-quality problems must not be hidden inside the confidence score.
4. System health must have its own audit events.
5. Recovery must be explicitly recorded.

---

SECTION 82 — RECOVERY & RESTART CONSISTENCY

On restart:

1. Load last persisted state.
2. Mark live streams as requiring revalidation.
3. Do not assume old WebSocket state remains current.
4. Re-fetch required market snapshots.
5. Revalidate freshness.
6. Reconcile monitoring states.
7. Re-check configuration version.
8. Log:

"SYSTEM_RESTART"

"STATE_REHYDRATED"

"DATA_REVALIDATED"

9. Restart alone must never create a duplicate confirmation.
10. A signal must be revalidated before being treated as currently active.

---

SECTION 83 — OBSERVABILITY

Required counters/metrics:

- signals detected
- signals developing
- signals confirmed
- signals invalidated
- signals expired
- upgrades
- downgrades
- cross-verification YES
- cross-verification PARTIAL
- cross-verification NO
- cross-verification UNAVAILABLE
- stale-data events
- missing-data events
- WebSocket reconnects
- stalled streams
- sequence gaps
- REST fallback activations
- rate-limit pressure
- rate-limit errors
- Telegram failures
- Telegram latency
- duplicate suppressions
- chase blocks
- no-valid-signal decisions
- database errors
- backup failures
- system restarts
- emergency stops

Market alerts and system-health alerts must remain distinguishable.

---

SECTION 84 — AUDIT EXPORT

The system must support exporting a complete signal audit package.

Required information

- signal ID
- symbol
- timeframe
- signal type
- original detection timestamp
- original signal snapshot
- confirmation snapshot
- verification snapshot
- source timestamps
- data ages
- Binance data
- Bybit verification data
- cross-exchange result
- liquidity state
- spread state
- catalyst state
- confidence explanation
- missing fields
- conflict state
- configuration version
- state transitions
- AI/model metadata if used
- infrastructure health
- error/recovery events
- post-signal outcome

Audit principle

An independent reviewer should be able to reconstruct:

"At the exact time this signal was generated, what information did the scanner actually have?"

No later information should be silently inserted into that historical reconstruction.

---

SECTION 85 — FINAL INTEGRITY RULE

The scanner must never manufacture certainty.

Priority order

"RAW DATA"

↓

"DATA QUALITY"

↓

"STRUCTURE / SIGNAL RULES"

↓

"CROSS-EXCHANGE VERIFICATION"

↓

"RISK / REWARD SANITY"

↓

"CONFIRMATION"

↓

"MONITORING"

↓

"AUDIT"

Core operating principle

"DETECT EARLY → VERIFY → CONFIRM → PAPER/ALERT → MONITOR → INVALIDATE/EXPIRE → AUDIT"

Absolute integrity rules

The system must never:

1. Use future information.
2. Hide missing data.
3. Convert delayed data into simultaneous data.
4. Treat displayed liquidity as guaranteed execution.
5. Let AI invent market facts.
6. Let AI override deterministic exchange evidence.
7. Convert "UNAVAILABLE" into "CONFIRMED".
8. Silently change historical decisions.
9. Rewrite an old signal after the market has moved.
10. Manufacture an entry, stop, target, volume, OI, catalyst, or other missing value.
11. Treat a backtest result as a guaranteed future result.
12. Present confidence as certainty.
13. Turn a stale signal into a fresh signal.
14. Treat a later catalyst as proof of an earlier prediction.
15. Hide infrastructure failures from the user.

FINAL A2Z PRINCIPLE

A2Z must prefer an honest "NO_VALID_SIGNAL" over a fabricated or poorly supported signal.

A reliable scanner is not one that always produces a signal.

A reliable scanner is one that clearly distinguishes:

"VALID DATA"

"MISSING DATA"

"DEGRADED DATA"

"CONFLICTED DATA"

"CONFIRMED SETUP"

"NO VALID SIGNAL"

"INVALIDATED"

"EXPIRED"

and preserves the evidence behind every decision.8





