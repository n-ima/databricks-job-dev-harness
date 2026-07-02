# リリースチェックリスト

手順は `.github/skills/databricks-deploy/SKILL.md` を参照。
productionの承認は必ず人が行う（AIは自己承認しない）。

## 対象

| 項目 | 内容 |
|---|---|
| バージョン / タグ | TODO |
| 対象コミット | TODO（SHA。stagingで検証した同一コミットをprodへ出す） |
| 変更内容の要約（設計ID） | TODO |
| データ影響 / 運用影響 | TODO |

## 前提確認

- [ ] `docs/03-test/test-report.md` が合格（独立レビュー「問題なし」含む）
- [ ] IRRの `CONDITIONAL GO` 条件がすべて解消済み
- [ ] CI（format/lint/型/テスト/build/bundle validate）が対象コミットで成功
- [ ] シークレット・設定値の確認（`environment.md` の保管先に存在すること）
- [ ] 変更可能時間帯の確認

## staging検証

| 項目 | 内容 |
|---|---|
| デプロイ日時 / 実施者 | TODO |
| `bundle deploy -t staging` 結果 | TODO |
| Job run ID / 実行時間 | TODO |
| 結合・データ品質・冪等性テスト結果 | TODO（数値化した閾値との比較） |
| 既知事項 | TODO / 該当なし |

## production承認・デプロイ

| 項目 | 内容 |
|---|---|
| 承認者（人） | TODO |
| 承認日時 | TODO |
| `bundle deploy -t prod` 結果 | TODO |
| `bundle summary -t prod` での設定確認 | TODO |
| 初回実行 run ID / 監視結果 | TODO |

## rollback手順

- コード・Job定義のみ: 最後の正常コミット（TODO: SHA）をprodへ再デプロイ
- データ変更を伴う場合: `runbook.md` の復旧手順（TODO: 該当セクション）
- 判断基準: TODO（どの閾値を割ったらrollbackするか）
