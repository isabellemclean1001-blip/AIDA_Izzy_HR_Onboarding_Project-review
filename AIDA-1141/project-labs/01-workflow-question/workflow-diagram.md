# Workflow Diagram – Onboarding Request Routing and Follow-Up

```mermaid
flowchart TD
    A["Hiring manager or HR submits<br/>one-task request<br/><i>Status: Open</i>"]
    C{"Required info missing<br/>or conflicting?"}
    E["Coordinator requests missing info<br/><i>Status: Waiting for information</i>"]
    A2["Requester provides missing info"]
    B["Routing rule assigns<br/>responsible team"]
    D["Checkpoint 1 (intake):<br/>model scores risk of<br/>missing start date"]
    F{"★ Coordinator:<br/>follow up?"}
    L["Coordinator follows up or<br/>expedites with team"]
    H["Team works on task<br/><i>Status: In progress</i>"]
    K{"Checkpoint 2 applies?<br/>(still incomplete 5 business<br/>days before start, after intake)"}
    G["Checkpoint 2:<br/>model re-scores risk"]
    F2{"★ Coordinator:<br/>follow up?"}
    L2["Coordinator follows up or<br/>expedites with team"]
    I["Team completes task<br/>and confirms"]
    J["Coordinator confirms completion<br/><i>Status: Complete</i>"]

    A --> C
    C -->|Yes| E --> A2 --> C
    C -->|No| B --> D --> F
    F -->|"Yes (at risk)"| L --> H
    F -->|No| H
    H --> K
    K -->|Yes| G --> F2
    K -->|No| I
    F2 -->|"Yes (at risk)"| L2 --> I
    F2 -->|No| I
    I --> J

    classDef requester fill:#e9d5ff,stroke:#7e22ce,stroke-width:2px,color:#000;
    classDef system fill:#f3f4f6,stroke:#374151,stroke-width:3.5px,stroke-dasharray:8 4,color:#000;
    classDef coordinator fill:#fef3c7,stroke:#b45309,color:#000;
    classDef human fill:#fef3c7,stroke:#b45309,stroke-width:3px,color:#000;
    classDef team fill:#dcfce7,stroke:#15803d,color:#000;

    class A,A2 requester;
    class B,C,D,G,K system;
    class E,J,L,L2 coordinator;
    class F,F2 human;
    class H,I team;
```

### Legend

| Colour / style | Role |
|:---|:---|
| 🟪 Purple | Requester (hiring manager or HR staff) |
| ⬜ Grey, dashed border | System (routing rule, information check, risk model) |
| 🟨 Yellow | Coordinator |
| 🟩 Green | Responsible team |

| Shape / marker | Meaning |
|:---|:---|
| ▭ Rectangle | A step or action |
| ◇ Diamond | A yes/no decision point |
| ★ Bold border | Key decision: coordinator reviews the model's suggestion |

**Notes:** The coordinator confirms the routing rule's team when reviewing checkpoint 1. Low model confidence or an unusual case adds a flag for coordinator review at either checkpoint. Each request has at most two assessments. Checkpoint 2 only applies if it falls after the intake assessment and the task is still incomplete. Requests received at or after that checkpoint receive only the intake assessment. All suggested actions require human confirmation. 

Timestamps recorded at every status change · Synthetic data only · Fictional Town of Pinecrest · No connection to real HR/ERP systems.
