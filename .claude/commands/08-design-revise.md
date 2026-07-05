<!-- GENERATED FILE。編集しないでください。
     生成元: .github/prompts/08-design-revise.prompt.md, .github/agents/design-gate.agent.md
     再生成: uv run task gen-tooling -->

---
description: バグ・機能追加・仕様変更の内容から設計書をディスカッションして改訂する（初回の下書き設計書を対話で仕上げる用途にも使う）。合意した変更を設計書と索引に反映し、差分チェックへつなぐ
allowed-tools: Read, Edit, Write, Grep, Glob, Task
---

このコマンドは薄いアダプタです。振る舞いの正は参照先にあります。

1. `.github/agents/design-gate.agent.md` を読み、その役割定義に従ってこの会話のロールを設定してください。
2. その上で `.github/prompts/08-design-revise.prompt.md` の本文の指示を実行してください。
3. 役割定義の中の `runSubagent` は、Claude Code では **Task ツール**で
   `.claude/agents/` の同名サブエージェント（design-critic / task-worker / reviewer）を
   呼ぶことに読み替えてください。ハンドオフボタンは存在しないため、フェーズ移行の案内は
   「新しいセッションで /<コマンド名> を実行」の形にしてください。
