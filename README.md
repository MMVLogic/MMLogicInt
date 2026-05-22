# 🛡️ LogiKeep AI — Autonomous Customs Compliance & Audit Pipeline

LogiKeep AI is an enterprise-grade Service-as-a-Software (SaaS) architecture designed to eliminate human data-entry overhead and mitigate compliance risks in cross-border maritime logistics. 

The platform autonomously intercepts unstructured shipping documents, parses nested entity hierarchies, maps regulatory tariff categories using highly efficient data structures, and runs linear optimization algorithms to detect cost and weight leakages across multi-document streams.

---

## 🧠 Architectural Engineering & Algorithmic Core

Unlike standard AI "wrappers" that pass massive, fragile text prompts to LLMs, LogiKeep AI utilizes an **Agentic Orchestration Framework** where artificial intelligence handles loose semantic translation, while traditional, deterministic algorithms enforce mathematical rigor and scalability.
[ Messy Unstructured Shipping Documents ] 
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│ 1. Multimodal Structured Ingestion Agent         │
│    Extracts token-efficient bounding JSON matrices│
└─────────────────────────┬────────────────────────┘
│
▼
┌──────────────────────────────────────────────────┐
│ 2. O(L) Bounded Prefix Tariff Tree (Trie)        │
│    Deterministic regional tax traversal pathways │
└─────────────────────────┬────────────────────────┘
│
▼
┌──────────────────────────────────────────────────┐
│ 3. Bipartite Graph Matching Engine               │
│    Linear Sum Assignment / Hungarian Algorithm    │
└─────────────────────────┬────────────────────────┘
│
▼
[ Validated, Audit-Cleared Compliance Payload ]
### 1. Spatial & Geometric JSON Normalization
Relying on raw text chunking destroys row-column correlations within shipping manifests. LogiKeep enforces structural containment schema layout mapping via Pydantic matching to isolate line names and numeric mass parameters cleanly before array ingestion.

### 2. O(L) Bounded Prefix Search Tree (Trie)
Global Harmonized System (HS) codes are strictly hierarchical paired-digit indexes. To prevent slow, non-deterministic database vector inquiries, our custom database engine parses national tariffs into a local dynamic Prefix Trie, capping lookup time complexity at a constant $O(L)$, where $L$ is the static depth of the regulatory classification string.

### 3. Weighted Bipartite Graph Optimization (The Cross-Doc Audit)
Cross-document reconciliation is modeled as a **Bipartite Graph Matching problem**. The engine constructs localized independent vertex sheets (Invoice vs Cargo Bill) and calculates an absolute difference distance matrix. It executes the **Hungarian Algorithm** (`scipy.optimize.linear_sum_assignment`) to find global matching pairs and isolate weight variances over strict tolerance thresholds.

---

## ⚙️ Workspace Setup & Dependencies

The system is engineered using highly optimized scientific computing layers and the official Google GenAI ecosystem.

### Prerequisites
* **Python 3.10+**
* An active Gemini API Key (Accessible via Google AI Studio)

### Installation Sequence
1. Clone this repository locally:
   
```bash
   git clone [https://github.com/yourusername/logikeep-ai.git](https://github.com/yourusername/logikeep-ai.git)
   cd logikeep-ai
Install pinned, cross-compatible dependencies:

Bash
   pip install -r requirements.txt
Create an environment configuration file in the project root:

Bash
   touch .env
Populate your environment variables inside the .env file:

Code snippet
   GEMINI_API_KEY=AIzaSyYourSecretKeyHere
🏃‍♂️ Launching the Application Interface
To initialize the live reactive pipeline dashboard interface on your local server loop, run:

Bash
streamlit run app.py
Open your browser to http://localhost:8501 to interface with the multi-regional compliance suite dashboard.`