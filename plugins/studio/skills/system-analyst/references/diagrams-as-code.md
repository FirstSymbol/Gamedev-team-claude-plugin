# Diagrams as code (Mermaid, PlantUML, C4)

## Which diagram for which question
| Question | Diagram | Tool default |
|---|---|---|
| Who/what interacts with the system? | C4 L1 System Context | Mermaid C4 / Structurizr |
| Which deployable units and protocols? | C4 L2 Container | Structurizr DSL or C4-PlantUML |
| Inside one service? | C4 L3 Component (only if it helps) | C4-PlantUML |
| Order of calls, failure paths | Sequence | Mermaid `sequenceDiagram` |
| Lifecycle of an entity | State | Mermaid `stateDiagram-v2` |
| Data structure | ER | Mermaid `erDiagram` |
| Domain types/contracts | Class | Mermaid `classDiagram` |
| Business process | Flowchart (BPMN-lite) | Mermaid `flowchart` (see business-analyst process-modeling) |
| Infra/runtime placement | C4 Deployment | Structurizr / C4-PlantUML |
Rules: one diagram = one question; ≤ ~15 nodes; title + legend when colors/styles carry meaning;
diagrams live next to the spec in markdown; GitHub/GitLab render ```mermaid natively.

## Mermaid sequence
```mermaid
sequenceDiagram
  autonumber
  actor P as Player
  participant C as Unity client
  participant API as Game API (.NET)
  participant S as Google Play
  participant DB as Postgres
  P->>C: Tap "Buy 1000 coins"
  C->>S: launchBillingFlow(sku)
  S-->>C: purchaseToken
  C->>+API: POST /purchases (Idempotency-Key, token)
  API->>S: purchases.products.get(token)
  alt valid and not yet granted
    API->>DB: ledger txn + outbox (one transaction)
    API-->>C: 200 {balance}
    C->>S: consume(token)
  else already granted
    API-->>C: 200 {balance} (replayed)
  else invalid
    API-->>-C: 422 problem+json
  end
  Note over C,API: timeout → retry same key (max 3, backoff)
```
- Arrows: `->>` sync call, `-->>` reply, `-)` async message, `-x` lost/failed.
- Blocks: `alt/else`, `opt`, `loop`, `par/and`, `critical/option`, `break`, `rect rgb(…)`.
- `+`/`-` on arrows = activate/deactivate; `autonumber` for step refs in specs.
- Gotchas: `;` and `#` in text need escaping (`#59;`); avoid the word `end` unquoted in labels.

## Mermaid state
```mermaid
stateDiagram-v2
  [*] --> Requested
  Requested --> Approved: kyc_ok && limits_ok
  Requested --> Rejected: kyc_fail / notify
  Approved --> Sent: payout_submitted
  Sent --> Settled: psp.settled
  Sent --> Failed: psp.failed
  Failed --> Requested: auto_retry [attempts < 3]
  state Approved {
    [*] --> AwaitingReview
    AwaitingReview --> Cleared: amount < 500 or reviewer_ok
  }
  Settled --> [*]
  Rejected --> [*]
```
- Label transitions `event [guard] / action`; `<<choice>>`, `<<fork>>`, `<<join>>` pseudo-states;
  `note right of X` for invariants. Every non-final state needs an exit (timeouts!).

## Mermaid class
```mermaid
classDiagram
  class Wallet {
    +string PlayerId
    +long BalanceMinor
    +Credit(long amount, string key) LedgerTxn
    +Debit(long amount, string key) LedgerTxn
  }
  class LedgerTxn {
    +Guid Id
    +string IdempotencyKey
    +TxnKind Kind
  }
  class TxnKind {
    <<enumeration>>
    PurchaseGrant
    Bet
    Win
    Refund
  }
  Wallet "1" --> "*" LedgerTxn : records
  LedgerTxn --> TxnKind
```
Relations: `<|--` inheritance, `*--` composition, `o--` aggregation, `-->` association,
`..>` dependency, `..|>` realization. Visibility `+ - # ~`.

## Mermaid ER
```mermaid
erDiagram
  PLAYER ||--o{ SESSION : starts
  PLAYER ||--o{ PURCHASE : makes
  PURCHASE }o--|| SKU : "of"
  SKU {
    text id PK
    int price_tier
  }
```
Cardinality pairs: `|o` zero/one, `||` exactly one, `}o` zero/many, `}|` one/many;
`--` identifying (solid), `..` non-identifying (dashed). Attribute keys `PK`, `FK`, `UK`.

