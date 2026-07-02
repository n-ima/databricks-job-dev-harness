---
agent: orchestrator
description: 'プロジェクトの進捗を確認し、次に進むべきフェーズを提案する（初回はprogress.md/learnings.mdを作成する）'
---

1. `docs/00-overview/progress.md` が無ければ `progress_template.md` から、
   `learnings.md` が無ければ `learnings_template.md` から作成する。
2. `docs/01-design/` 〜 `docs/04-release/` の成果物と `GATE_STATUS` を
   `gate-check` スキルの判定ロジックで突き合わせ、フェーズ状況を表で提示する。
   IRRの判定値（GO/CONDITIONAL GO/NO-GO/未判定）を必ず明示する。
3. 次に進むべきフェーズを1つだけ推奨し、対応するハンドオフボタンを案内する。
   初回（何も無い状態）なら「承認済み設計書を用意して `/01-design-intake`」を案内する。
