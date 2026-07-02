---
agent: release
description: 'リリースチェックリスト作成→staging検証→人のproduction承認→productionデプロイ→初回実行監視を進める'
---

前提: `docs/03-test/test-report.md` が完成し、独立レビューが「問題なし」であること。

releaseエージェントの手順で進める。

1. `environment.md` のstaging/prod設定・承認者・変更可能時間帯・自動化境界を確認する。
2. IRRの `CONDITIONAL GO` 条件が解消済みであることを確認する（未解消なら止まる）。
3. `release-checklist.md`・`runbook.md`（初回のみ）を作成し、`CHANGELOG.md` に追記する。
4. stagingへデプロイして検証し、証跡（commit SHA / target / run ID / 結果）を記録する。
5. staging検証結果を要約して **productionデプロイの承認を人に求める**。
6. 承認後、同一コミットをproductionへデプロイし、`bundle summary` で設定を確認、
   初回実行を監視する。閾値未達なら停止してrollback/roll-forwardの判断材料を提示する。
7. 完了後、`/07-retrospective` の実施を提案する。
