<!-- GENERATED FILE。編集しないでください。
     生成元: .github/prompts/06-release.prompt.md, .github/agents/release.agent.md
     再生成: uv run task gen-tooling -->

---
description: リリースチェックリスト作成→staging検証→人のproduction承認→productionデプロイ→初回実行監視を進める
allowed-tools: Read, Edit, Write, Grep, Glob, Bash, WebFetch, WebSearch
---

このコマンドは薄いアダプタです。振る舞いの正は参照先にあります。

1. `.github/agents/release.agent.md` を読み、その役割定義に従ってこの会話のロールを設定してください。
2. その上で `.github/prompts/06-release.prompt.md` の本文の指示を実行してください。
3. 役割定義の中の `runSubagent` は、Claude Code では **Task ツール**で
   `.claude/agents/` の同名サブエージェント（design-critic / task-worker / reviewer）を
   呼ぶことに読み替えてください。ハンドオフボタンは存在しないため、フェーズ移行の案内は
   「新しいセッションで /<コマンド名> を実行」の形にしてください。
