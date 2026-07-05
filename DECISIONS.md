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

## D-015: AI Dev Kitは「知識と調査」、CLI+Bundlesは「操作」という役割分担

- **判断**: Databricksの操作（deploy/run/destroy）の正は常にDatabricks CLI +
  Asset Bundlesとし、AI Dev Kit（Agent Skills / MCP）は構文知識の供給と
  ワークスペース調査（スキーマ参照・run調査）に使う。導入は「標準」とするが
  同梱必須にはしない（できない組織のためにenvironment.mdへの理由記録を求める）。
- **根拠**: CLIコマンドは `guard-databricks-prod` フックで検査でき、CI/CDと同一の
  再現可能な経路になる。MCPツール呼び出しはフックのコマンドパターン検査が及ばないため、
  操作の主経路にすると本番保護が権限分離だけに痩せる。公式キット自体も
  Bundles/CLIをデプロイの正としている。「公式キットを使わない」のではなく
  「公式のデプロイ経路(CLI)と公式のAI支援(Dev Kit)を層で使い分ける」。

## D-016: 改修・バグ修正は差分駆動、ホットフィックスは乖離追跡つきで許容

- **判断**: リリース後の改修は (A) 設計変更あり→該当設計IDだけIRR再判定→該当タスクのみ
  追加、(B) 設計変更なしのバグ修正→設計書修正・IRR再判定とも不要（再現テスト先行で修正）
  の2経路とし、全体見直しをしない。緊急ホットフィックスによる設計との乖離は禁止せず、
  `design-index.md` の状態「実装乖離あり（期限つき）」+ `learnings.md` 追記で機械的に
  追跡し、未解消の間はIRRを `CONDITIONAL GO` 止まりにする。
- **根拠**: 影響範囲は `traceability.md` で機械的に辿れるため、全体再チェックは
  トークンと時間の無駄（ユーザー指摘）。ホットフィックスを「絶対禁止」にすると
  障害対応で必ず破られ、破られたルールは記録もされなくなる。禁止するのは
  「黙って乖離したままにすること」だけにし、learnings.mdへの記録でSessionStart注入に
  乗せて忘れられない仕組みにした。

## D-017: 設計改訂をハーネス内に取り込む（/08-design-revise、D-003の部分的緩和）

- **判断**: design-gateに「設計ディスカッション・改訂」モードを追加。バグ・機能追加の
  内容から影響設計IDを特定し、選択肢・トレードオフを議論して**1決定ずつ人間の合意**を
  取りながら設計書を改訂できる。初回の下書き設計書を対話で仕上げる用途にも使う。
  外部正本（Excel/Wiki）の場合は変更提案Markdownを出力して人が反映する。
  改訂後の `/02-design-check`（差分再判定）は別セッションで行う。
- **根拠**: D-003の「業務設計を変更しない」は運用してみると保守フローで不便
  （ユーザー要望: 改修は設計書修正から始めたい、初回もディスカッションで仕上げたい）。
  本来防ぎたかったのは「AIが黙って推測で補完する」ことであり、人間合意つきの
  改訂プロセスはむしろ設計と実装の乖離を防ぐ。絶対ルールの文言を
  「黙って変更・補完しない」に精密化した。

## D-018: セッション分割の基準を数値つきで明文化

- **判断**: `/03→/04→/05`（実装計画〜テスト）は1セッション継続を既定とし、
  「完了タスク10個超」「実装⇔テスト差し戻し2往復超」「応答劣化」「中断」のいずれかで
  新セッションへ切り替える。設計改訂(/08)とチェック(/02)、リリース、改修サイクル開始は
  必ず新セッション。USAGE.mdに表として明文化。
- **根拠**: 実装本体はtask-workerに隔離されるためコーディネーターの会話は軽く、
  フェーズごとに切るより継続の方が運用が単純。ただし同一セッションは毎ターン履歴を
  再送するため無限に安くはなく、「いつ切るべきか」が曖昧だとユーザーが判断できない
  （ユーザー指摘）。数値目安を置き、エージェント側からも区切りを提案するようにした。

