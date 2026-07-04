# Databricks Job 開発ハーネス — GitHub Copilot用

VS Code + GitHub Copilot で、Databricks Job（Lakeflow Jobs）の
「設計書チェック → 実装計画 → 実装 → テスト → デプロイ/リリース」を
一気通貫でオーケストレーションするための **Databricks特化テンプレート** です。

汎用アプリ開発ハーネス（CreateAppl）と同じ3層構造（Agents / Skills / Hooks）を踏襲しつつ、
次の点がDatabricks Job開発向けに特化しています。

- **上流工程（要件定義・設計）はこのハーネスの外で完了している前提。**
  入力は「承認済みの設計書」であり、最初のフェーズは設計ではなく **設計書チェック** である。
  設計書の質が悪いまま実装に入ると全自動区間が必ず破綻するため、
  ここに最も厚いゲート（品質チェック + 実装準備レビュー IRR）を置いている。
- 実装・デプロイの正は **Databricks Asset Bundles**（`databricks.yml` / `resources/*.yml`）。
  UIでの恒久変更は禁止。
- テストは「Spark非依存の単体テスト（ローカル）→ wheelビルド → bundle validate →
  devデプロイ → 実Job実行 → 結合テスト」の段階で自動実行する。
- staging/productionへのデプロイと破壊的操作（`bundle destroy` 等）は、
  Hooksにより機械的に人の確認が入る。

> 2026年7月時点のGitHub Copilot / VS Codeの最新仕様（Custom Agents, Agent Skills,
> Agent Hooks, AGENTS.md）に基づいて構築しています。Agent Hooks / Agent Plugins は
> Preview機能であり、仕様が変わる可能性があります。

> 実際の操作手順・具体例は **[USAGE.md](USAGE.md)** を参照してください。
> ハーネス自体の設計判断の背景・根拠は **[DECISIONS.md](DECISIONS.md)** に記録しています。
> ハーネスを改修する際は、同じ議論の繰り返しや直したバグの再導入を防ぐため、
> 変更前に必ず目を通してください。

## 前提

- VS Code + GitHub Copilot Chat 拡張機能（Custom Agents / Agent Skills 対応バージョン）
- Databricks CLI（Bundles対応の新CLI, v0.218以降推奨）と `uv`（Pythonツールチェーン）
- Databricks拡張機能（`databricks.databricks`）— `.vscode/extensions.json` で推奨に含めている
- （推奨）Databricks AI Dev Kit / Databricks Agent Skills —
  導入手順は `.github/skills/databricks-env-setup/SKILL.md` を参照

## 適用範囲（使うべき場面・使うべきでない場面）

このハーネスの固定費（設計登録+IRRで数時間）と1タスクあたりの儀式コスト
（タスク記録・再現テスト・証跡）は、**無人で本番データに対して走り続けるJob**で
初めて回収できる。対象外の作業に使うと明確に過剰なので、最初に判断すること。

| 場面 | 判断 | 理由 |
|---|---|---|
| 本番スケジュールで無人実行されるJob | **使う** | 欠陥が静かにデータを壊す。ゲート・冪等性実証・証跡の価値が最大 |
| 複数人・長期保守、監査要件のある環境 | **使う** | 引き継ぎ耐性と監査証跡が副産物として残る |
| 使い捨ての分析ノートブック・1回きりのアドホック処理 | **使わない** | 素のCopilot + AI Dev Kitの方が速い |
| PoC・技術検証 | **使わない**（本番化が決まった時点で載せ替える） | 仕様が流動的な段階ではゲートが摩擦になる |

過剰さへの一番の防御は、対象外の作業に使わせないことである。
なお本ハーネス自身も過剰化を避けるため、旧版から copierの二重構造・標準文書群・
Delivery Record を削除し、エージェントを8体（サブエージェント経路3本）に絞っている
（経緯は [DECISIONS.md](DECISIONS.md)）。

## クイックスタート

1. このリポジトリをテンプレートとして新しいプロジェクトを作る。
2. 承認済みの設計書を `docs/01-design/` 配下（`basic-design/`, `detailed-design/`）に配置する
   （機密上リポジトリに置けない場合は正式保管先へのリンクだけを索引に登録する）。
3. Copilot Chat で `/00-start-project` を実行する（`agent: orchestrator` にバインド済み）。
   → 進捗を確認し、次にやるべきことを提案してくれる。
4. `/01-design-intake`（設計書の索引登録・環境情報の記入）→ `/02-design-check`
   （設計書品質チェック + IRR）と進み、**IRRが `GO` / `CONDITIONAL GO` になってから**
   実装フェーズに入る。以降はハンドオフボタンでノンストップに進む。

