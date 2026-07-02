# DECISIONS.md — このハーネス自体の設計判断の記録

ハーネスを改修する際は、同じ議論を繰り返したり直したバグを再導入したりしないよう、
変更前に必ずこのファイルに目を通すこと。新しい判断を下したら、根拠つきでここに追記する。

---

## D-001: 汎用ハーネス（CreateAppl）の3層構造を踏襲する

- **判断**: Agents（誰が）/ Skills（どうやるか）/ Hooks（機械的強制）+ Prompts + 単一の
  `AGENTS.md` という構成を、Databricks特化版でもそのまま採用する。
- **根拠**: CreateAppl で実証済みの構成であり、エージェントを薄く保つ・段階的開示で
  コンテキストを節約する・指示とHooksの二重の安全網、という設計原則がそのまま通用する。
  ハーネスごとに構造が違うと、利用者・改修者の学習コストが二重になる。

## D-002: copierテンプレート層を廃止し、フラットなテンプレートリポジトリにする

- **判断**: 旧 `databricks-develop` が持っていた copier テンプレート
  （`template/` + `copier.yml` + 生成テスト + テンプレート運用ドキュメント・CI）を廃止。
  このリポジトリ自体を「GitHubのテンプレートリポジトリとしてコピーして使う」形にする。
- **根拠**: テンプレートのテンプレートという二重構造が複雑さの主因だった
  （`template/`・`generated-test/`・`template-tools/`・テンプレート配布用workflowが混在し、
  どのファイルが正か分かりにくい）。プロジェクト数が増えテンプレート更新の一斉配布が
  本当に必要になった時点で、copier化を再検討すればよい（YAGNI）。
- **影響**: 旧テンプレートの `template-lifecycle.md`、`update_template.py` 等は引き継がない。

## D-003: 最初のフェーズを「要件定義」ではなく「設計書チェック」にする

- **判断**: このハーネスは要件定義・業務設計を行わない。入力は承認済み設計書であり、
  フェーズ1は設計書の登録（索引化）、フェーズ2は品質チェック + 実装準備レビュー（IRR）。
- **根拠**: 対象組織のDatabricks Job開発は、設計が別工程（別チーム・別ツール）で完成する
  ワークフローである。一方「設計書の質が悪いと先が進まない」ため、CreateApplで
  要件定義に置いていた「最も厚い人の関与と独立レビュー」を、ここでは設計書チェックに移した。
  spec-critic（CreateAppl）に相当する独立レビューは `design-critic` として残し、
  Databricks適合性の機械的チェックは IRR（旧databricks-developから継承）が担う。

## D-004: IRRのGO/CONDITIONAL GO/NO-GOゲートを継承する

- **判断**: 旧 `databricks-develop` の実装準備レビュー（IRR）テンプレートと
  「NO-GOの間はプロダクションコードを実装しない」ルールをほぼそのまま継承する。
- **根拠**: IRRの必須チェック（Job DAG・compute・環境分離・権限・冪等性・テスト可能性・
  監視・復旧・AI利用境界）は旧ハーネスで最も価値が高かった資産であり、
  「設計レビュー通過」と「この方式で実装可能」のギャップを埋める唯一の仕組み。

## D-005: 設計書の実体はリポジトリ内・外のどちらでもよい（索引が正）

- **判断**: `docs/01-design/design-index.md` を唯一の入口とし、設計書本体は
  リポジトリ内（`basic-design/` 等）でも外部の正式保管先でもよい。ファイル名は強制せず、
  変更されにくい設計IDで追跡する。
- **根拠**: 機密区分上リポジトリへ複製できない設計書が存在する。また既存の組織命名規則を
  壊さないため。AIは索引→対象設計だけを読む（コンテキスト節約）。

## D-006: devターゲットへのdeploy/runは全自動区間に含める

- **判断**: `databricks bundle deploy -t dev` / `bundle run -t dev` は確認なしで
  自動実行してよい。staging/prodターゲットの指定・`bundle destroy`・`jobs delete` は
  Hooksで ask を強制する。
- **根拠**: devは `mode: development` + ユーザー配下のパスに隔離され、壊しても影響が
  個人開発領域に閉じる。ここまで自動化しないと「テストフェーズの全自動」が成立しない
  （単体テストだけでは実Jobの検証にならない）。本番保護はHooks・GitHub Environments・
  Databricks権限分離の三重で担保する。

## D-007: サブエージェント経路は3つに絞る

- **判断**: `design-gate → design-critic`（1回）、`implement → task-worker`（タスク数）、
  `test → reviewer`（1回）のみを既定とする。
