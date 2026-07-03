---
name: databricks-env-setup
description: 開発環境のセットアップと診断の手順。Databricks CLI/uv/VS Code拡張の導入、認証プロファイル作成、AI Dev KitとDatabricks Agent Skills(aitools)の導入・バージョン固定、動作確認(doctorチェック)に使う。
---

# Databricks開発環境セットアップスキル

## 必須ツール

| ツール | 確認コマンド | 備考 |
|---|---|---|
| Databricks CLI (新CLI) | `databricks --version` | Bundles対応版（v0.218+）。旧`databricks-cli`(pip)と混同しない |
| uv | `uv --version` | Python環境・タスクランナー |
| Python 3.11/3.12 | `uv python list` | `pyproject.toml` の `requires-python` に一致 |
| VS Code拡張 | - | `.vscode/extensions.json` の推奨（Databricks拡張・Copilot・Ruff等） |

## セットアップ手順

```bash
uv sync --all-groups                                  # 依存導入
uv run task check                                     # ハーネス自体の健全性確認
databricks auth login --host https://<dev-workspace>  # devプロファイル作成（OAuth）
databricks auth profiles                              # プロファイル確認
databricks bundle validate -t dev                     # Bundle疎通確認
```

- 認証はOAuth（`auth login`）を標準とし、PATは使わない。
- `.env` はコミットしない（`.env.example` を参照）。
- staging/prod用プロファイルは開発機に置かない運用を推奨
  （CI/CDのservice principal + OIDCに委ねる。開発者IDにprod書き込み権限を与えない）。

## プロジェクトリネーム（`sample_job` → 案件名）

雛形のままの名前を案件名へ変更する際は、以下を**すべて**一貫して変更する
（1箇所でも漏れるとwheelビルドまたはJob実行が壊れる）。

| ファイル | 変更箇所 |
|---|---|
| `pyproject.toml` | `project.name`、`project.scripts`、`tool.hatch.build.targets.wheel.packages`、`tool.pytest.ini_options.addopts` の `--cov=`、`tool.mypy.packages` |
| `databricks.yml` | `bundle.name`、devターゲットの `schema` 変数 |
| `resources/main.job.yml` | `name`、`python_wheel_task.package_name` |
| `src/sample_job/` | ディレクトリ名 |
| `tests/unit/test_main.py` | import文 |
| `docs/01-design/environment.md` | Bundle名の欄 |

変更後に `uv sync --all-groups && uv run task check && uv run task build` で検証する。
リネームはファイル移動・コマンド実行を伴うため、`execute` 権限を持つエージェント
（implement / task-worker）または人間が行う（design-gateは決定の記録まで）。

## Databricks Agent Skills / AI Dev Kit の導入（推奨）

Databricks公式のAIツール群。**導入時は公式一次情報（docs.databricks.com の
Agent Skillsページ、github.com/databricks-solutions/ai-dev-kit）で最新の手順を
確認すること**（活発に更新されており、コマンド・スキル構成が変わっている可能性がある）。

1. **Databricks Agent Skills**（CLI同梱の `aitools` コマンド群）: 製品構文・
   ベストプラクティスの一般知識をエージェントに供給するMarkdownスキル集。
   2026年7月時点の構成: `databricks-core`（基本）/ `databricks-dabs`（Bundle）/
   `databricks-jobs`（Job開発）/ `databricks-pipelines`（DLT）/ `databricks-apps` /
   `databricks-lakebase` / `databricks-model-serving` / `databricks-serverless-migration`。
   このハーネスでは **`databricks-core` + `databricks-dabs` + `databricks-jobs`** が中核。

   ```bash
   databricks aitools install --scope project   # 導入(CLIが対応エージェントを自動検出)
   databricks aitools list                      # 導入済みスキルの確認
   databricks aitools update --check --scope project   # 更新の事前確認(適用は専用PRで)
   ```

   スコープはグローバル（`~/.databricks/aitools/skills/`、既定）とプロジェクトが選べる。
   チームで差が出ないよう**projectスコープ + 専用PRでのレビュー**を標準とする。
2. **AI Dev Kit（MCPサーバー等）**: ワークスペース操作（テーブル・スキーマ参照、
   Job実行状態の確認、SQL実行など）をエージェントのツールとして供給する。
   これを入れると「テーブルのスキーマを見ながら実装」「Job失敗のrunを直接調査」が
   Chat内で完結し、CLI往復が減る。導入する場合:
   - `.vscode/mcp.json.example` を `mcp.json` にコピーし、公式READMEの導入コマンドで埋める。
   - バージョン・コミット・チェックサムを固定し、`docs/01-design/environment.md` に記録する。
   - MCPに与えるDatabricks権限は開発用identity（devプロファイル）の最小権限とする。
     **MCP経由でもstaging/prodへ書き込める権限を与えない**（Hooksはネイティブツールの
     コマンドしか検査できないため、MCPツールの権限は接続元identityで絞るしかない）。
   - VS CodeのMCP server trust・ツール有効化は開発者が内容を確認して明示的に行う。
   - マシン固有の `.vscode/mcp.json` はコミットしない（`.gitignore` 済み）。
3. **VS Code Databricks拡張**（`databricks.databricks`）: Bundleターゲットの切替・
   デプロイ・実行がGUIから可能。またdatabricks-connectによるローカルからの
   リモートSpark実行・デバッグに対応する。エージェントの自動区間はCLIを正とし、
   拡張は人の確認・デバッグ用として使い分ける。

導入したSkillsは製品構文・一般的手順の根拠に使い、**案件固有の設計
（catalog名・権限・SLA・業務ルール）の根拠には使わない**（正は `docs/01-design/`）。

## 診断（doctorチェック）

環境が疑わしいときは次を順に確認する。

1. `databricks --version` — 新CLIか（`Databricks CLI v0.2xx`形式）
2. `databricks auth profiles` — devプロファイルが有効か
3. `databricks current-user me --profile dev` — 認証が通るか
4. `uv run task check` — ローカルツールチェーンが揃っているか
5. `databricks bundle validate -t dev` — Bundle定義が壊れていないか
6. Copilot Chat: Customization Diagnostics（またはレスポンスのReferences）で
   `AGENTS.md`・該当instructionsが読み込まれているか
7. Hooks: OutputパネルのGitHub Copilot Chat Hooksでロード状態を確認
   （Preview機能のため発火しない環境がある）
