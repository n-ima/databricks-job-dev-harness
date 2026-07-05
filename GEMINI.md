# GEMINI.md — Antigravity固有の設定

Antigravityは `AGENTS.md` をプロジェクトルートから自動的に読み込む（追加設定不要）。
このファイルは、AGENTS.mdと矛盾しないAntigravity固有の運用ルール・注意点だけを補う
（GEMINI.mdはAGENTS.mdより優先されるため、ここには「Antigravityでの動き方の違い」
だけを書き、業務ルール自体は書かない）。

## フェーズエージェントの実行方法

このハーネスの各フェーズエージェント（orchestrator, design-gate, implement, test,
release）は、`.agent/workflows/*.md` としてワークフロー化してある
（`.github/prompts/` + `.github/agents/` から自動生成。編集は `.github/` 側で行い
`uv run task gen-tooling` を再実行する）。GitHub Copilotのハンドオフボタン・
Claude Codeのスラッシュコマンドに相当する。フェーズを進める際は、対応するワークフローを
新しいエージェントセッション（Manager Surface）で実行する。対応表はREADME.mdを参照。

## 独立レビュー（design-critic / task-worker / reviewer）の相当機能

Antigravityは2026年のGoogle I/OでSubagents機能が追加されたが、本ハーネス作成時点
（2026年7月）では設定ファイル形式が公式ドキュメントで確認できなかったため、
自動生成の対象にしていない。**代わりに、Manager Surfaceで新しい独立したエージェント
セッションを手動で開き、`.agent/workflows/` の該当ワークフロー本文（design-critic/
task-worker/reviewerの人格定義を含む）を渡して実行する運用とする。**
これにより「実装した本人とは別コンテキストでのレビュー」という目的そのものは達成できる
（自動呼び出しではなく手動のひと手間が必要な点が他ツールとの違い）。

Antigravity公式のSubagents/Hooks機能が安定・文書化された場合は、
`scripts/generate_agent_tooling.py` の対応を追加することを検討する
（追加前に公式ドキュメントで現行スキーマを必ず確認すること。DECISIONS.md参照）。

## 本番保護（Hooksの代替）

Antigravityには（本ハーネス作成時点で確認できた範囲では）GitHub Copilot/Claude Codeの
ような、コマンド内容を見てdeny/askを機械的に返すスクリプト式Hooksに相当する機能はない。
代わりにTerminal Permission Mode（Off/Manual/Auto）とsettings.jsonの許可リストで
保護する。**このハーネスでは "Off（許可リストのみ）" または "Manual（実行前に確認）"
を推奨する。** 特に以下のパターンは許可リストに入れない（`guard-databricks-prod.sh`
が防いでいるのと同じ操作）:

- `databricks bundle deploy -t staging` / `-t prod`
- `databricks bundle run ... -t staging` / `-t prod`
- `databricks bundle destroy`
- `git push` / `git tag` / `--force` / `reset --hard`

devターゲットへの操作（`-t dev`）は全自動区間の一部として許可リストに含めてよい。

## 要確認事項（このファイルの前提が古くなっていないか）

- Antigravity公式のSubagents/Hooks機能のスキーマは要確認（上記参照）。
- Terminal Permission Modeの名称・挙動はAntigravityのバージョンにより変わりうる。
  設定前に公式ドキュメント（antigravity.google/docs）で最新仕様を確認すること。