## D-019: 全エージェントにナビゲーション責務（メタガイダンス）を持たせる

- **判断**: 全エージェントは応答末尾に「次の一手 + 新チャットにすべきか」を案内し、
  フェーズ違いの依頼は正しい入口へ誘導し、セッション切り替えを自分から提案する
  （AGENTS.md「ナビゲーション責務」）。使い方の質問専用に `/09-harness-help` +
  `harness-guide` スキルを追加。
- **根拠**: ハーネスの価値は正しく使われて初めて出る。操作手順を人が暗記する前提は
  スケールしない（ユーザー要望）。案内ロジックをスキルに集約し、各エージェントには
  「案内する義務」だけを置くことで、指示の重複とコンテキスト消費を抑えた。

## D-020: 2026年7月の他ハーネス・公式機能調査に基づく採用/見送り

- **調査対象**: GitHub Spec Kit、BMAD Method、Kiro、GSD、VS Code Copilot公式の
  Hooks/Custom Agents/Skills/Plugins最新仕様、Databricks AI Dev Kit / Agent Skills公式。
- **採用**:
  - `PreCompact` フックでGATE_STATUS/IRR/教訓を再注入（圧縮でゲート状態が失われる穴を
    塞ぐ。公式Hooks仕様の8イベント中、従来3つしか使っていなかった）
  - Spec Kit `/analyze` 相当の横断整合監査を `gate-check` スキル + `/99-status` に追加
  - Kiro由来のEARS記法をdesign-criticの指摘（書き直し例）に採用
  - `aitools` の正確なスキル構成（8種、core/dabs/jobsが中核）とコマンドを
    `databricks-env-setup` に反映。AI Dev Kitのリポジトリは
    **databricks-solutions/ai-dev-kit**（旧記載の databricks/ai-dev-kit は誤り）
- **見送り**:
  - agent-scoped hooks（.agent.md frontmatter定義）— workspace hooks（.github/hooks/）に
    一元管理する方が保護対象の見通しがよく、ハーネス設定保護フックの対象も1箇所で済む
  - BMAD型の多エージェント化 — コスト対効果が合わない（D-007の3経路を維持）
  - Spec Kit `taskstoissues`（GitHub Issues連携）— D-011の軽量方針を維持
  - Autopilot（公開プレビュー）— 採用ではなく「Hooksのask有効を確認して使う」注意つき
    案内に留める（harness-guideスキル）

## D-021: サンプルは同梱、ハーネスの検証は「配布経路で作った別プロジェクト」で行う

- **判断**: 動作確認用サンプル（`samples/`: 設計書md+検証CSVのみ、コードなし）は
  ハーネス本体に同梱し、配布ZIPにも既定で含める（除外したい組織向けに
  `.gitattributes` の `export-ignore` をコメントで用意）。ハーネスのE2E検証は
  本体リポジトリやブランチ上では行わず、**ZIP/テンプレートの配布経路で作った
  使い捨ての検証プロジェクト**（例: `../daily-sales-report-trial`）で実施する。
  改善は検証プロジェクトの `/07-retrospective` → 人間が本体へ適用 → DECISIONS記録で還流。
- **根拠**: 本体上で実装するとテンプレートが「実装済みプロジェクト」に変質し配布物が
  汚れる。ブランチ検証は実装コミットがハーネス履歴と絡み、公開リポジトリに残骸が載り、
  かつ配布経路を通らないため配布手順の欠陥を検出できない。別プロジェクト方式は
  利用者と同じ道を通るドッグフーディングになり、テスト自体が配布検証を兼ねる。
  別リポジトリ化はCI/PRフローまで検証したい場合にのみ（privateで）作成すればよい。

## D-022: E2E検証第1回（daily-sales-report-trial, 2026-07-05）の還流

検証プロジェクトの振り返り（H-001〜H-006 + ユーザー観察）から適用した改善。

