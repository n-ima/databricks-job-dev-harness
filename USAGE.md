# USAGE.md — 実際の使い方（具体例つき）

このドキュメントは「手を動かしたときに何が起きるか」を追う操作ガイドです。
全体構造の説明は [README.md](README.md) を参照してください。

## 0. 初回セットアップ（プロジェクト開始ごとに1回）

1. このリポジトリをテンプレートとして新しいリポジトリを作り、VS Codeで開く。
2. ターミナルで環境を確認する（詳細は `.github/skills/databricks-env-setup/SKILL.md`）。

```bash
uv sync --all-groups
uv run task check          # ハーネス自体が壊れていないことを確認
databricks auth login --host https://<workspace-host>   # devプロファイル作成
databricks bundle validate -t dev
```

3. プロジェクト名（`sample_job` / `sample-job`）を案件名にリネームする。
   変更箇所のチェックリストは `.github/skills/databricks-env-setup/SKILL.md` の
   「プロジェクトリネーム」節を参照（この場で手動でやらなくても、`/01-design-intake` で
   名前を決めて記録し、実装フェーズのT-000タスクとしてエージェントに任せられる）。
4. （標準）Databricks公式Agent Skills / AI Dev Kit を導入する
   （`databricks-env-setup` Skill参照。バージョンを固定し、導入は専用PRにする）。
   MCPサーバーを使う場合は `.vscode/mcp.json.example` を `mcp.json` にコピーして設定する。
   - **役割分担に注意**: Databricksの「操作」（deploy/run）の正は常にCLI + Asset Bundles
     （フックで検査でき、CI/CDと同一コマンドで再現できるため）。AI Dev Kitが担うのは
     「知識と調査」— 正しいBundle構文の供給（Agent Skills）と、テーブルスキーマや
     Job実行状態のChat内調査（MCP）。導入すると実装・テスト失敗調査の往復が大きく減る。
   - ハーネスに同梱していないのは更新が速く焼き込むと陳腐化するため（DECISIONS D-009）。
     組織ポリシー等で導入できない場合は、その旨を `environment.md` のAIツール構成に記録する。
5. GitHub Copilot Chat にサインインし、Chatビューのagentセレクタに
   `orchestrator` 等が表示されることを確認する。
6. （CI/CDを使う場合）GitHubリポジトリに `staging` / `production` Environmentsを作成し、
   `production` にrequired reviewersを設定する。各Environmentに `DATABRICKS_HOST` /
   `DATABRICKS_CLIENT_ID` 変数を登録し、Databricks側でservice principalの
   federation policy（OIDC）を設定する（`.github/workflows/deploy.yml` のコメント参照）。

## 1. プロジェクト開始 → 設計書登録

承認済みの設計書（基本設計・詳細設計）を手元に用意し、Copilot Chatで:

```text
/00-start-project
```

orchestrator が進捗ダッシュボード（`docs/00-overview/progress.md`）を作成し、
「設計書登録から始めましょう」と提案してくる。ハンドオフボタンで `design-gate` に移り:

```text
/01-design-intake
```

エージェントは次を行う。

- 設計書ファイルを `docs/01-design/basic-design/`・`detailed-design/features/`・
  `detailed-design/common/` へ配置するよう案内（リポジトリに置けない機密文書は
  正式保管先のリンクだけ登録）。
- `docs/01-design/design-index.md` に設計ID・版・承認日・受け入れ条件を登録。
- `docs/01-design/environment.md` のヒアリング。**ここは仮置きせず答えること**:
  - dev/staging/prod のワークスペースURL・認証プロファイル
  - catalog / schema の環境分離
  - 実行用service principal、通知先、シークレット保管場所
  - **自動化境界**（エージェントが確認なしで実行してよい操作の範囲）

## 2. 設計書チェック（品質チェック + IRR）

新しいチャットセッションを開いて:

```text
/02-design-check
```

