#!/usr/bin/env python3
"""AI Agent Lab — Local-first LLM orchestration simulator."""
import json, os, random, datetime, hashlib, time

AGENTS = {
    "planner": {"role": "Decomposes tasks into subtasks", "temp": 0.3},
    "researcher": {"role": "Gathers information from knowledge base", "temp": 0.5},
    "coder": {"role": "Generates code solutions", "temp": 0.2},
    "reviewer": {"role": "Reviews and critiques outputs", "temp": 0.4},
    "synthesizer": {"role": "Combines agent outputs into final answer", "temp": 0.3},
}

TASKS = [
    "Build a REST API for user authentication",
    "Analyze CSV data and generate statistical summary",
    "Refactor legacy codebase to use dependency injection",
    "Write integration tests for payment processing module",
    "Design a caching strategy for high-traffic endpoints",
    "Implement rate limiting middleware",
    "Create a data migration script for schema v2",
    "Build a CLI tool for log analysis",
]

def simulate_agent(name, config, task, context=""):
    latency = round(random.uniform(0.1, 2.5), 3)
    tokens_in = random.randint(50, 500)
    tokens_out = random.randint(100, 800)
    quality = round(random.uniform(0.5, 1.0), 3)
    return {
        "agent": name,
        "role": config["role"],
        "temperature": config["temp"],
        "task_input": task[:80],
        "latency_seconds": latency,
        "tokens": {"input": tokens_in, "output": tokens_out, "total": tokens_in + tokens_out},
        "quality_score": quality,
        "status": "success" if quality > 0.6 else "needs_retry",
    }

def orchestrate(task):
    pipeline = []
    context = ""
    for name, config in AGENTS.items():
        result = simulate_agent(name, config, task, context)
        pipeline.append(result)
        context += f"[{name}:{result['quality_score']}]"
    total_latency = round(sum(r["latency_seconds"] for r in pipeline), 3)
    total_tokens = sum(r["tokens"]["total"] for r in pipeline)
    avg_quality = round(sum(r["quality_score"] for r in pipeline) / len(pipeline), 3)
    return {
        "task": task,
        "pipeline": pipeline,
        "metrics": {
            "total_latency": total_latency,
            "total_tokens": total_tokens,
            "avg_quality": avg_quality,
            "agents_used": len(pipeline),
            "retries_needed": sum(1 for r in pipeline if r["status"] == "needs_retry"),
        },
    }

def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    selected_tasks = random.sample(TASKS, k=min(3, len(TASKS)))

    results = []
    for task in selected_tasks:
        results.append(orchestrate(task))

    report = {
        "timestamp": now.isoformat(),
        "run_id": hashlib.sha256(now.isoformat().encode()).hexdigest()[:10],
        "tasks_processed": len(results),
        "results": results,
        "aggregate": {
            "avg_latency": round(sum(r["metrics"]["total_latency"] for r in results) / len(results), 3),
            "total_tokens": sum(r["metrics"]["total_tokens"] for r in results),
            "avg_quality": round(sum(r["metrics"]["avg_quality"] for r in results) / len(results), 3),
        },
    }

    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{date_str}.json", "w") as f:
        json.dump(report, f, indent=2)

    md = [f"# AI Agent Lab — Orchestration Report {date_str}\n"]
    md.append(f"**Run ID:** `{report['run_id']}` | **Tasks:** {report['tasks_processed']}\n")
    md.append(f"## Aggregate Metrics\n")
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    for k, v in report["aggregate"].items():
        md.append(f"| {k} | {v} |")
    md.append(f"\n## Task Results\n")
    for r in results:
        md.append(f"### {r['task'][:60]}")
        md.append(f"| Agent | Quality | Latency | Tokens | Status |")
        md.append(f"|-------|---------|---------|--------|--------|")
        for p in r["pipeline"]:
            md.append(f"| {p['agent']} | {p['quality_score']} | {p['latency_seconds']}s | {p['tokens']['total']} | {p['status']} |")
        md.append("")

    with open(f"logs/{date_str}.md", "w") as f:
        f.write("\n".join(md))

    print(f"[ai-agent-lab] Report generated: logs/{date_str}.md")

if __name__ == "__main__":
    main()
