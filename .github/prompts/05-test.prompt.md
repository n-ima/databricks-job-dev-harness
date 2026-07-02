---
agent: test
description: 'テスト計画作成→単体テスト→ビルド→bundle validate→devデプロイ→実Job実行→結合テスト→独立レビューまでを自動実行する'
---

前提: `docs/02-implementation/tasks.md` の全タスクが完了していること。

testエージェントの手順で進める。

1. `test_plan_template.md` から `test-plan.md` を作成する（設計ID・受け入れ条件との対応づけ）。
2. 段階実行: `uv run task check` → `uv run task build` →
   `databricks bundle validate -t dev` → `bundle deploy -t dev` →
   `bundle run <job_key> -t dev` → `uv run task integration` →
   （受け入れ条件にあれば）再実行による冪等性の実証。前段が失敗したら先に進まない。
3. 失敗は自分で切り分け、実装バグは実装エージェントへの自動差し戻しで回す。
   仕様判断が必要な場合のみ人に確認する。
4. `test-report.md` に実行コマンド・run ID・実測値をまとめる。
5. 最後に `runSubagent` で `reviewer` を1回呼び出し、結果を
   `security-review-report.md` と `test-report.md` に記録してから、
   問題なしならリリースフェーズへのハンドオフを自動送信する。
