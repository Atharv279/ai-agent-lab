#!/usr/bin/env python3
"""AI Agent Lab — LLM orchestration simulator with pipeline visualization."""
import json
import os
import random
import datetime
import hashlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AGENTS = {
    "planner": {"role": "Decomposes tasks into subtasks", "temp": 0.3, "color": "#3498db"},
    "researcher": {"role": "Gathers information from knowledge base", "temp": 0.5, "color": "#2ecc71"},
    "coder": {"role": "Generates code solutions", "temp": 0.2, "color": "#e74c3c"},
    "reviewer": {"role": "Reviews and critiques outputs", "temp": 0.4, "color": "#f39c12"},
    "synthesizer": {"role": "Combines agent outputs into final answer", "temp": 0.3, "color": "#9b59b6"},
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

def simulate_agent(name, config, task):
    latency = round(random.uniform(0.1, 2.5), 3)
    tokens_in = random.randint(50, 500)
    tokens_out = random.randint(100, 800)
    quality = round(random.uniform(0.5, 1.0), 3)
    return {
        "agent": name, "role": config["role"], "temperature": config["temp"],
        "latency_seconds": latency,
        "tokens": {"input": tokens_in, "output": tokens_out, "total": tokens_in + tokens_out},
        "quality_score": quality, "status": "success" if quality > 0.6 else "needs_retry",
    }

def orchestrate(task):
    pipeline = []
    for name, config in AGENTS.items():
        pipeline.append(simulate_agent(name, config, task))
    return {
        "task": task, "pipeline": pipeline,
        "metrics": {
            "total_latency": round(sum(r["latency_seconds"] for r in pipeline), 3),
            "total_tokens": sum(r["tokens"]["total"] for r in pipeline),
            "avg_quality": round(sum(r["quality_score"] for r in pipeline) / len(pipeline), 3),
            "agents_used": len(pipeline),
            "retries_needed": sum(1 for r in pipeline if r["status"] == "needs_retry"),
        },
    }

def load_yesterday(date_str):
    yesterday = (datetime.datetime.strptime(date_str, "%Y-%m-%d") - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    path = f"logs/{yesterday}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def compute_delta(today, yesterday):
    if not yesterday:
        return {"status": "no_previous_data"}
    t_agg = today["aggregate"]
    y_agg = yesterday.get("aggregate", {})
    deltas = {}
    for key in ["avg_latency", "total_tokens", "avg_quality"]:
        t_val = t_agg.get(key, 0)
        y_val = y_agg.get(key, 0)
        if y_val:
            deltas[key] = {"today": t_val, "yesterday": y_val, "change_pct": round(((t_val - y_val) / y_val) * 100, 1)}
    return {"status": "compared", "deltas": deltas}

def generate_charts(report, date_str):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"AI Agent Lab — Orchestration Dashboard {date_str}", fontsize=14, fontweight="bold")

    # 1: Quality per agent across tasks
    agent_names = list(AGENTS.keys())
    agent_colors = [AGENTS[a]["color"] for a in agent_names]
    quality_by_agent = {a: [] for a in agent_names}
    for r in report["results"]:
        for p in r["pipeline"]:
            quality_by_agent[p["agent"]].append(p["quality_score"])
    avg_qualities = [sum(v)/len(v) if v else 0 for v in quality_by_agent.values()]
    axes[0][0].bar(agent_names, avg_qualities, color=agent_colors)
    axes[0][0].set_ylim(0, 1)
    axes[0][0].set_ylabel("Avg Quality")
    axes[0][0].set_title("Agent Quality Scores")
    axes[0][0].axhline(y=0.6, color="red", linestyle="--", alpha=0.5, label="Retry threshold")
    axes[0][0].legend(fontsize=8)

    # 2: Token usage per agent
    tokens_by_agent = {a: [] for a in agent_names}
    for r in report["results"]:
        for p in r["pipeline"]:
            tokens_by_agent[p["agent"]].append(p["tokens"]["total"])
    avg_tokens = [sum(v)/len(v) if v else 0 for v in tokens_by_agent.values()]
    axes[0][1].barh(agent_names, avg_tokens, color=agent_colors)
    axes[0][1].set_xlabel("Avg Tokens")
    axes[0][1].set_title("Token Consumption by Agent")

    # 3: Latency waterfall per task
    for i, r in enumerate(report["results"][:3]):
        latencies = [p["latency_seconds"] for p in r["pipeline"]]
        cumulative = [sum(latencies[:j+1]) for j in range(len(latencies))]
        axes[1][0].plot(agent_names, cumulative, "o-", label=f"Task {i+1}", linewidth=2)
    axes[1][0].set_ylabel("Cumulative Latency (s)")
    axes[1][0].set_title("Pipeline Latency Waterfall")
    axes[1][0].legend(fontsize=8)

    # 4: Task-level metrics
    task_labels = [r["task"][:25] + "..." for r in report["results"]]
    task_quality = [r["metrics"]["avg_quality"] for r in report["results"]]
    task_colors = ["#2ecc71" if q > 0.75 else "#f39c12" if q > 0.6 else "#e74c3c" for q in task_quality]
    axes[1][1].barh(task_labels, task_quality, color=task_colors)
    axes[1][1].set_xlim(0, 1)
    axes[1][1].set_xlabel("Avg Quality")
    axes[1][1].set_title("Per-Task Quality")

    plt.tight_layout()
    path = f"logs/{date_str}_dashboard.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path

def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    selected_tasks = random.sample(TASKS, k=min(4, len(TASKS)))
    results = [orchestrate(task) for task in selected_tasks]

    report = {
        "timestamp": now.isoformat(),
        "run_id": hashlib.sha256(now.isoformat().encode()).hexdigest()[:10],
        "tasks_processed": len(results), "results": results,
        "aggregate": {
            "avg_latency": round(sum(r["metrics"]["total_latency"] for r in results) / len(results), 3),
            "total_tokens": sum(r["metrics"]["total_tokens"] for r in results),
            "avg_quality": round(sum(r["metrics"]["avg_quality"] for r in results) / len(results), 3),
        },
    }

    yesterday = load_yesterday(date_str)
    report["delta"] = compute_delta(report, yesterday)

    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{date_str}.json", "w") as f:
        json.dump(report, f, indent=2)

    chart_path = generate_charts(report, date_str)

    md = [f"# AI Agent Lab — Orchestration Report {date_str}\n"]
    md.append(f"**Run ID:** `{report['run_id']}` | **Tasks:** {report['tasks_processed']} | **Avg Quality:** {report['aggregate']['avg_quality']}\n")
    md.append(f"![Dashboard]({os.path.basename(chart_path)})\n")
    md.append("## Aggregate Metrics\n")
    md.append("| Metric | Value |")
    md.append("|--------|-------|")
    for k, v in report["aggregate"].items():
        md.append(f"| {k} | {v} |")
    if report["delta"].get("status") == "compared":
        md.append("\n## Delta vs Yesterday\n")
        md.append("| Metric | Today | Yesterday | Change |")
        md.append("|--------|-------|-----------|--------|")
        for k, d in report["delta"]["deltas"].items():
            arrow = "📈" if d["change_pct"] > 0 else "📉"
            md.append(f"| {k} | {d['today']} | {d['yesterday']} | {arrow} {d['change_pct']}% |")
    md.append("\n## Pipeline Results\n")
    for r in results:
        md.append(f"### {r['task'][:60]}")
        md.append("| Agent | Quality | Latency | Tokens | Status |")
        md.append("|-------|---------|---------|--------|--------|")
        for p in r["pipeline"]:
            md.append(f"| {p['agent']} | {p['quality_score']} | {p['latency_seconds']}s | {p['tokens']['total']} | {p['status']} |")
        md.append("")

    with open(f"logs/{date_str}.md", "w") as f:
        f.write("\n".join(md))
    print("[ai-agent-lab] v2.0 report + charts generated")

if __name__ == "__main__":
    main()