- **根拠**: CreateAppl の4経路のうち `requirements → spec-critic` は上流工程ごと
  ハーネス外に出たため不要。並列多視点レビューはコスト対効果の判断が要るため
  ユーザーの明示要求時のみ（CreateApplと同方針）。

## D-008: 実行系ツールチェーンは uv + taskipy + Databricks CLI に固定

- **判断**: `uv run task format/check/build/integration` を標準コマンド群とし、
  エージェント・CI・人間が同じコマンドを使う。
- **根拠**: 旧ハーネスで実証済み。エージェントに「何を実行すれば検証済みと言えるか」を
  一意に伝えられる（`AGENTS.md` の完了条件が機械的に定義できる）。

## D-009: AI Dev Kit / Databricks Agent Skills は「導入手順Skill」として扱う

- **判断**: AI Dev KitのMCPサーバーやDatabricks公式Agent Skills（`databricks aitools`）は
  ハーネスに同梱せず、`databricks-env-setup` Skill の手順でプロジェクトごとに導入する。
  バージョン・スコープを固定し、更新は専用PRでレビューする。
- **根拠**: 外部キットは更新が速く、同梱すると陳腐化する。またマシン固有の
  `.vscode/mcp.json` はコミットしない（旧ハーネスの運用ルールを継承）。
  公式Skillsは製品構文の根拠に使い、案件固有の設計より優先しない。

## D-010: ドキュメント階層は docs/00〜05 の番号付きフラット構成にする

- **判断**: 旧 `databricks-develop` の `docs/standards/`（9ファイルの組織標準文書群）と
  `docs/ai/`（context-map等）を廃止し、CreateAppl型の番号付きフェーズ別ディレクトリに
  一本化する。組織ルールは `environment.md` の該当欄と `AGENTS.md` に集約する。
- **根拠**: standards文書群は正本が分散して「どこに何を書くか」の判断コストが高かった。
  AI参照ルーター（context-map）の役割は、Skillの段階的開示とプロンプトの
  agentバインドで代替できる。

## D-011: Delivery Record は導入しない（tasks.md + traceability.md で代替）

- **判断**: 旧ハーネスのIssueごとのDelivery Record（`docs/project/delivery/active/`）は
  引き継がず、`docs/02-implementation/tasks.md`（進捗の正）と
  `traceability.md`（設計ID↔実装↔テストの対応）の2ファイルに集約する。
- **根拠**: Delivery RecordはIssue駆動・複数人並行開発向けの重い仕組みで、
  記入コストが高い割にtasks.mdと内容が重複していた。1人+AIの開発フローでは
  「唯一の正の状態ファイル」を増やさない方がコンテキスト管理上も有利。
  複数人運用にスケールさせる場合に再検討する。

## D-012: CI/CDワークフロー（ci.yml / deploy.yml）を同梱する

- **判断**: PRごとの品質ゲート（uvタスク + gitleaks secret scan）と、
  main→staging自動デプロイ + workflow_dispatch→production（Environment承認）の
  2ワークフローを最初から同梱する。認証はOIDC（`databricks/setup-cli` + github-oidc）。
- **根拠**: release-checklist・deployスキル・AGENTS.mdがCI成功とEnvironment承認を
  前提にしているのに実体が無いと、利用者が毎回ゼロから書くことになり品質担保が絵に描いた
  餅になる（初版レビューで発見）。ワークフローはハーネス設定と同様にhooks/CODEOWNERSで
  エージェントの自動編集から保護する。

## D-013: プロジェクトリネームは実装フェーズのT-000タスクとして実行する

- **判断**: `sample_job`→案件名のリネームは、design-gateが名前を決めて
  `environment.md` に記録し、実行は人間または実装フェーズの最初のタスク（T-000）が
  `databricks-env-setup` スキルのチェックリストに従って行う。
- **根拠**: design-gateは最小権限の原則で `execute` を持たない（CreateAppl踏襲）。
  リネームはファイル移動と検証コマンド実行を伴うため、design-gateに実施させる
  初版の記述は権限と矛盾していた（初版レビューで発見）。

## D-014: MCP設定は `.vscode/mcp.json.example` のTODO付き雛形で提供する

- **判断**: AI Dev KitのMCPサーバー導入コマンドをハーネスにハードコードせず、
  exampleファイル + 公式README参照の形にする。
- **根拠**: AI Dev Kitのコマンド体系は更新が速く、誤ったコマンドを焼き込むより
  「公式一次情報で確認してバージョン固定」の運用を強制する方が安全（D-009と同方針）。
  また、MCPツールはHooksのコマンド検査が及ばないため、接続identityの権限を
  devの最小権限に絞ることをexampleとスキルの両方に明記した。
