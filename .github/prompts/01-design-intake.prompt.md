---
agent: design-gate
description: '承認済み設計書をdocs/01-design/へ配置・索引登録し、environment.md（環境・自動化境界）をヒアリングして埋める'
---

design-gateエージェントの「フェーズ1: 設計書登録」の手順で進める。

1. ユーザーが持っている設計書の種類（要件/基本設計/機能詳細/共通詳細）と
   配置可否（リポジトリ内 or 外部正式保管先）を確認し、配置を案内する。
2. `docs/01-design/design_index_template.md` から `design-index.md` を作成し、
   設計ID・版・承認日・受け入れ条件・関連IDを登録する。`TODO`のまま残る行は
   「未登録」として明示する。
3. `docs/01-design/environment_template.md` から `environment.md` を作成し、
   ワークスペース・認証・catalog/schema分離・実行identity・シークレット保管先・
   自動化境界を構造化した質問でヒアリングして埋める。仮置きを許さない。
4. プロジェクト名が `sample_job` のままなら案件名を決めて `environment.md` に記録する
   （リネームの実行は人間か実装フェーズのT-000タスクに委ねる。
   チェックリストは `databricks-env-setup` スキル参照）。
5. 完了したら `/02-design-check`（設計書チェック）へ進むことを案内する。