## Mermaid C4 (experimental — syntax may change; compatible with C4-PlantUML)
```mermaid
C4Container
  title Container diagram — Social casino
  Person(player, "Player", "Mobile user")
  System_Ext(store, "App Store / Google Play", "IAP")
  System_Boundary(sc, "Social casino platform") {
    Container(app, "Game client", "Unity 6, C#", "Slots, lobby, store")
    Container(api, "Game API", ".NET 10, ASP.NET Core", "Auth, wallet, rewards")
    ContainerDb(db, "OLTP DB", "PostgreSQL", "Players, ledger")
    Container(bus, "Event bus", "Kafka/RabbitMQ", "Domain events")
    Container(admin, "Back-office", "React SPA", "CS, live-ops")
  }
  Rel(player, app, "Plays")
  Rel(app, api, "Calls", "HTTPS/JSON")
  Rel(api, db, "Reads/writes", "SQL")
  Rel(api, bus, "Publishes", "outbox")
  Rel(api, store, "Validates receipts", "HTTPS")
  Rel(admin, api, "Manages", "HTTPS")
```
Types: `C4Context`, `C4Container`, `C4Component`, `C4Dynamic`, `C4Deployment`. Elements:
`Person`, `System`, `System_Ext`, `SystemDb`, `Container`, `ContainerDb`, `ContainerQueue`,
`Component`, `*_Boundary`, `Rel`, `BiRel`. Layout: `UpdateLayoutConfig($c4ShapeInRow="3")`.

## C4 model rules (c4model.com)
- Levels: 1 System Context (people + systems), 2 Container (separately deployable/runnable
  units: apps, DBs, queues), 3 Component (inside a container), 4 Code (rarely drawn; use IDE).
- Every element: name, type, technology, 1-line responsibility. Every relationship: verb
  phrase + protocol/tech ("Publishes events to", "gRPC"). Unidirectional arrows.
- Include a key/legend; avoid ambiguous acronyms; draw L1 + L2 for every system, L3 only when
  a container is complex; supplementary: dynamic (numbered flows) and deployment diagrams.
- "Container" ≠ Docker container. A Unity client and a DB are both containers.

## Structurizr DSL (model once, many views)
```
workspace "Social casino" {
  model {
    player = person "Player"
    store = softwareSystem "App stores" { tags "External" }
    sc = softwareSystem "Social casino" {
      app = container "Game client" "Slots, lobby" "Unity 6"
      api = container "Game API" "Wallet, rewards" ".NET 10"
      db  = container "OLTP DB" "Players, ledger" "PostgreSQL" { tags "Database" }
    }
    player -> app "Plays"
    app -> api "Calls" "HTTPS/JSON"
    api -> db "Reads/writes" "SQL"
    api -> store "Validates receipts" "HTTPS"
  }
  views {
    systemContext sc { include * autolayout lr }
    container sc { include * autolayout lr }
    styles { element "Database" { shape cylinder } element "External" { background #999999 } }
  }
}
```
Render: Structurizr Lite/vNext (Docker) or export to PlantUML/Mermaid via Structurizr CLI
(verify: current Structurizr tooling names).

## PlantUML essentials
```plantuml
@startuml
!include <C4/C4_Container>
Person(player, "Player")
System_Boundary(sc, "Social casino") {
  Container(api, "Game API", ".NET 10")
  ContainerDb(db, "OLTP DB", "PostgreSQL")
}
Rel(player, api, "Uses", "HTTPS")
Rel(api, db, "Reads/writes", "SQL")
SHOW_LEGEND()
@enduml
```
- Sequence: `participant`, `->` / `-->`, `activate`, `alt/else/end`, `group`, `== section ==`,
  `...delay...`, `autonumber`. Same structure as Mermaid; PlantUML better for very large diagrams.
- Activity (swimlanes `|Lane|`), state, component, deployment, timing, and `@startjson` / `@startyaml`
  for payload visualization. Requires Java/Graphviz or a PlantUML server to render.

## Review checklist
- [ ] Diagram answers one stated question; title present; ≤ ~15 nodes.
- [ ] Sequence includes failure branches (timeout, duplicate, partner error) and retries.
- [ ] State diagram: all states reachable, every non-final state has an exit, guards labeled.
- [ ] C4 relationships labeled with intent + protocol; externals visually distinct; legend.
- [ ] Names match the spec/contract identifiers (service names, endpoints, entities).
- [ ] Renders without errors (Mermaid Live Editor / PlantUML server) before handoff.

## Sources
- Mermaid sequence diagram syntax https://mermaid.js.org/syntax/sequenceDiagram.html
- Mermaid state diagrams https://mermaid.js.org/syntax/stateDiagram.html
- Mermaid class diagrams https://mermaid.js.org/syntax/classDiagram.html
- Mermaid C4 diagrams (experimental) https://mermaid.js.org/syntax/c4.html
- C4 model (Simon Brown) https://c4model.com/
- Structurizr DSL language reference https://docs.structurizr.com/dsl/language
- C4-PlantUML https://github.com/plantuml-stdlib/C4-PlantUML
- PlantUML sequence diagrams https://plantuml.com/sequence-diagram
