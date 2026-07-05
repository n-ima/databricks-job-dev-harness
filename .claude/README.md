# .claude/ — Claude Code向け薄いアダプタ（自動生成）

このディレクトリの中身は `.github/agents/`, `.github/prompts/`, `.github/skills/`,
`.github/hooks/` から `scripts/generate_agent_tooling.py` によって自動生成される。
**直接編集しない。** 編集は `.github/` 側で行うこと。

frontmatter（name/description/tools等）は生成時に転写されるため、これらを
変更した場合は再生成が必要。**本文は正典への参照ポインタのみ**（「`.github/agents/...`を
読んで従え」という指示）なので、本文（手順・ペルソナの中身）を変更しただけなら
再生成しなくても常に最新が実行時に読まれる。ただしSkill/Promptの**追加・削除**は
対応するポインタファイルの生成/削除が要るため、いずれの変更後も次を実行しておくと安全。

```bash
uv run task gen-tooling         # 生成
uv run task gen-tooling-check   # 生成結果と現状が一致しているか検査(CIで実行)
```

| ファイル/ディレクトリ | 生成元 | 役割 |
|---|---|---|
| `agents/*.md` | `.github/agents/{design-critic,task-worker,reviewer}.agent.md` | Claude Codeのサブエージェント（`Task`ツールで自動的に呼び出される。薄いポインタ） |
| `commands/*.md` | `.github/prompts/*.prompt.md` + 対応する `.github/agents/*.agent.md` | スラッシュコマンド（薄いポインタ。実行時に生成元を読みに行く） |
| `skills/*/SKILL.md` | `.github/skills/*/SKILL.md` | Agent Skills（GitHub Copilotと同一のオープン標準。frontmatterのみ転写、本文は薄いポインタ） |
| `settings.json` | `.github/hooks/*.json` + `scripts/` | Hooks（ゲート・本番保護）+ 補助的なpermissions.deny |

個人用の上書きは `.claude/settings.local.json`（gitignore対象）に置く。