- `design-gate` がまず `design-critic` サブエージェントを独立コンテキストで1回呼び出し、
  曖昧さ・受け入れ条件の欠落・設計間の矛盾を検出する（BLOCKER/MAJOR/MINOR）。
- 次に `docs/01-design/irr_template.md` から `irr.md` を作成し、Databricks適合性
  （Job DAG・compute・環境分離・権限・冪等性・テスト可能性・監視・復旧・AI利用境界）を
  チェックして `GO` / `CONDITIONAL GO` / `NO-GO` を判定する。
- **判定と根拠が提示されたら、人が承認する。** `NO-GO` の場合は設計工程に差し戻す
  不足リストが出るので、設計側で解消してから再実行する。

`GO`（または期限・担当付き条件つきの `CONDITIONAL GO`）が承認されると、
`GATE_STATUS` の `design_check` が `done` になり、以降の全自動区間が解放される。

## 3. 実装計画 → 実装 → テスト（全自動区間）

```text
/03-implementation-plan
```

`implement` が設計IDごとに1コミット粒度のタスクへ分解し、`docs/02-implementation/tasks.md` と
`traceability.md`（設計ID↔実装↔テストの対応表）を作る。そのまま:

```text
/04-implement-task
```

- タスクごとに `task-worker` サブエージェントが独立コンテキストで起動し、
  受け入れ条件から先にテストを書き、最小実装で通す（テストファースト）。
- あなたは基本見ているだけでよい。止まるのは「設計だけでは判断できない事実が必要なとき」と
  Hooksが確認を求める操作のときだけ。
- 全タスク完了後、自動で `test` エージェントへハンドオフされる。

テストフェーズでは次が自動実行される。

```bash
uv run task check                         # format / lint / mypy / 単体テスト
uv run task build                         # wheelビルド
databricks bundle validate -t dev
databricks bundle deploy -t dev           # devは確認なしで自動（自動化境界内）
databricks bundle run <job> -t dev
uv run task integration                   # デプロイ済みリソースに対する結合テスト
```

結果は `docs/03-test/test-report.md` にまとまり、最後に `reviewer` サブエージェントの
独立レビュー（正しさ・冪等性・権限・シークレット・性能/コスト）が入る。
CRITICAL/HIGHがあれば自動で実装に差し戻される。

## 4. リリース（staging自動 → production承認は人）

```text
/06-release
```

- `release` エージェントが `docs/04-release/release-checklist.md` を作成し、
  staging へ同一コミットをデプロイして検証する（`bundle deploy -t staging` は
  Hooksにより ask 確認が入る）。
- 検証証跡（commit SHA・bundle target・Job run ID・結果）が揃ったら、
  **productionデプロイの最終承認を人に求める**。AIは自己承認しない。
  GitHub Actionsを使う場合、mainへのmergeで `.github/workflows/deploy.yml` が
  stagingへ自動デプロイ・検証し、productionは `workflow_dispatch` +
  `production` Environment の required reviewers が最終ゲートになる。
- デプロイ後は最初のJob実行を監視し、閾値を満たさない場合は停止して
  rollback（旧成果物の再デプロイ）/ roll-forward の判断を人に提示する。

## 5. 振り返り

```text
/07-retrospective
```

摩擦のあった出来事を「ハーネス改善 / プロジェクト固有 / 一過性」に分類し、
ハーネス改善分を提案表にする。採用した改善はハーネス本体リポジトリに人間が適用し、
`DECISIONS.md` に記録する。

## 6. リリース後の機能改修・バグ修正

改修も新規開発と同じゲートを通るが、**常に差分駆動**で行う。全設計書の再チェックや
全タスクの見直しはしない（トークンと時間の無駄）。影響範囲は
`docs/02-implementation/traceability.md`（設計ID→実装→テスト）から機械的に辿る。
改修サイクルの開始時に、`GATE_STATUS` の該当フェーズを `in_progress` へ戻す
（`gate-check` スキル参照）。起点は2つに分かれる。