> はじめてハーネスを試すときは、実装まで到達できるサンプル設計書一式
> （日次売上レポートジョブ、基本設計1+詳細設計4+検証データ+答え合わせ）を
> [samples/](samples/README.md) に用意している。

## フェーズごとに人の関わり方が違う（重要）

| フェーズ | 人の役割 |
|---|---|
| 設計書登録・チェック | **厚く関わる**。設計書を配置し、不足への質問に具体的に答え、IRR判定を承認する。特に `environment.md`（ワークスペース・カタログ・自動化境界）は仮置きしない。ここが要。 |
| 実装計画〜テスト | **基本ノータッチ**。devターゲットへのデプロイ・Job実行まで含めて自動実行される。真のブロッカー発生時のみ質問が来る。 |
| リリース | staging検証は自動。**productionデプロイの承認は必ず人**。Hooksでも機械的に確認が入る。 |

設計書チェックフェーズだけは厚く聞かれる前提で臨んでください。ここで
「TODOのまま」「版・承認日不明のまま」進めると、全自動区間で必ず詰まります。

## 3層構造：Agents / Skills / Hooks

| 仕組み | 役割 | 置き場所 |
|---|---|---|
| **Custom Agents** | フェーズごとの人格・ツール権限・引き継ぎ先を定義する「誰が」 | `.github/agents/*.agent.md` |
| **Subagents** | 独立コンテキストで動く補助（`design-critic`, `reviewer`, `task-worker`） | `.github/agents/*.agent.md` |
| **Agent Skills** | フェーズ内で使う手順・チェックリストという「どうやるか」の部品 | `.github/skills/*/SKILL.md` |
| **Prompt Files** | フェーズを1手ずつ進める再利用可能なスラッシュコマンド | `.github/prompts/*.prompt.md` |
| **Agent Hooks** | ゲート・セキュリティ・本番保護を機械的に補強する自動実行（Preview） | `.github/hooks/` |

エージェントを薄く保ち、手順の詳細はSkillに逃がすことで、各エージェントファイルが
肥大化しないようにしています。Skillは段階的開示（`name`/`description`だけを常時読み込み、
本文は関連する時だけ読み込む）により、コンテキスト・トークンを圧迫しない設計です。

## フェーズとエージェント／プロンプト対応表

| # | フェーズ | プロンプト | 対応エージェント | 成果物 |
|---|---|---|---|---|
| - | 進捗確認 | `/00-start-project`, `/99-status` | orchestrator | `docs/00-overview/progress.md` |
| 1 | 設計書登録 | `/01-design-intake` | design-gate | `docs/01-design/design-index.md`, `environment.md` |
| 1.5 | 設計改訂（任意） | `/08-design-revise` | design-gate | 対話で合意した設計変更の反映 + 索引の版更新（初回の下書き仕上げ・改修時の設計修正に使う） |
| 2 | 設計書チェック | `/02-design-check` | design-gate（→ `design-critic`を判定前に1回） | `docs/01-design/irr.md`（GO/CONDITIONAL GO/NO-GO） |
| 3 | 実装計画 | `/03-implementation-plan` | implement | `docs/02-implementation/tasks.md`, `traceability.md` |
| 4 | 実装 | `/04-implement-task` | implement（→ `task-worker`をタスクごとに呼び出し） | `src/` + `tests/unit/` |
| 5 | テスト | `/05-test` | test（→ `reviewer`をsubagent呼び出し） | devデプロイ・Job実行 + `docs/03-test/test-report.md` |
| 6 | リリース | `/06-release` | release | staging/prodデプロイ + `docs/04-release/` |
| 7 | 振り返り | `/07-retrospective` | orchestrator | `docs/05-retrospective/retrospective.md` |
| - | 使い方ヘルプ | `/09-harness-help` | orchestrator | 次の一手・セッション運用・コストの案内（`harness-guide` スキル） |

エージェント自身が使い方を案内する（応答末尾に「次の一手 + 新チャットにすべきか」を
添える、フェーズ違いの依頼は正しい入口へ誘導する等。AGENTS.mdの「ナビゲーション責務」）。

IRRの承認（2→3）以降は、フェーズ間の `send: true` ハンドオフにより
実装→テストがノンストップでつながる（真のブロッカー・Hooksによる`ask`確認・
`reviewer`が問題を検出した時だけ止まる）。リリースのproduction承認だけは必ず人が行う。

## 設計書チェック（このハーネスの心臓部）

「設計はできている」前提でも、**実装可能な設計書とレビューを通っただけの設計書は別物**です。
`/02-design-check` は2段階で確認します。

