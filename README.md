# Azat Codex Plugins

Small Codex plugins and standalone skills.

## Extensions

| Extension | Type | Purpose |
| --- | --- | --- |
| `codex-cli-auto-title` | Plugin | Name a new Codex CLI thread after its first response. |
| `my-plan-executor` | Skill | Execute an approved implementation plan with repository-native safeguards. |

## Install

Add the marketplace once:

```bash
codex plugin marketplace add AzatSul23/azat-codex-plugins --ref main
```

Install the hook-based plugin:

```bash
codex plugin add codex-cli-auto-title@azat
```

Install the standalone skill globally for Codex:

```bash
npx skills add AzatSul23/azat-codex-plugins \
  --skill my-plan-executor \
  --agent codex \
  --global \
  --yes
```

## Codex CLI Auto Title

`codex-cli-auto-title` gives a new, unnamed Codex CLI thread a concise title after its first completed response. It runs as a synchronous `Stop` hook and uses an ephemeral `codex exec` process, so title generation uses the same Codex sign-in and subscription allowance as the parent CLI session.

The hook only generates a title when the stored thread:

- has no existing name;
- contains exactly one user message; and
- contains text in that message.

Named, multi-prompt, empty, and image-only threads are left unchanged. A failure shows a short warning, never includes prompt text, and never blocks the original conversation.

### Requirements

- Codex CLI 0.144.1 or newer
- Python 3.9 or newer available as `python3` on macOS/Linux or through `py -3` on Windows
- An active Codex sign-in and subscription allowance; no API key is required

Version 0.1.0 is verified on macOS. Linux and Windows support is best-effort until tested on those platforms.

Start a new Codex CLI thread, open `/hooks`, and review and trust the plugin hook. Codex intentionally skips newly installed or changed non-managed hooks until their exact definition is trusted.

The title appears after the first response completes, not when the prompt is submitted. The title-generation subprocess can take up to 60 seconds.

### Update

```bash
codex plugin marketplace upgrade azat
codex plugin add codex-cli-auto-title@azat
```

Review `/hooks` again if Codex reports that the updated hook definition needs trust, then test in a new thread.

### Remove

```bash
codex plugin remove codex-cli-auto-title@azat
```

To remove the marketplace too:

```bash
codex plugin marketplace remove azat
```

### How it works

The hook reads the completed thread through the read-only `thread/read` app-server method. For one eligible text prompt it runs:

```text
codex exec --ephemeral --ignore-user-config \
  --skip-git-repo-check --sandbox read-only \
  --output-last-message <temporary-file> -
```

The nested process receives `CODEX_AUTO_TITLE_CHILD=1` to prevent recursive title generation. Its first non-empty output line is normalized, stripped of wrapping quotes and a trailing period, and capped at seven words and 80 characters before `thread/name/set` stores it. The ephemeral run leaves no title-generation thread behind.

The plugin does not require npm, `npx`, PyPI packages, third-party Python modules, direct SQLite writes, or edits to Codex session index files.

### Troubleshooting

If a title stays as a UUID:

1. Confirm `codex --version` is at least 0.144.1.
2. Run `codex plugin list` and confirm `codex-cli-auto-title@azat` is installed and enabled.
3. Open `/hooks` and trust the current hook definition.
4. Test in a new unnamed thread with one text prompt; an existing name, a second prompt, or an image-only prompt is intentionally skipped.
5. Confirm the signed-in Codex account has allowance available for the extra ephemeral title-generation run.

For vetted non-interactive automation only, Codex provides `--dangerously-bypass-hook-trust`; normal interactive use should review the hook in `/hooks` instead.

## My Plan Executor

`my-plan-executor` runs an explicitly invoked saved implementation plan. It
reads repository instructions plus the paired spec, keeps implementation and
workspace choices independent, and defaults to subagent-driven execution in a
separate worktree.

Invoke it with a saved plan:

```text
$my-plan-executor docs/superpowers/plans/example.md
```

The skill is explicit-only: installing it does not make Codex execute plans
implicitly.

### Update

```bash
npx skills update my-plan-executor --global
```

### Remove

```bash
npx skills remove my-plan-executor --agent codex --global --yes
```

## Development

Run the standard-library test suite:

```bash
python3 -m unittest discover -s plugins/codex-cli-auto-title/tests -v
```

Validate the package and JSON files:

```bash
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" \
  plugins/codex-cli-auto-title
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  skills/my-plan-executor
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/codex-cli-auto-title/hooks/hooks.json >/dev/null
```

## License

MIT
