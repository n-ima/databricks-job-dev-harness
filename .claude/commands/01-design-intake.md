<!-- GENERATED FILE。編集しないでください。
     生成元: .github/prompts/01-design-intake.prompt.md, .github/agents/design-gate.agent.md
     再生成: uv run task gen-tooling -->

---
description: 承認済み設計書をdocs/01-design/へ配置・索引登録し、environment.md（環境・自動化境界）をヒアリングして埋める
allowed-tools: Read, Edit, Write, Grep, Glob, Task
---

このコマンドは薄いアダプタです。振る舞いの正は参照先にあります。

1. `.github/agents/design-gate.agent.md` を読み、その役割定義に従ってこの会話のロールを設定してください。
2. その上で `.github/prompts/01-design-intake.prompt.md` の本文の指示を実行してください。
3. 役割定義の中の `runSubagent` は、Claude Code では **Task ツール**で
   `.claude/agents/` の同名サブエージェント（design-critic / task-worker / reviewer）を
   呼ぶことに読み替えてください。ハンドオフボタンは存在しないため、フェーズ移行の案内は
   「新しいセッションで /<コマンド名> を実行」の形にしてください。