1. **品質チェック（design-critic サブエージェント）** — 設計書を書いた人とは独立の
   コンテキストで、曖昧さ・検証不能な記述・受け入れ条件の欠落・設計間の矛盾を検出する。
   業務設計そのものは変更せず、指摘として返す。
2. **実装準備レビュー（IRR）** — 設計内容がこのリポジトリの方式
   （Databricks Job / Bundles / CI/CD / AI支援開発）で安全に実装・試験・運用できるかを、
   `docs/01-design/irr_template.md` の必須チェック（Job DAG・compute・環境分離・権限・
   冪等性・テスト可能性・監視・復旧・AI利用境界）で確認し、
   `GO` / `CONDITIONAL GO` / `NO-GO` を判定する。

**IRRが未実施または `NO-GO` の間、エージェントはプロダクションコードを実装しません**
（AGENTS.mdのルール + SessionStartフックによるゲート状況注入で強制）。

## レビューは別コンテキストで（design-critic / reviewer サブエージェント）

- `design-gate` はIRR判定前に必ず `design-critic` を1回呼び出す（設計書の独立レビュー）。
- `test` は全テスト成功後、リリースへ進む前に必ず `reviewer` を1回呼び出す
  （コードの正しさ・Databricks固有リスク・セキュリティの独立レビュー）。

いずれも読み取り専用・独立コンテキストで起動され、「書いた本人がそのまま自己承認する」
バイアスを防ぎます。CRITICAL/HIGHの指摘があれば自動で差し戻されます。

## 成長ループ：使うたびに賢くなるハーネス

1. **教訓ログ（`docs/00-overview/learnings.md`）** — 開発中、エージェントが訂正を受けたり
   同じ失敗を繰り返したりしたら、その場で1行追記される。SessionStartフックが
   このファイルを以後の全セッションに自動注入する。
2. **振り返り（`/07-retrospective`）** — リリース後に実施。摩擦のあった出来事を
   「ハーネス改善 / プロジェクト固有 / 一過性」に分類し、改善提案表にまとめる。
3. **本体への還流** — 改善提案と再利用可能なSkillをこのテンプレートリポジトリに
   人間が適用し、`DECISIONS.md` に根拠つきで記録する。

## Agent Hooks によるゲート・本番保護（Preview）

`.github/hooks/` により以下を機械的に補強しています（詳細は
[.github/hooks/README.md](.github/hooks/README.md)）。

- `*_template.md` への直接編集を **deny**
- `git push` / `git tag` / force系 / `rm -rf` を **ask**（毎回確認）
- **`databricks bundle deploy/run` の staging・prodターゲット指定、`bundle destroy`、
  `jobs delete` 等の本番影響・破壊的CLI操作を ask**（devターゲットは自動実行を許可）
- セッション開始時にフェーズゲート状況（IRR判定を含む）を自動注入
- ハーネス自体の設定（`.github/agents/`・`hooks/`・`AGENTS.md` 等）への編集を **deny**
- クラウド認証情報・秘密鍵らしき高確度パターンを **deny**、汎用的なパターンは **ask**

Preview機能のため、発火しない環境でも `AGENTS.md` の指示レベルのルールが効くように
してあります（二重の安全網）。さらにGitHub Environments（productionのrequired reviewers）、
Databricks側の権限分離（dev用IDにはprod書き込み権限を与えない）を最終ゲートとします。

## ディレクトリ構成

```
AGENTS.md                     … 全AIエージェント共通の唯一の指示ファイル（正）
plugin.json                   … Agent Plugin マニフェスト（配布用、任意）
databricks.yml                … Asset Bundle定義（dev/staging/prodターゲット）
resources/                    … Job等のリソース定義（宣言的、1リソース1ファイル）
src/                          … wheelパッケージ本体（ノートブックを主実装にしない）
tests/
  unit/                       … Spark非依存・ローカル完結の単体テスト
  integration/                … デプロイ済みリソースが必要な結合テスト（markerで分離）
.github/
  agents/                     … フェーズ別Custom Agent + subagents
  skills/                     … 手順・チェックリスト（IRR、テスト設計、デプロイ等）
  prompts/                    … フェーズを進めるプロンプトファイル
  hooks/                      … ゲート・本番保護フック（Preview）
  instructions/               … パス限定の追加指示（bundles/python/tests/docs）
  workflows/                  … CI（品質ゲート+secret scan）とstaging/prodデプロイ（OIDC）
  pull_request_template.md    … 設計ID・検証証跡・データ影響を必須にするPRテンプレート
docs/
  00-overview/                … 進捗ダッシュボード（GATE_STATUS）・教訓ログ
  01-design/                  … 入力となる設計書一式・索引・IRR・環境情報
    basic-design/             … 基本設計（アーキテクチャ・外部設計）
    detailed-design/          … 機能別・共通機能別の詳細設計
    requirements/             … 要件文書（ある場合のみ）
  02-implementation/          … 実装タスクリスト・トレーサビリティ
  03-test/                    … テスト計画・結果・独立レビュー結果
  04-release/                 … リリースチェックリスト・Runbook・CHANGELOG
  05-retrospective/           … 振り返り
```

