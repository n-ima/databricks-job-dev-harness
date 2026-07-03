---
agent: orchestrator
description: '現在のフェーズゲート状況(GATE_STATUS)とIRR判定を表で表示し、次の一手を提案する'
---

1. `docs/00-overview/progress.md` の `GATE_STATUS` と各フェーズの成果物の実態を
   `gate-check` スキルで突き合わせ、状況を表で提示する。
2. `docs/01-design/irr.md` があれば判定値と未解決条件（期限つき）を表示する。
3. 実態とGATE_STATUSがずれていれば指摘する（`done` への変更は人の承認が必要）。
4. 次に進むべきフェーズを1つだけ推奨する。
5. ユーザーが「整合チェック」「監査」を求めた場合は、`gate-check` スキルの
   「横断整合監査」を実行し、設計索引↔IRR↔tasks↔traceability↔実ファイル間の
   食い違いを表で報告する（修正はせず、修正が必要な入口を案内する）。
