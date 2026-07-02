---
agent: implement
description: 'IRR承認済みの設計IDを1コミット粒度の実装タスクに分解し、tasks.mdとtraceability.mdを作成する'
---

前提: `docs/01-design/irr.md` が `GO` / `CONDITIONAL GO` で承認済みであること。
未承認・`NO-GO` なら実装計画を作らず、設計書チェックへの差し戻しを案内する。

1. `design-index.md` の設計IDごとに、1コミットで完結する粒度のタスクへ分解し、
   `docs/02-implementation/tasks_template.md` から `tasks.md` を作成する
   （依存順・各タスクに設計ID/受け入れ条件IDを付与）。
   `CONDITIONAL GO` の未解決条件に依存するタスクは後回しの位置に置き、条件IDを明記する。
   プロジェクト名が `sample_job` のまま（environment.mdで案件名決定済み）なら、
   `databricks-env-setup` スキルのリネームチェックリストをT-000として先頭に置く。
2. `traceability_template.md` から `traceability.md` の骨格を作成する。
3. 計画を提示したら確認は求めず、そのまま `/04-implement-task` の実装ループへ進んでよい。
