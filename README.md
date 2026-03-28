# mini_orchestrator_py

A lightweight, terminal-first orchestration runtime that models multi-step task execution as a structured loop.

Instead of treating tasks as a single-shot operation, this project focuses on how a system can incrementally gather information, make decisions, and execute actions in a controlled and observable way.

---

## Why this project

In many real-world scenarios (e.g., understanding a new code repository), the system does not have full context upfront.

Instead, it must:
- explore the environment
- gather information step by step
- decide what to do next based on current observations

This project is a minimal prototype of such an orchestration layer.

It explicitly models the execution loop:

plan → act → observe → update state → decide next step → finish

The goal is not to build a full agent, but to validate how the execution loop itself should be structured.

---

## Key design ideas

- **State-driven execution**  
  Decisions are not pre-defined. Each step depends on the current state and observations.

- **Separation of concerns**
  - planner: decides what to do next
  - executor: executes commands
  - state: updates structured memory
  - orchestrator: drives the loop

- **Structured observability**  
  Every step is recorded as a trace (action, observation, status), making execution debuggable.

- **Execution vs observation quality**  
  A command may succeed but still provide no useful information. The system distinguishes between these cases.

---

## Current capabilities

- confirm current workspace (`pwd`)
- inspect repository structure (`ls`)
- discover key metadata files (`find`)
- read README and manifest previews (`head`)
- infer project type (Python / Node / Rust)
- generate structured execution traces (`trace.json`)

---


## Real-world testing

Tested on real multi-project repositories.

During testing, a key issue was discovered:
- detecting a file is not sufficient
- the system must also propagate the concrete file path into subsequent actions

This led to introducing explicit path tracking in the state layer, which significantly improved execution correctness.

This highlights the importance of state management in orchestration systems.

---

## Example usage

```bash
python3 main.py \
  --task "Inspect this repository and tell me how to run it" \
  --workspace .