- **最重要: 教訓ログのトリガー拡張（ユーザー観察起点）**。dev検証で試行錯誤の末に
  確立したコマンド実行方法（CLIのPATH問題→Python経由等）が記録されず、別セッションの
  stagingで同じ試行錯誤が再発した。仕組み（learnings.md + SessionStart注入）は機能して
  いたが、トリガー条件が仕様系の教訓に偏り「実行方法の獲得知識」が記録対象と認識されて
  いなかったのが原因。対応: AGENTS.md / learnings_template / harness-retrospective の
  トリガーに「試行錯誤の末に確立した実行方法は成功コマンドをそのまま記録」
  「セッション終了・引き継ぎ前に記録済みか確認」を追加し、test（記録する側）と
  release（最初から使う側）のエージェントに明示した。
- **H-001**: main.job.yml のserverless例を検証済みの形（`environment_key` +
  `spec.client: "2"`）に更新し、実機制約確認の注意を追記。
- **H-002**: IRRのDatabricks適合性に「compute選択が実機制約と一致することを
  実ワークスペースで確認」を必須項目として追加（environment.md記載の鵜呑み禁止）。
  ※ サーバレス専用ワークスペースにclassic設計のまま `GO` を出し実装で手戻りした実績。
- **H-003/H-006**: databricks-job-testing に「Serverless SQL Warehouse cold startの
  120秒ポーリング」「異常系は明示チェック（内部例外任せ禁止）」の落とし穴節を追加。
  python.instructions / task-worker禁止事項にも異常系の明示チェックを追加。
- **H-004**: databricks-env-setup に devリソース初期化節（schema/Volume/出力ディレクトリ/
  テーブル/テストデータの冪等スクリプト化、Volume出力先は自動で作られない）を追加。
- **H-005**: SQL直接連結の禁止を task-worker の禁止事項に前倒し
  （reviewer検出では手戻りが大きい。実装時点で止める）。

## D-023: 起動経路の等価性ルール（プロンプト/ハンドオフ/サブエージェント）

- **判断**: ハンドオフ経由では `.prompt.md` が読み込まれないため、
  「振る舞いの正は常に `.agent.md`、プロンプトは薄い起動ショートカット
  （プロンプト固有の手順を持たせない）」を明文化した（AGENTS.md）。あわせて点検で
  見つかった違反を修正: (1) T-000リネーム指示が03プロンプトにしかなかった
  → implement.agent.md へ移植。(2) test→release ハンドオフが `send: true` で
  同一セッション自動続行になっており、USAGEの「リリースは新規セッション」と矛盾
  → `send: false` に変更し、testエージェントは新チャットでの `/06-release` を推奨、
  ボタン続行でも動作は同じ（履歴コストだけ増える）と案内する形にした。
- **根拠**: 起動経路（プロンプト実行/ハンドオフ/新チャット）によって結果が変わると、
  利用者は「どのボタンを押すべきか」を暗記させられ、ハーネスの信頼が崩れる
  （ユーザー指摘）。等価性を設計ルールにすれば、どの経路でも同じ動作になり、
  経路の違いは「履歴を引き継ぐか（コスト）」だけになる。implement→test の
  `send: true` は全自動区間の設計意図どおりのため維持。

## D-024: Claude Code / Antigravity対応（自動生成による単一ソース化）

