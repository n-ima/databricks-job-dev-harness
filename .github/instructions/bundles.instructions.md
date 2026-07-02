---
applyTo: "databricks.yml,resources/**/*.yml"
---

# Databricks Bundle固有ルール

- リソース定義は宣言的にし、`resources/` 配下へ1リソース1ファイルで分割する。
- 環境固有値（catalog/schema/通知先/service principal等）は変数化する。直書き禁止。
- production系ターゲットには承認済みservice principal、tag、通知、timeout、
  上限付きretryを必ず設定する。
- timezone・pause状態・SLA・同時実行・backfill方針がIRRで承認される前に
  scheduleを追加しない。
- Runtime・node type・serverless・policy・autoscalingを推測で選ばず、IRRの決定を使う。
- `permissions` の拡大・`data_security_mode` の変更には、設計IDで説明できる
  業務上の理由と明示的なレビューを必要とする。
- このファイル群の変更はJob定義の変更そのもの。関連する設計IDを必ずコミット・PRに記す。
