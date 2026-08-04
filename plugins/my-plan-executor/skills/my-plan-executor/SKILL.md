---
name: my-plan-executor
description: Execute an explicitly invoked saved implementation plan from pasted `.md` text or `docs/superpowers/plans/*.md`; read the paired spec, default to subagent-driven execution in a separate worktree unless the user explicitly chooses inline/current-worktree/main-branch alternatives, and delegate execution discipline to Superpowers plus repo instructions.
---

# My Plan Executor

Use the plan as the contract. Let Superpowers and repo instructions handle the
heavy workflow.

1. Read `AGENTS.md`, the plan, and the paired spec.
2. Assume the plan as approved unless user says review-only.
   - Invoking this skill with a saved plan path or pasted plan is explicit
     current-thread approval to commit that plan and its paired spec first,
     unless the user says `review-only`, `no commit`, or equivalent.
3. Parse only two independent choices:
   - Implementation mode: default to `subagent driven`; use `inline` only when
     the user explicitly says inline.
   - Workspace mode: default to a separate worktree; use a current-worktree
     alternative only when the user explicitly says `stay on main`, `no branch`,
     `current worktree`, or `new branch`.
4. Treat `inline` as implementation mode only. It does not imply staying on
   `main`; `do it inline` still defaults to a separate worktree.
5. Resolve workspace alternatives this way:
   - `stay on main` or `no branch`: stay in the current worktree on `main`
     without creating a branch.
   - `new branch`: stay in the current worktree and create/use a task branch.
   - missing workspace choice: create/use a separate worktree.
6. Ask only for risky git/dirt cases, such as uncommitted edits that would block
   switching branches or creating the worktree.
7. Preserve unrelated dirt and inspect staged files before commits.
8. Commit approved plan/spec first if not committed yet.
   - If the plan/spec are untracked or dirty in the current checkout and the
     default separate-worktree path will be used, commit them before creating
     the worktree.
   - If worktree setup has already happened, carry the plan/spec into the task
     branch and commit them before implementation work.
   - Stage only the plan and its paired spec for this commit; keep scratchpads,
     unrelated draft docs, and unrelated dirt out.
9. Execute through the chosen mode.
10. If a branch/worktree was used, finish with `git merge --no-ff` and cleanup
   unless told otherwise.
