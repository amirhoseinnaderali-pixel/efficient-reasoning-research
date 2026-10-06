# Prior Work

Existing repositories were inspected as **read-only**. None was modified.

## Test-time / reasoning

### `LLM_reasoning_solve_NQueen_with_no_code`
README and Python implementation inspected. It uses Ollama `llama3.2:1b`, a strict n-Queens representation, and iterative re-feeding of previous output. The implementation contains a documented hard-coding issue for `n`/`max_steps`. Reused concept: sequential refinement under a verifiable task.

### `Reasoning-Agent---Multi-Stage-AI-Reasoning-System`
README and source inspected. It implements Planner → Logic Agent → Judge → conditional Replanner in LangGraph, using an LLM score. Reused concept: modular staged reasoning. New framework replaces judge-as-primary-signal with objective execution for code tasks.

### `multi-agent-react-sandbox`
README and sandbox code inspected. It describes 24 agents, ReAct-style refinement, and Docker/subprocess execution with test validation. Reused concept: isolated execution feedback.

### `Reasoning-Is-All-You-Need`
README/reproducibility/audit artifacts and implementation structure inspected. Reused concept: execution-based reasoning/debugging and reproducibility discipline.

### `codechain`
README inspected. It explicitly frames a controlled Single vs sequential-chain comparison, tracks model calls, uses executable correctness, and separates visible candidate selection from held-out evaluation. This is a direct methodological precursor to EXP-001.

### `graph_reasoning`
README inspected. It treats graph-based candidate aggregation as a hypothesis over heterogeneous reasoning trajectories. Reused concept: graph aggregation as one condition rather than an isolated demo.

### `agentCoder` / `agent_coder`
Repositories and primary agent files were located. Detailed claims beyond their multi-agent coding role are **UNVERIFIED in this pass**.

### `ox` / `ox-vs-claude-vs-grok`
Repositories were located. Detailed experimental claims are **UNVERIFIED in this pass**.

## Training / adaptation

### `DistillLlama-Curriculum`
README inspected. It uses a four-stage LoRA curriculum on DeepSeek-R1-Distill-Llama-8B with optional teacher distillation for coding/reasoning. Reused as training-lineage context; kept outside inference-only EXP-001.

### `Phi-to-Qwen-Knowledge-Distillation` / `Phi-4-to-Qwen-Knowledge-Distillation`
README inspected. They use teacher-generated soft labels, CE + KL distillation, selective student fine-tuning, and memory-saving methods. Reused as future training/adaptation lineage. Reported expected performance numbers are not imported as evidence.

### `DPO-Training-Benchmark-Performance-Comparison-of-Distributed-Training-Methods-for-LLMs`
README inspected. It reports a historical TinyLlama/dual-T4 comparison across Standard, FSDP and DeepSpeed configurations. Reused lesson: measure systems dimensions explicitly; historical numbers are not EXP-001 evidence.

### `Fine-tune-Qwen2.5-Coder-14B-on-HumanEval-MBPP-using-LoRA`
README inspected. It uses 4-bit Qwen2.5-Coder-14B + LoRA/Unsloth on HumanEval/MBPP. Reused as coding-model adaptation lineage.

### Additional located repositories
`FineTune_T5_on_imdb`, `qwen-math-reasoning`, `1-fine-tuning-structured-output-llama2`, `vulnerability-detection-ai`, `AutoTune-Research-Assistan`, `auto-finetune-llm`, `SmartRAG`, `Multimodal_Rag`, and `deepresearch-agent` were located. Detailed claims about their internals are **UNVERIFIED in this pass**.

## Scientific traceability

Historical evidence → concept → reimplementation → controlled experiment. No historical prototype output is silently relabeled as a new result.
