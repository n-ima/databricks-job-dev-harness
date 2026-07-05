<!-- GENERATED FILE。編集しないでください。
     生成元: .github/prompts/00-start-project.prompt.md, .github/agents/orchestrator.agent.md
     再生成: uv run task gen-tooling -->

---
description: プロジェクトの進捗を確認し、次に進むべきフェーズを提案する（初回はprogress.md/learnings.mdを作成する）
allowed-tools: Read, Grep, Glob, Edit, Write, TodoWrite
---

このコマンドは薄いアダプタです。振る舞いの正は参照先にあります。

1. `.github/agents/orchestrator.agent.md` を読み、その役割定義に従ってこの会話のロールを設定してください。
2. その上で `.github/prompts/00-start-project.prompt.md` の本文の指示を実行してください。
3. 役割定義の中の `runSubagent` は、Claude Code では **Task ツール**で
   `.claude/agents/` の同名サブエージェント（design-critic / task-worker / reviewer）を
   呼ぶことに読み替えてください。ハンドオフボタンは存在しないため、フェーズ移行の案内は
   「新しいセッションで /<コマンド名> を実行」の形にしてください。
