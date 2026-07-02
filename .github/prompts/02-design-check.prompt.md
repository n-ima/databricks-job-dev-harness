---
agent: design-gate
description: '登録済み設計書の品質チェック（design-critic独立レビュー）と実装準備レビュー(IRR)を実行し、GO/CONDITIONAL GO/NO-GOを判定する'
---

前提: `docs/01-design/design-index.md` と `environment.md` が作成済みであること。
未作成なら先に `/01-design-intake` を案内する。

design-gateエージェントの「フェーズ2: 設計書チェック」の手順で進める。

1. 索引の形式チェック（全行登録済み・版・承認日・正本が一意）。
2. `runSubagent` で `design-critic` を1回呼び出し、設計書の品質を独立レビューさせる。
   BLOCKER/MAJORの指摘はIRRの未解決事項へ転記する。
3. `docs/01-design/irr_template.md` から `irr.md` を作成し、
   `design-readiness-review` スキルの手順で必須チェックを1項目ずつ確認する。
4. `GO` / `CONDITIONAL GO` / `NO-GO` を判定し、根拠・blocker・条件・
   最初に実装すべき小さな単位を提示して人の承認を求める。
5. 承認されたら `GATE_STATUS` の `design_check` を更新し、実装フェーズへの
   ハンドオフを提示する。`NO-GO` なら設計工程へ返す不足リストを整理して終了する。