### A. 設計変更を伴う改修（機能追加・仕様変更）

1. 設計書を設計工程（ハーネスの外）で修正・承認する。
2. `design-index.md` の該当設計IDの版・承認日を更新する（新機能なら行を追加）。
3. `/02-design-check` を実行する。design-criticとIRRは**変更された設計IDに関する
   項目だけ**を再判定する（`design-readiness-review` スキルの「再判定」節）。
   全項目のやり直しはしない。
4. `/03-implementation-plan` で該当設計IDのタスクだけを `tasks.md` に追記する。
5. 以降は通常どおり `/04` → `/05` → `/06`。テストは影響のある受け入れ条件 + 回帰
   （`uv run task check` は常に全体が走るので回帰は自動的に担保される）に絞る。

### B. 設計変更を伴わないバグ修正（実装が設計とずれていた）

設計書は正しいので設計書の修正もIRRの再判定も不要。

1. `tasks.md` に修正タスクを1行追記し、**再現テストを先に追加**して失敗を確認する。
2. 最小修正で通し、`uv run task check` で回帰確認する。
3. `/05-test`（影響範囲のdev検証）→ `/06-release`。

## セッション運用の原則

- **フェーズが変わったら New Chat**。特に設計書チェック・独立レビューは
  実装セッションの続きで行わない（前提や自己弁護を引き継がないため）。
- 会話が長くなってきたら、無理に続けず新しいセッションで `docs/` を読み直させる。
  ドキュメントに残っている情報は会話をまたいでも失われない。
- 進捗が分からなくなったら `/99-status`。

## よくある質問

**Q. 設計書がExcel/社内Wikiにあり、リポジトリに置けない。**
A. 問題ない。`design-index.md` に正式保管先URL・版・承認日を登録すれば、
エージェントは「その設計IDについて人に内容を確認する」動きになる。
ただし実装に必要な粒度の情報（入出力スキーマ・受け入れ条件）はIRRで具体化を求められる。

**Q. IRRがNO-GOのまま急ぎで実装したい。**
A. ハーネスとしては推奨しない（NO-GO = 推測実装になる状態）。それでも進める場合は
人間の判断で `GATE_STATUS` を手動更新することになるが、その決定と理由を
`docs/00-overview/progress.md` の申し送りに残すこと。

**Q. devデプロイまで勝手にやってほしくない。**
A. `docs/01-design/environment.md` の自動化境界で「devデプロイは人手」と明示すれば、
エージェントはそれに従う（フェーズの既定より environment.md の明示が優先）。

**Q. 障害対応でどうしようもなく、設計書を直さずコードを直接修正した（したい）。**
A. 緊急のroll-forwardとして許容される。ただし2つの原則を守ること。
1. **緊急でも省略しないもの**: 再現テスト・PR・人の承認・記録
   （`AGENTS.md` / releaseエージェントの方針。Hooksもこれらを免除しない）。
2. **乖離を機械的に追跡する**: 修正と同時に
   `design-index.md` の該当設計IDの状態を「実装乖離あり（解消期限: YYYY-MM-DD）」にし、
   `learnings.md` に1行追記する（SessionStartフックで全セッションに注入され、
   忘れられなくなる）。期限までに設計書を正式に更新して版を上げ、状態を戻す。
   乖離が未解消の間、次の `/02-design-check` は該当設計IDを `CONDITIONAL GO` の
   条件として扱う。**「絶対禁止」にしない代わりに「黙って乖離したまま」を禁止**している。

**Q. 既存のJobリポジトリに後からこのハーネスを入れたい。**
A. `.github/`・`docs/`・`AGENTS.md` をコピーし、`databricks.yml` は既存のものを正とする。
`/01-design-intake` から始めれば索引・環境情報が既存構成に合わせて埋まる。
