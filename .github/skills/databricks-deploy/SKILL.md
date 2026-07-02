---
name: databricks-deploy
description: Databricks Asset Bundlesによるdev/staging/prodへのデプロイ手順とコマンド、CI/CD(GitHub Actions+OIDC)構成、rollback手順。デプロイ・リリース作業時に使う。
---

# Databricksデプロイスキル

## ターゲットと自動化境界

| ターゲット | mode | 実行identity | エージェントの操作 |
|---|---|---|---|
| dev | development | 開発者本人 | deploy/run とも自動でよい（確認不要） |
| staging | production | service principal | **Hooksでask確認**。テスト証跡を残す |
| prod | production | service principal | **必ず人の承認**。AIは自己承認しない |

`docs/01-design/environment.md` の自動化境界が上記より狭い場合はそちらが優先。

## 基本コマンド

```bash
databricks bundle validate -t <target>            # 構文・参照整合の検証
databricks bundle deploy -t <target>              # デプロイ（wheelビルド込み）
databricks bundle run <job_key> -t <target>       # Job実行（終了まで待ち、結果を返す）
databricks bundle summary -t <target>             # デプロイ済みリソースの確認
databricks bundle open -t <target>                # ブラウザでリソースを開く（人向け）
```

- 認証は `databricks auth login --host <workspace-url>` で作成したプロファイルを使う。
  プロファイル指定が必要な環境では `--profile <name>` を付ける。PATの直書きはしない。
- `bundle run` の出力からJob run IDを控え、証跡（test-report / release-checklist）に記録する。

## リリースの流れ（release エージェント用）

1. 対象コミットのCI成功・独立レビュー完了・IRR条件解消を確認する。
2. stagingへdeployし、対象Jobを実行、結合/データ品質/冪等性テストを行う。
   commit SHA・target・run ID・実行時間・結果を記録する。
3. 数値化された受け入れ閾値と比較する。
4. **人のproduction承認を待つ。** GitHub Actionsを使う場合は `production` Environmentの
   required reviewersが正式ゲート。
5. **stagingで検証した同一コミット** をprodへdeployする（新しいコミットを直接prodへ
   出さない）。
6. `bundle summary -t prod` で設定を確認し、最初のproduction実行を監視する。

## CI/CD（GitHub Actionsを使う場合の要点）

- 認証はservice principal + Workload Identity Federation（OIDC）。長期PATを
  Secretsに置かない。
- PR: `uv run task check` + `uv run task build` + `bundle validate`。
- mainへのmerge: stagingへ自動deploy + 結合テスト。
- production: Environment承認後に同一SHAをdeploy。
- workflowファイルはエージェントが自動編集しない（`.vscode/settings.json` でも保護）。

## rollback / roll-forward

- **コード・Job定義のみの問題**: 最後の正常コミットをcheckoutして
  `bundle deploy -t prod` で再デプロイする（Bundlesは宣言的なので状態が収束する）。
- **破壊的なデータ変更を伴う場合**: コードのrollbackだけではデータは戻らない。
  設計済みの復旧手順（`docs/04-release/runbook.md`）に従う。
- 実行中の異常で影響拡大が見込まれる場合はJobを停止し、Runbookに従って通知する。
- 緊急修正でもPR・テスト・承認・記録を省略しない。

## 禁止事項

- `databricks bundle destroy` の自発的な実行（人の明示指示 + Hooks確認が必須）。
- UI（ワークスペース画面）でのJob定義・権限・スケジュールの恒久変更。
- stagingを経ずにprodへデプロイすること。
