# Idea

Determine whether the new `pontonier==0.6.0` PyPI dependency (which upstream
`briandconnelly/codex-in-claude`@`aeba3bc` substituted for the vendored `_core`
package) already contains equivalents of this fork's 5 merged WSL2/DrvFs fixes,
to inform a merge-strategy decision (rebase-and-drop vs. rebase-and-carry-forward).

## Artifact provenance

Every `briandconnelly/pontonier` citation below is pinned to commit
`81c96525c89d44dd0b9d612817703ffda8c91b35` — the commit the `v0.6.0` tag
dereferences to (verified via the GitHub API) — rather than the mutable `main`
branch, so the links stay valid even after `main` moves further. The per-file
blob `sha` recorded alongside each citation is the exact content that was
fetched and searched on 2026-08-21, independent of the link target.

The `pontonier==0.6.0` PyPI artifacts were verified against
`https://pypi.org/pypi/pontonier/0.6.0/json`:

- sdist `pontonier-0.6.0.tar.gz` — sha256
  `c5a7359846162d4a0bc167a486c63e3685a0bb128c0f95565a34d8c5954607b0`
- wheel `pontonier-0.6.0-py3-none-any.whl` — sha256
  `2b29a6459e719d6f714e56315fe53f30edacbfe61aaab5279153d938370d6db2`

## Requirements

A fix counts as "already covered" only if pontonier's public source contains
functionally equivalent logic — not just a file of the same name. Specifically,
for each of the 5 local fixes:

1. `_core/gitdiff.py` — WSL/path handling in the diff engine (gitdir translation
   awareness, path handling under WSL).
2. `_core/worktree.py` — translation of a Windows-style linked-worktree `gitdir`
   pointer for WSL git calls, and refusal to write a WSL-shaped pointer into a
   Windows-created worktree.
3. `_core/wslpath.py` — dedicated WSL path-translation helper module (new file).
4. `_core/workspace.py` — translation of WSL2 drive-letter roots / `workspace_root`
   to `/mnt/<drive>/...`.
5. `_core/binresolve.py` — resolution of the `codex` binary to a WSL-native
   install (ordered candidate probes: `~/.local/bin`, `/usr/local/bin`, `npm bin -g`,
   `shutil.which`) rather than a Windows-native shim.

A candidate module fails to cover a requirement if it contains no WSL/DrvFs/
Windows-path-specific logic at all (i.e., is functionally identical to this
project's pre-fix, unpatched version of the same file).

## Search axes used

- **Direct source lookup** — the PyPI package name "pontonier" and its GitHub
  source repo (`briandconnelly/pontonier`), read directly file-by-file.
- **Problem-shape synonyms** — searched every file in pontonier's `core/` and
  `backend/` modules for `wsl`, `WSL`, `drvfs`, `DrvFs`, `/mnt/[a-z]`,
  `windows`/`Windows`, `gitdir`, `drive.letter` (via `-o` occurrence-mode grep,
  not just line-mode, since the GitHub API returns file content as a single
  JSON-escaped line), each paired with a positive control (a term known to be
  present) to confirm the fetched dump was actually readable/searchable. This
  pattern is case-sensitive except where explicit alternation covers both
  cases (e.g. `windows|Windows`); the all-caps identifier `_WINDOWS_DRIVE_RE`
  (present in `gitdiff.py`) was missed on the first pass as a result and was
  only found via direct source inspection — see Finding 1's case-sensitivity
  caveat.
- **Vendor-specific phrasing** — the commit message's own framing ("extracted
  from this code via moonbridge's fork, which carried the superset fixes") was
  checked directly against pontonier's `CHANGELOG.md`, which enumerates exactly
  what the `0.1.0` "core extraction" milestone carried over.
- **Issue tracker** — searched `briandconnelly/pontonier` issues/PRs for
  `wsl`, `drvfs`, `windows` to check whether the gap is tracked but unmerged.
- **Negative axis** — GitHub's hosted code search (`search_code`) was tried
  first but returned zero results even for strings known to exist in the repo
  (e.g. `resolve_workspace`), indicating the repo is too new to be indexed;
  discarded in favor of direct file fetches + local grep, which is what the
  findings below rely on.

## Findings (per fix)

### 1. `gitdiff.py` — WSL/path handling in diff engine

**Absent.** Fetched `src/pontonier/core/gitdiff.py` (60,641 bytes) in full and
grepped for `wsl|WSL|drvfs|DrvFs|/mnt/[a-z]|windows|Windows|gitdir` with
occurrence-mode matching: zero hits. Positive control run against the same
saved dump (`def |redact|diff --git`, occurrence-mode) returned dozens of hits,
confirming the dump is fully readable/searchable and the zero-hit WSL result is
not an artifact of a truncated or unreadable fetch.
https://github.com/briandconnelly/pontonier/blob/81c96525c89d44dd0b9d612817703ffda8c91b35/src/pontonier/core/gitdiff.py
(fetched 2026-08-21, file `sha` `9cd203189a60760333a34ab2b8903dc1636e41b8`).

By contrast, this fork's `src/codex_in_claude/_core/gitdiff.py` imports
`wslpath` directly (`from codex_in_claude._core import gitproc, streamcap, wslpath`)
and calls `wslpath.git_dir_override(cwd)` inside `_base_git_env` (fork line ~358)
to build `GIT_DIR`/`GIT_WORK_TREE` overrides for a Windows-created worktree. None
of that exists in pontonier's copy.

**Case-sensitivity caveat:** pontonier's `src/pontonier/core/gitdiff.py` does
contain `_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")` (line 32), used inside
`normalize_paths()` (line 153) to reject non-repo-relative `git diff` pathspec
filter arguments (i.e., arguments starting with `/` or a drive letter) supplied
by the caller. This identifier was missed by the case-sensitive grep pattern
used in the initial pass (see Search axes used) because `windows|Windows` does
not match the all-caps `_WINDOWS_DRIVE_RE`. Having found it via direct source
inspection, it serves generic pathspec-filter validation, not gitdir-pointer
translation or any equivalent of this fork's WSL2/DrvFs handling — so it does
not change the **Absent** verdict for the actual capability being audited here
(diff-engine WSL/path handling).

### 2. `worktree.py` — Windows-style linked-worktree `gitdir` pointer translation

**Absent.** Fetched `src/pontonier/core/worktree.py` (55,753 bytes) in full and
grepped for the same keyword set: zero hits, including `gitdir` itself (a term
that would appear even in ordinary, non-WSL worktree-pointer handling).
https://github.com/briandconnelly/pontonier/blob/81c96525c89d44dd0b9d612817703ffda8c91b35/src/pontonier/core/worktree.py
(fetched 2026-08-21, `sha` `c26df6d96cede4bfc58fdef7b0b7398162d27537`).

This fork's `_core/worktree.py` imports `wslpath` and calls
`wslpath.linked_worktree_gitdir_from_ancestors(repo)` (fork line ~305) as the
write-path refusal guard, refusing to write a WSL-shaped gitdir pointer into a
Windows-created worktree, plus a dedicated docstring/comment block explaining the
WSL gitdir-pointer translation (fork issue #4). None of this is present upstream.

### 3. `wslpath.py` — dedicated WSL path-translation module

**Absent — module does not exist.** `src/pontonier/core/`'s directory listing
contains exactly 11 files: `__init__.py`, `gitdiff.py`, `gitproc.py`,
`idempotency.py`, `jobs.py`, `jsoncache.py`, `redaction.py`, `runtime.py`,
`streamcap.py`, `workspace.py`, `worktree.py`. There is no `wslpath.py`
anywhere in the package (`src/pontonier/{core,backend,conventions,testing}`).
https://github.com/briandconnelly/pontonier/tree/81c96525c89d44dd0b9d612817703ffda8c91b35/src/pontonier/core
(fetched 2026-08-21).

### 4. `workspace.py` — WSL2 drive-letter root / `workspace_root` translation

**Absent.** Fetched `src/pontonier/core/workspace.py` in full (2,157 bytes —
notably smaller than this fork's patched version). It contains only
`WorkspaceResolution`, `_is_within`, `resolve_workspace`, and `server_cwd` — no
`normalize_wsl_drive_path` function and no drive-letter handling anywhere in
`resolve_workspace`'s `explicit` branch.
https://github.com/briandconnelly/pontonier/blob/81c96525c89d44dd0b9d612817703ffda8c91b35/src/pontonier/core/workspace.py
(fetched 2026-08-21, `sha` `e3408da34719af0c56aa8810d2ff9a90d0a60f9c`).

This fork's `_core/workspace.py` adds a `normalize_wsl_drive_path(path)` function
(translates `/<drive>:/...`-shaped decoded URIs to `/mnt/<drive>/...`) and calls it
on the `explicit` workspace-root candidate before resolving it. Pontonier's
`resolve_workspace` passes `explicit` straight to `Path(explicit)` unmodified.

### 5. `binresolve.py` — WSL-native `codex` binary resolution

**Absent — module does not exist, and no equivalent logic found elsewhere in
the published package.** No `binresolve.py` in `core/`. Also checked
`src/pontonier/backend/` (`classify.py`, `contract.py`, `protocol.py`), the
only other layer in this repo that references CLI-binary identity: it carries
`bin_name: str` as a static `BackendContract` field
(`src/pontonier/backend/contract.py`), but `PreparedRun.argv` (the staged
invocation, `src/pontonier/backend/protocol.py`) is constructed by each
backend's `AgentBackend.prepare()` implementation, and no such implementation
is present in this repo — `pontonier.backend` ships only the protocol/contract/
classifier, not adapters. `core/runtime.py`'s `run_async`/`run_sync_capture`
spawn `argv[0]` via `subprocess.Popen`/`subprocess.run` directly, relying on
the OS `PATH`; `runtime.py` contains no ordered-candidate-probe fallback logic
(no reference to `~/.local/bin`, `/usr/local/bin`, or `npm bin -g` anywhere in
the file).
https://github.com/briandconnelly/pontonier/blob/81c96525c89d44dd0b9d612817703ffda8c91b35/src/pontonier/core/runtime.py
(fetched 2026-08-21, `sha` `54b129b43981e5ffd2c8674bfed6acb29c040e30`);
https://github.com/briandconnelly/pontonier/blob/81c96525c89d44dd0b9d612817703ffda8c91b35/src/pontonier/backend/protocol.py
(fetched 2026-08-21, `sha` `ddff644ed38b460a1a30ea8a4c4e7e850878fc56`).

`src/pontonier/core/__init__.py` states the module is "CLI-agnostic" and
"never imports from the rest of the ... package" — a fact about how `core` is
scoped, offered here as context for why a Codex-specific resolver would be an
unusual fit for that module, not as a claim about where this fork's
`binresolve.py` logic should go.

`pontonier.conventions/` was also checked (specifically `preflight.py`, 100
lines): it contains zero WSL/DrvFs/Windows/drive-letter references, and it
does a functionally different thing anyway (CLI `--help` feature-flag
detection, not binary-path resolution), so the **Absent** verdict for binary
resolution stands.

## Corroborating evidence: pontonier's own changelog

`CHANGELOG.md`'s `0.1.0 (milestone M0 — core extraction)` entry states exactly
what was carried over from "moonbridge's `_core`": *"jobs, worktree, gitdiff,
redaction, runtime, gitproc, streamcap, idempotency, workspace, jsoncache,
carrying **the redaction trailing-newline fix and the orphan-process sweep**."*
https://github.com/briandconnelly/pontonier/blob/81c96525c89d44dd0b9d612817703ffda8c91b35/CHANGELOG.md
(fetched 2026-08-21, `sha` `b3f77ba7cd5d3b446e0ca48c48b17ef0d292ed94`).

Only two specific fixes are named as carried forward, and neither is WSL-related.
No changelog entry (0.1.0 through 0.6.0) mentions WSL, DrvFs, drive letters, or
Windows anywhere in its ~19KB text. This matches the direct source-code
findings: the upstream commit message's framing ("moonbridge's fork carried the
superset fixes") does not appear to include this fork's 5 WSL2/DrvFs fixes —
either moonbridge's fork never had them, or they were not part of what flowed
into pontonier's extraction.

## Issue tracker check

`mcp__github__search_issues` for `repo:briandconnelly/pontonier wsl OR drvfs OR
windows` returned 0 results (fetched 2026-08-21) — the gap is not tracked as a
known/pending item in pontonier's issue tracker either.

## Summary table

| # | Fork fix | File(s) | Pontonier status |
|---|---|---|---|
| 1 | Diff-engine WSL/path handling | `gitdiff.py` | **Absent** — no gitdir-pointer or WSL translation logic; the one drive-letter regex present (`_WINDOWS_DRIVE_RE`) validates `git diff` pathspec filters only (see caveat) |
| 2 | Linked-worktree gitdir pointer translation | `worktree.py` | **Absent** — no wsl/gitdir/drive references in full file text |
| 3 | WSL path-translation helpers | `wslpath.py` | **Absent** — module does not exist in the package |
| 4 | Workspace root drive-letter translation | `workspace.py` | **Absent** — `resolve_workspace` has no `normalize_wsl_drive_path` equivalent; file is materially smaller than the patched fork version |
| 5 | WSL-native `codex` binary resolution | `binresolve.py` | **Absent** — no module, and `core/runtime.py` spawns `argv[0]` via bare PATH lookup with no candidate-probe fallback; CLI-specific binary resolution is architecturally pushed into bridge-side adapters pontonier does not publish |

## No prior art found

- **All 5 fixes** — searched pontonier's full `core/` module source (all 11
  files: `__init__.py`, `gitdiff.py`, `gitproc.py`, `idempotency.py`,
  `jobs.py`, `jsoncache.py`, `redaction.py`, `runtime.py`, `streamcap.py`,
  `workspace.py`, `worktree.py`), its `backend/` module (all 4 files), its
  `CHANGELOG.md`, and its issue tracker. Every file was fetched in full and
  searched with occurrence-mode (not line-mode) grep for
  `wsl|WSL|drvfs|DrvFs|/mnt/[a-z]|windows|Windows|gitdir|drive.letter`: zero
  hits in every file except the one case-sensitivity gap noted in Finding 1's
  caveat (`_WINDOWS_DRIVE_RE`, which does not change that finding's verdict).
  Positive controls (grepping the same saved dumps for
  terms known to be present, e.g. "def ", "class ", `redact`, `worktree`)
  confirmed each dump was fully readable and searchable, so the zero-hit
  results are not artifacts of a truncated fetch. No equivalent WSL2/DrvFs
  handling was found anywhere in the publicly available
  `briandconnelly/pontonier` source as of commit
  `81c96525c89d44dd0b9d612817703ffda8c91b35` (the `v0.6.0` tag; repo created
  2026-08-16, most recent push 2026-08-20T16:23:22Z). The changelog
  independently corroborates this by naming exactly what *was* carried
  forward from the `_core` extraction ("the redaction trailing-newline fix
  and the orphan-process sweep") and omitting WSL entirely across all six
  changelog versions (0.1.0–0.6.0).

## Recommended handoff

- **User** — this is a merge-strategy decision the report was explicitly
  scoped not to make. The finding is: switching to `pontonier==0.6.0` as
  upstream did would silently drop all 5 WSL2/DrvFs fixes (they are not
  superseded, they are simply absent), so adopting the dependency as-is
  would regress WSL2/DrvFs-checkout support unless the fixes are carried
  forward some other way (e.g. re-applied downstream in the bridge's own
  code, or upstreamed into `pontonier` itself as a follow-up PR).
- **project-planner** — if the user decides to adopt `pontonier` while
  preserving WSL2 support, planning should scope how to carry each of the 5
  fixes forward, using this report's per-fix findings (which module owns each
  piece of missing logic today, and what pontonier's current module
  boundaries look like) as input.

## Open questions

- Whether `moonbridge`'s own fork (named in the upstream commit message as
  the source of "the superset fixes") independently carries these 5 WSL
  fixes was not checked — this task scoped the check to `pontonier`'s public
  source specifically. If moonbridge's fork is itself public, a follow-up
  check there could clarify whether the fixes were dropped during
  moonbridge's extraction or never existed in that lineage at all.
- Whether upstream `briandconnelly/codex-in-claude` retained any bridge-local
  (non-`_core`) WSL handling after adopting `pontonier==0.6.0` was not
  checked — this task scoped strictly to `pontonier`'s own module content, not
  upstream's post-migration bridge code.
