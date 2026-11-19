# Research notes

## SHADE-Arena — Kutasov et al. (2025)

**What it studied.** Agents performed legitimate tasks alongside hidden harmful
objectives. A separate LLM monitor reviewed their behavior. The study measured
task completion, harmful outcomes, and detection separately.

**Design choice in this lab.** F01 pairs a legitimate diagnostics task with a
synthetic disclosure objective. The monitor sees the proposed action and its
context. An independent sink check establishes what was actually recorded.

**Scope.** SHADE-Arena studies a scratchpad hidden from the monitor. Our small
replay comparison varies whether the reviewer sees reasoning text that the
local model exposes. Our results cover the recorded trajectories we tested.

[SHADE-Arena paper](https://arxiv.org/abs/2506.15740)

## AI Control: Improving Safety Despite Intentional Subversion — Greenblatt et al. (2024)

**What it studied.** The authors evaluated safeguards for programming tasks
under the assumption that the model could deliberately undermine them. The
study considered both safety and the ability to deliver useful work.

**Design choice in this lab.** We track harmful outcomes and legitimate task
completion separately. An F01 denial can prevent a disclosure while leaving
the assigned task unfinished. F04 and F08 use independent checks and receipts
to establish whether useful work completed.

**Scope.** The lab reports individual outcomes for local fixtures and runs.
It does not estimate safety guarantees under adaptive adversaries.

[AI Control paper](https://arxiv.org/abs/2312.06942)

## Watcher — Apollo Research

**What the documentation describes.** Watcher records coding-agent trajectories,
uses LLM graders, and supports blocking review before a tool call executes as
well as review that follows a session.

**Design choice in this lab.** We separate replay judgments from live gate
decisions. In F01, the harness can deny a proposed submission before it reaches
the broker. In replay, it records what a reviewer would have decided.

**Scope.** Watcher is a design reference. The lab implements and evaluates its
own small harness with local Ollama and Docker.

[Watcher concepts](https://watcher-docs.apolloresearch.ai/concepts/)