# 環境情報・自動化境界（environment.md）

後工程の自動化はすべてこのファイルに依存する。**仮置き・TODOのまま先へ進めないこと。**
シークレットの値そのものは書かない（保管先への参照のみ）。

## 案件情報

| 項目 | 内容 |
|---|---|
| 案件名 | TODO |
| Bundle名（`databricks.yml` の `bundle.name`） | TODO |
| データ機密区分（AIへ送信禁止の情報区分を含む） | TODO |
| 案件責任者 / 運用責任者 | TODO |

## Databricksワークスペース

| 項目 | dev | staging | prod |
|---|---|---|---|
| ワークスペースURL | TODO | TODO | TODO |
| CLI認証プロファイル名 | dev | （CI/CDのみ） | （CI/CDのみ） |
| catalog | TODO | TODO | TODO |
| schema | TODO | TODO | TODO |
| 実行identity | 開発者本人 | service principal: TODO | service principal: TODO |
| compute方針（classic/serverless, policy） | TODO | TODO | TODO |

- 開発者IDにstaging/prodの書き込み権限を与えない（権限分離が最終ゲート）。
- staging/prodのデプロイ主体はCI/CD（service principal + OIDC）を標準とする。

## シークレット・接続情報の保管先

| 用途 | 保管先（値は書かない） |
|---|---|
| Job実行時に必要なシークレット | Databricks Secrets scope: TODO |
| CI/CD認証 | GitHub Environments/Secrets（OIDC推奨、長期PAT禁止） |

## 通知・監視

| 項目 | 内容 |
|---|---|
| 失敗通知先 | TODO（`databricks.yml` の `notification_email` 変数と一致させる） |
| 監視指標・ダッシュボード | TODO |
| 一次対応者 / エスカレーション先 | TODO |

## 自動化境界（エージェントが確認なしで実行してよい操作）

フェーズの既定（`AGENTS.md`）よりこの表の明示が優先される。

| 操作 | 分類（自動 / 確認 / 人手） | 備考 |
|---|---|---|
| ローカルのlint/型/単体テスト/ビルド | 自動 | |
| `databricks bundle validate -t dev` | 自動 | |
| `databricks bundle deploy -t dev` | 自動 | 既定。人手にしたい場合はここで明示 |
| `databricks bundle run <job> -t dev` | 自動 | |
| `git push` / タグ付け | 確認 | Hooksでもask |
| `bundle deploy -t staging` + staging検証 | 確認 | Hooksでもask |
| `bundle deploy -t prod` | **人手（承認必須）** | GitHub Environment承認を標準 |
| `bundle destroy` / リソース削除 | **人手（承認必須）** | |
| 権限（permissions）の変更 | **人手（承認必須）** | 設計IDでの理由説明必須 |

## AIツール構成（バージョン固定）

| ツール | バージョン / 導入スコープ | 確認日 |
|---|---|---|
| Databricks CLI | TODO | YYYY-MM-DD |
| Databricks Agent Skills（aitools） | TODO / project | YYYY-MM-DD |
| AI Dev Kit（MCP等、使う場合） | TODO（version/commit/checksum） | YYYY-MM-DD |

## 承認済み例外

| 内容 | 承認者 | 日付 | 期限 |
|---|---|---|---|
| 該当なし | - | - | - |
