<div align="center">

# 🧪 AI Agent Lab

[![Daily Run](https://github.com/USER/ai-agent-lab/actions/workflows/daily_run.yml/badge.svg)](https://github.com/USER/ai-agent-lab/actions/workflows/daily_run.yml)
![Python](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Automated](https://img.shields.io/badge/Runs-Daily%20via%20CI-blue)

**Multi-agent LLM orchestration simulator with pipeline visualization and performance tracking.**

</div>

---

## Architecture

```mermaid
graph TD
    T[📋 Task Queue] --> P[🗂️ Planner]
    P --> R[🔬 Researcher]
    R --> C[💻 Coder]
    C --> V[👁️ Reviewer]
    V -->|Quality < 0.6| C
    V -->|Quality ≥ 0.6| S[🧩 Synthesizer]
    S --> M[📊 Metrics Engine]
    M --> D[📈 Dashboard Generator]
    M --> Delta[🔄 Delta Comparison]
    D --> Report[📋 Daily Report]
    Delta --> Report
    Report -->|Git Push| Deploy[🚀 GitHub]
```

## Agent Pipeline

| Agent | Role | Temperature |
|-------|------|-------------|
| **Planner** | Decomposes tasks into subtasks | 0.3 |
| **Researcher** | Gathers information from knowledge base | 0.5 |
| **Coder** | Generates code solutions | 0.2 |
| **Reviewer** | Reviews and critiques outputs | 0.4 |
| **Synthesizer** | Combines outputs into final answer | 0.3 |

## Live Dashboard Preview

![Dashboard](logs/2026-03-07_dashboard.png)

## Output Structure

```
logs/
├── YYYY-MM-DD.json          # Full pipeline data
├── YYYY-MM-DD.md            # Markdown report with delta analysis
└── YYYY-MM-DD_dashboard.png # 4-panel visual dashboard
```

## Quick Start

```bash
pip install -r dev-requirements.txt
python main.py
```