- **判断**: `.github/agents/`, `.github/prompts/`, `.github/skills/`, `.github/hooks/`,
  `AGENTS.md` を唯一の正としたまま、GitHub Copilotに加えてClaude CodeとAntigravityにも
  対応させる。ツール固有の設定は手で三重に書かず、`scripts/generate_agent_tooling.py`
  （stdlibのみ、依存追加なし）で自動生成する。生成物はコミット対象とし、`uv run task
  gen-tooling-check` をCIに追加してドリフト（3ツール間の内容の食い違い）を検出する。
  - **Claude Code**: `CLAUDE.md` に `@AGENTS.md` インポートを1行書くだけ（Claude Codeは
    2026年7月時点でAGENTS.mdをネイティブサポートしていないため。GitHub issueで要望済みだが
    未実装）。真のサブエージェント（design-critic, task-worker, reviewer）は
    `.claude/agents/*.md` として生成する（frontmatterの`tools`をCopilot短縮名から
    Claude Codeのツール名（Read/Edit/Write/Grep/Glob/Bash/TodoWrite/Task等）へ
    マッピング）。一方フェーズの「人格」エージェント（orchestrator/design-gate/
    implement/test/release）はClaude Codeに main thread のペルソナ切替に相当する機能が
    ないため、`.claude/commands/*.md`（スラッシュコマンド）の本文に該当
    `.agent.md` の全文を埋め込み、実行した瞬間にそのエージェントとして振る舞うよう
    指示する形で代替した。Agent Skills（SKILL.md）はGitHub CopilotとClaude Codeで
    **同一のオープン標準**（frontmatterに`name`/`description`必須という共通仕様）と
    確認できたため、`.github/skills/`から`.claude/skills/`へ変換なしでコピーする。
    Hooksは`.claude/settings.json`のJSON構造がCopilotと異なる（`matcher`+`hooks`配列の
    入れ子）が、フックスクリプト自体（`.github/hooks/scripts/*.sh`）のstdin/stdout
    契約（`tool_input.file_path`等の読み取り、`hookSpecificOutput.permissionDecision`
    の出力）は共通と確認できたため、**スクリプトは1つのまま、JSONマニフェストだけ
    ツールごとに用意**する設計にした。
  - **Antigravity**: `AGENTS.md`をプロジェクトルートからネイティブに直接読む（追加設定
    不要、確認済み）。`GEMINI.md`がAntigravity固有の上書き先として公式に用意されている
    ため、そこにサブエージェント代替手順・Terminal Permission Mode推奨設定を記載した。
    `.agent/workflows/*.md`はプレーンMarkdownの手順書という説明のみ確認できたため、
    Claude Codeのcommand生成と同じ「エージェント人格を全文埋め込む」技法を流用して
    生成した。
  - **意図的に実装しなかったもの**: Antigravityは2026年Google I/Oで独自のSubagents/
    Hooks機能が追加されたと発表されているが、本ハーネス作成時点で公式ドキュメント
    （antigravity.google/docs/*）がJavaScript描画のサイトでWebFetchによる直接取得が
    できず、正確な設定ファイル形式・フィールド名を一次情報で確認できなかった。
    このハーネス自身の原則（IRR「`TODO`・未確認の情報を実装根拠にしない」、
    D-009/D-014「AI Dev Kit等の速く変わる外部仕様は公式一次情報で確認してから
    バージョン固定する」）に従い、**未検証のスキーマを推測で実装することはしなかった**。
    代わりに確実に動作するAntigravityの既存機能（AGENTS.mdネイティブ読み込み、
    GEMINI.md、ワークフロー、Terminal Permission Mode）で同等の目的
    （独立レビュー・本番保護）を代替する運用を`GEMINI.md`に明記し、Antigravity公式の
    Subagents/Hooksが安定・文書化された場合に生成対応を追加する旨をTODOとして残した。
  - **ハーネス保護の拡張**: `guard-harness-config-edit.sh`/`.ps1`の保護対象パターンに
    `CLAUDE.md`, `GEMINI.md`, `.claude/agents/`, `.claude/commands/`,
    `.claude/settings.json`, `.agent/workflows/` を追加した（`.claude/skills/`は
    `.github/skills/`のコピーで再生成のたび上書きされるため、既存の`.github/skills/`
    除外方針と合わせて対象外にした）。`.claude/settings.json`の`permissions.deny`にも
    同じパスパターンを二重の安全網として追加した（主たる強制はHooks、permissions.denyは
    補助）。
- **根拠**: 3ツールの設定を手で別々に保守すると、片方だけ更新されて食い違う事故が
  必ず起きる（このハーネス自体がプロンプト/エージェント間の等価性で苦労した経緯が
  D-023にある）。生成方式なら「`.github/`を直せば全ツールに伝播する」という単純な
  運用原則ひとつで一貫性を保証できる。またAntigravityのように仕様がまだ流動的な
  対象について、検証できない機能を実装したと称するのは、このハーネスが設計書に対して
  求めている基準（推測で埋めない、TODOのまま実装根拠にしない）に自ら違反することに
  なるため、確実な部分だけを実装し不確実な部分は明示的にTODO化した。

## D-025: .claude/.agent生成をハイブリッド方式(frontmatter生成+本文は参照ポインタ)へ変更

- **経緯**: D-024で構築した生成方式（`.github/agents/*.agent.md`等の全文を`.claude/commands/`
  `.agent/workflows/`へ埋め込む）について、ユーザーが並行して整備していた別プロジェクト
  `D:\vscode-worspace\ai-manager`（マルチエージェント対応の独立実装）と、それを参考に
  ユーザーがマルチエージェント対応させた`D:\vscode-worspace\CreateAppl`（本ハーネスの
  派生元）を比較する機会があった。両者は`.claude/commands/*.md`・`.agent/workflows/*.md`・
  `.claude/skills/*/SKILL.md`の本文を**全文コピーではなく「正典を読んで実行せよ」という
  数行の参照ポインタのみ**にしていた（例: CreateAppl `.claude/commands/03-design-architecture.md`
  は8行、`.github/agents/design.agent.md`を読んで従うよう指示するだけ）。
- **判断**: 本ハーネスもポインタ方式に切り替える。ただし**frontmatter
  （name/description/tools/allowed-tools）の自動生成とCI検証（`gen-tooling-check`）は維持する**。
  `scripts/generate_agent_tooling.py`の`gen_claude_subagents`/`gen_claude_commands`/
  `gen_claude_skills`/`gen_antigravity_workflows`を、全文埋め込みから
  「frontmatter生成＋固定テンプレートの参照ポインタ本文」に書き換えた。
  生成ファイルは平均130行前後→15〜25行程度に縮小した。
- **根拠（ハイブリッドにした理由）**: ポインタ方式は「本文（手順・ペルソナ）を編集しても
  再生成を忘れるリスクが構造的に無い」という明確な優位性がある（全文埋め込み方式は
  編集のたびに`gen-tooling`再実行が必要で、CIの`--check`はpushするまで気づけない）。
  一方でai-manager/CreateAppl双方とも、(a) frontmatter（特にdescription）の変更は
  手動転記に頼っており自動検証が無い、(b) Skill/Promptを追加・削除したときの
  対応ポインタファイルの作成漏れを検知する仕組みが無い、という弱点を抱えていた。
  本ハーネスの生成スクリプトはCopilotのtools短縮名→Claude Codeツール名への変換が
  そもそも必要（frontmatterは実行時参照に委譲できない、ツール自体がモデル呼び出し前に
  静的パースするメタデータのため）なので、この自動変換ロジックと`--check`によるCI検証は
  そのまま活かし、本文だけポインタ化するのが両者の弱点を打ち消し合う設計になる。
- **副次的な収穫**: CreateApplの`.agent/workflows/`アダプタには「Antigravity IDEは
  プロジェクト内のスクリプトフックを読まない」という**実機検証済み**の記述があった。
  自分はAntigravity公式ドキュメントがJS描画サイトで一次情報を確認できず「要確認」と
  保留していたが、姉妹プロジェクトの実機検証という裏付けが取れたため、`GEMINI.md`と
  生成スクリプトの`.agent/workflows/*.md`アダプタ本文をより確信度の高い書き方に更新した
  （Antigravity独自のSubagents/Hooks機能自体のスキーマは依然未検証のまま。D-024参照）。
- **今後の運用**: `.github/`側の本文編集は再生成不要（常に最新が実行時に読まれる）。
  frontmatter変更、またはSkill/Promptの追加・削除をしたときだけ
  `uv run task gen-tooling`を実行する。判断に迷う場合は常に実行して`--check`で確認すればよい。
