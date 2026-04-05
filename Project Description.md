# 📘 CS416: Large Language Models Project (SP26)

## 🎯 Course Learning Outcomes (CLOs)

- **CLO-3:** Apply transfer learning and prompt engineering for LLM problems
- **CLO-5:** Design pipelines and fine-tune LLMs for NLP tasks collaboratively
- **CLO-6:** Gain proficiency in modern LLM tools

---

## 🧠 Project Overview

Design an LLM-based AI assistant for a local bank that:

- Handles customer queries
- Generates context-aware responses
- Maintains data privacy and trust

---

## 📂 Dataset

- **Source:** Provided via LMS
- **Formats:** JSON / CSV / Text
- **Tasks:**
  - Parsing
  - Preprocessing
  - Cleaning & anonymization

---

## ⚙️ Project Requirements

### 1. Data Ingestion & Preprocessing
- Read and sanitize the dataset
- Perform anonymization (if needed)
- Apply:
  - Tokenization
  - Lowercasing
  - Text cleaning

### 2. LLM Selection
- **Allowed:** Open-source models (e.g., LLaMA, T5, DeepSeek)
- ❌ **Not allowed:** Commercial models (e.g., ChatGPT)
- **Constraint:** ≤ 6 billion parameters
- Must justify model choice

### 3. Embedding & Indexing
- Create an embedding-based index
- Store vector embeddings for documents/chunks
- Enable fast retrieval

### 4. Fine-Tuning & Inference
- Fine-tune LLM on the bank dataset
- Retrieval + generation pipeline:
  - Retrieve relevant chunks
  - Generate response

### 5. Prompt Engineering
- Simulate a helpful banking assistant
- Requirements:
  - Domain-specific answers
  - Graceful handling of out-of-domain queries

### 6. Real-Time Updates
- Support adding new documents dynamically
- Newly added data must:
  - Be indexed instantly
  - Be queryable immediately
- *Optional:* UI for uploading documents

### 7. Performance & Reliability
- Low latency for complex queries
- Scalable to large datasets
- Maintain response quality

### 8. Git Collaboration
- Continuous commits (not one-time upload)
- All members must contribute
- Use GitHub/Bitbucket (private repo allowed)

### 9. System Interface (UI)
- **Features:**
  - Ask questions
  - View responses
  - Upload documents
- **Design:** Simple & trustworthy

### 10. Guard Rails & Safety
- Implement:
  - Content filtering
  - Policy enforcement
- Must handle:
  - Harmful queries
  - Prompt injection
  - Jailbreak attempts

---

## 🧮 Grading Criteria (Total: 20 Marks)

### 📊 Rubric Breakdown

| # | Component | Marks | Excellent | Good | Satisfactory | Poor |
|---|---|---|---|---|---|---|
| 1 | **Data Preprocessing** | 2 | Full anonymization + clean pipeline | — | Minor issues | Unsafe / inconsistent handling |
| 2 | **Vector Embeddings & Retrieval** | 3 | Highly relevant retrieval | Mostly relevant | Mixed results | Poor retrieval |
| 3 | **Prompt Engineering** | 2 | Stable, safe, domain-correct | — | Some hallucinations | Unsafe or confusing |
| 4 | **Guard Rails & Safety** | 3 | Strong jailbreak resistance | Mostly effective | Basic checks | Easily bypassed |
| 5 | **Response Quality & Latency** | 2 | Accurate + low latency | — | Acceptable delay | Slow or incorrect |
| 6 | **Real-Time Updates** | 2 | Instant ingestion | — | Manual steps required | No update mechanism |
| 7 | **Code Quality & Documentation** | 2 | Clean, modular, well-documented | — | Limited structure | Hard to follow |
| 8 | **System Interface** | 1 | Clean, intuitive UI | — | — | Confusing or missing |
| 9 | **Git Collaboration** | 3 | Frequent commits + teamwork | Consistent commits | Limited history | Single upload |

### 📌 CLO Weightage

| CLO | Marks |
|---|---|
| CLO-3 | 7 |
| CLO-5 | 7 |
| CLO-6 | 6 |
| **Total** | **20** |

---

## 📅 Project Timeline

| # | Milestone | Details | Deadline |
|---|---|---|---|
| 1 | **Project Proposal** | Group members, tools & frameworks | 📌 11 Feb 2026 |
| 2 | **LLM Implementation** | Code (prototype) + architecture diagram | 📌 8 Mar 2026 *(Lab Project)* |
| 3 | **Final Submission** | Full system: ingestion, embeddings, model integration, guard rails, UI + documentation | 📌 5 Apr 2026 *(Course Project)* |
| 4 | **Presentation, Demo & Viva** | Presentation + Demo → Course Project; Viva → Lab Final | 📌 8 Apr 2026 |

---

## 🧩 Complex Problem Requirements

### Key Aspects
- Requires deep engineering knowledge
- Data quality assessment + chunking strategy
- Strong understanding of LLM internals
- Interdependent pipeline components

### ⚙️ Complex Engineering Activities
- Use multiple libraries (LLM, UI, guardrails)
- High component interaction
- Requires innovation for:
  - Scaling
  - Retrieval performance
- Extend knowledge to:
  - Embeddings
  - Semantic ranking
  - Prompt engineering
