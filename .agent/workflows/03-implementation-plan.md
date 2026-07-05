<!-- GENERATED FILE。編集しないでください。
     生成元: .github/prompts/03-implementation-plan.prompt.md, .github/agents/implement.agent.md
     再生成: uv run task gen-tooling -->

---
description: IRR承認済みの設計IDを1コミット粒度の実装タスクに分解し、tasks.mdとtraceability.mdを作成する
---

このワークフローは薄いアダプタです。振る舞いの正は参照先にあります。

1. `.github/agents/implement.agent.md` を読み、その役割定義に従って振る舞ってください。
2. その上で `.github/prompts/03-implementation-plan.prompt.md` の本文の指示を実行してください。
3. 役割定義の中の `runSubagent`（独立コンテキストでのレビュー・実装分離）は、
   Antigravity では **Agent Manager で別のエージェント会話として実行**し、
   結果を受け取って続行することに読み替えてください（同一会話で続ける場合は、
   独立性が失われることをユーザーに伝えたうえで行うこと）。
   ハンドオフボタンは存在しないため、フェーズ移行の案内は
   「新しいエージェント会話で /<ワークフロー名> を実行」の形にしてください。
4. フック（機械的ガードレール）はこの環境では発火しません（Antigravity IDEはプロジェクト内の
   スクリプトフックを読まない・姉妹プロジェクトの実機検証で確認済み）。AGENTS.md の指示レベルのルール
   （テンプレート直接編集の禁止・push/tag等の事前確認・シークレット非記載）を自分の判断で
   厳守してください。機械的な保護が必要な場合、ユーザーに Terminal Permission Mode / GUI Deny List
   への危険コマンド登録を案内してください（詳細は GEMINI.md）。
