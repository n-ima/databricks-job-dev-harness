<!-- GENERATED FILE。編集しないでください。
     生成元: .github/prompts/08-design-revise.prompt.md, .github/agents/design-gate.agent.md
     再生成: uv run task gen-tooling -->

---
description: バグ・機能追加・仕様変更の内容から設計書をディスカッションして改訂する（初回の下書き設計書を対話で仕上げる用途にも使う）。合意した変更を設計書と索引に反映し、差分チェックへつなぐ
---

このワークフローは薄いアダプタです。振る舞いの正は参照先にあります。

1. `.github/agents/design-gate.agent.md` を読み、その役割定義に従って振る舞ってください。
2. その上で `.github/prompts/08-design-revise.prompt.md` の本文の指示を実行してください。
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
