# OpenSpec Autosteer

This directory is the control layer for the automated OpenSpec workflow.

It is intentionally separate from:

- `openspec/`
  - source of truth for specs and changes
- `openspec_py/`
  - execution engine

Current contents:

- `docs/`
  - requirements and architecture input for planning agents
- `guidance/`
  - reusable implementation and validation guidance
- `reviews/`
  - acceptance and review reports
- `regulations/`
  - project-specific workflow rules beyond official OpenSpec defaults
- `feed/`
  - human control inputs for the scheduler
- `registry/`
  - static agent and runner definitions
- `runtime/`
  - derived runtime state and indices
- `prompts/`
  - reusable prompt templates
- `scripts/`
  - future control-layer scripts
