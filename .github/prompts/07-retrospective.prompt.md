---
agent: orchestrator
description: 'リリース後の振り返り。摩擦をハーネス改善/プロジェクト固有/一過性に分類し、ハーネス本体への改善提案表を作る'
---

`.github/skills/harness-retrospective/SKILL.md` の手順で進める。

1. `docs/00-overview/learnings.md`・各フェーズの成果物・会話で摩擦のあった出来事を集める。
2. 「ハーネス改善 / プロジェクト固有 / 一過性」に分類する。
3. ハーネス改善分は、対象ファイル・問題・提案・根拠の4点セットの改善提案表にまとめ、
   `docs/05-retrospective/retrospective_template.md` から `retrospective.md` を作成する。
4. 改善提案はハーネス本体リポジトリへ人間が適用し、DECISIONS.mdに記録することを案内する
   （ハーネス設定はエージェントの自動編集が禁止されている）。
