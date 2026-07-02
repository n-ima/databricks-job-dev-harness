---
agent: implement
description: 'tasks.mdの未完了タスクを先頭から順に、task-workerサブエージェントへ1タスクずつ委譲して自動実装する'
---

前提: `docs/02-implementation/tasks.md` が存在すること。無ければ先に
`/03-implementation-plan` を実行する。

1. `tasks.md` の未完了タスクを先頭から特定する。
2. 1タスクにつき1回 `runSubagent` で `task-worker` を呼び出す。タスクID・設計ID・
   受け入れ条件IDを渡し、返答は要約のみ受け取る。
3. `tasks.md` / `traceability.md` の更新を確認し、次のタスクへ進む。
   タスクごとの着手確認・完了確認をユーザーに求めない（全自動区間）。
4. ブロッカー（設計だけでは判断できない事実が必要）だけは止まって人に確認する。
5. 全タスク完了後、テストフェーズへのハンドオフを自動送信する。
