# .claude/ — Claude Code向け設定（自動生成）

このディレクトリの中身は `.github/agents/`, `.github/prompts/`, `.github/skills/`,
`.github/hooks/` から `scripts/generate_agent_tooling.py` によって自動生成される。
**直接編集しない。** 編集は `.github/` 側で行い、以下を再実行すること。

```bash
uv run task gen-tooling         # 生成
uv run task gen-tooling-check   # 生成結果と現状が一致しているか検査(CIで実行)
```

| ファイル/ディレクトリ | 生成元 | 役割 |
|---|---|---|
| `agents/*.md` | `.github/agents/{design-critic,task-worker,reviewer}.agent.md` | Claude Codeのサブエージェント（`Task`ツールで自動的に呼び出される） |
| `commands/*.md` | `.github/prompts/*.prompt.md` + 対応する `.github/agents/*.agent.md` | スラッシュコマンド。実行するとそのフェーズのエージェント人格を引き継ぐ |
| `skills/*/SKILL.md` | `.github/skills/*/SKILL.md` | Agent Skills（GitHub Copilotと同一のオープン標準。コピーそのまま） |
| `settings.json` | `.github/hooks/*.json` + `scripts/` | Hooks（ゲート・本番保護）+ 補助的なpermissions.deny |

個人用の上書きは `.claude/settings.local.json`（gitignore対象）に置く。