## 設計方針

- **設計書チェックがすべての前提**: 上流の欠陥は下流ほど修正コストが大きい。
  実装より前に、最も費用対効果の高い独立レビュー（design-critic + IRR）を置く。
- **Bundlesが正、UIは見るだけ**: Job定義・権限・スケジュールの変更はすべて
  `databricks.yml` / `resources/*.yml` 経由。UIでの恒久変更は禁止。
- **業務ロジックはSparkから分離**: `src/` の純粋関数に業務ルールを置き、
  ローカルで高速にテストできるようにする。Sparkやワークスペースが必要なテストは
  `tests/integration/` にmarker付きで分離する。
- **環境差分は変数化**: catalog/schema/通知先などはBundle変数とターゲット定義に置き、
  コードに直書きしない。シークレットはDatabricks Secrets / GitHub Secretsを参照する。
- **dev自動・prod人間**: devターゲットへのdeploy/runは全自動区間に含める。
  staging/prodはHooks・GitHub Environments・権限分離の三重で人の承認を強制する。
- **エージェントを薄く、手順はSkillへ**: 各エージェントは人格・権限・引き継ぎ先だけを持つ。
- **クロスエージェント対応**: `AGENTS.md` を単一の正として、VS Code Copilot以外
  （Copilot coding agent, Claude Code等）でも同じルールが効くようにする。
- **トークンコストを意識**: 高頻度・機械的なフェーズは `model: auto`、
  一度の判断ミスが高くつくフェーズ（設計書チェック・独立レビュー）は強いモデルを検討する。

## 他の開発ハーネス・手法との位置づけ（2026年7月調査）

| 手法 | 特徴 | このハーネスとの関係 |
|---|---|---|
| [GitHub Spec Kit](https://github.com/github/spec-kit)（スペック駆動開発） | constitution→specify→plan→tasks→implementの汎用SDDワークフロー | 思想は同じ「仕様が正、コードは生成物」。Spec Kitは仕様をAIと書く前提だが、本ハーネスは**承認済み設計書が別工程から来る企業開発**に合わせ、設計書チェック(IRR)をゲートにした。Spec Kitの`/analyze`（成果物間整合チェック）相当は`/99-status`の横断整合監査として取り込み済み |
| BMAD Method（12+エージェントのアジャイルチーム模倣） | Analyst/PM/Architect/QA等のフルロールプレイ | 上流(要件・設計)までAIで担う思想。本ハーネスは上流を人間の設計工程に置き、エージェントを8体・サブエージェント経路3本に絞ってコストを制御 |
| Kiro（AWSのスペック駆動IDE） | EARS記法要求への変換と実装の追跡 | EARS記法はdesign-criticの指摘（書き直し例の提示）に採用 |
| [Databricks AI Dev Kit](https://github.com/databricks-solutions/ai-dev-kit) / Agent Skills | 公式スキル8種 + MCP 50ツール | 競合ではなく部品。操作の正はCLI+Bundles（フックで検査可能）とし、Dev Kitは知識・調査層として標準導入（`databricks-env-setup`スキル） |

本ハーネス固有の強み: **設計書チェック（IRR）の機械可読ゲート**（フックがNO-GOを
毎セッション注入）、**本番保護の三重化**（Hooks + GitHub Environments + Databricks権限分離）、
**乖離追跡つきホットフィックス**、**改修の差分駆動**、**成長ループ**（learnings/振り返り/DECISIONS）。

## 既知の制約・要検証事項

- Custom Agents / Agent Skills / Agent Hooks は比較的新しい機能（一部Preview）であり、
  実際にVS Code上で動かしてフォーマットのズレがないか確認することを推奨します。
- Databricks AI Dev Kit / `databricks aitools` は活発に更新されているため、
  導入時は `.github/skills/databricks-env-setup/SKILL.md` の手順で公式一次情報を
  確認しながらバージョンを固定してください。
- Hooksのstdin/stdoutペイロード形状は公式一次情報から確認した範囲での実装であり、
  実環境での挙動確認・調整が必要な場合があります。
