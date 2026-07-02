## 目的・設計トレーサビリティ

- 設計ID:
- 受け入れ条件:
- IRR判定/未解決条件:
- タスク（docs/02-implementation/tasks.md）:

## 変更内容

- 

## 検証結果

- [ ] `uv run task check`（format/lint/型/単体テスト）
- [ ] `uv run task build`
- [ ] `databricks bundle validate -t dev`
- [ ] devでの実Job実行 + 結合テスト（run ID: ）
- [ ] 実装とは別セッションの `reviewer` 独立レビューを実施し、CRITICAL/HIGHを解消した
- [ ] `docs/02-implementation/traceability.md` を更新した

## 影響と安全性

- [ ] データ・schema・権限への影響を記載した
- [ ] secret、個人情報、実データを含まない
- [ ] 冪等性、retry、重複実行、部分失敗を確認した
- [ ] 性能・コストへの影響を確認した
- [ ] AI生成コードを人が理解しレビューした

## リリース・rollback

- staging確認項目:
- production監視:
- rollback/roll-forward:
