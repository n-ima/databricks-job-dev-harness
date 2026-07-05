#!/usr/bin/env python3
"""Databricksハーネスの唯一の正(.github/agents, .github/prompts, .github/skills,
.github/hooks, AGENTS.md)から、Claude Code(.claude/)とAntigravity(.agent/)向けの
「薄いアダプタ」ファイルを生成する。

## 方式（ハイブリッド: frontmatter生成 + 本文は参照ポインタ）

- **frontmatter（name/description/tools等）は自動生成する。** ツールがモデル呼び出し前に
  静的パースするメタデータのため実行時参照に委譲できず、Copilot短縮名からClaude Code
  ツール名へのマッピングもここでしか行えない。
- **本文は正典への参照ポインタのみを生成する**（全文埋め込みはしない）。
  「`.github/agents/<name>.agent.md` を読み、それに従って行動せよ」という短い指示文だけを
  置くことで、本文を編集しても再生成せずに常に最新の内容が実行時に読まれる
  （姉妹ハーネス CreateAppl / ai-manager プロジェクトの実装を参考に採用した設計。
  詳細は DECISIONS.md D-025）。
- 一方で「新しいSkill/Promptを追加したのに対応ファイルの作成を忘れる」事故は
  ポインタ方式だけでは防げないため、本スクリプト+`--check`によるCI検証は維持する
  （`.github/`側の実ファイルを毎回スキャンして期待される生成物を計算するため、
  追加・削除も自動的に検知できる）。

3ツールの内容が食い違う(ドリフトする)ことを防ぐため、Claude Code/Antigravity向けの
ファイルは直接編集しない。編集は必ず .github/ 側で行い、本スクリプトを再実行する。

使い方:
    uv run python scripts/generate_agent_tooling.py          # 生成して書き込む
    uv run python scripts/generate_agent_tooling.py --check  # 生成結果と現状の差分を検査(CI用)

対応状況の前提(2026年7月時点、公式一次情報で確認済み):
    - GitHub Copilot (VS Code): .github/agents, .github/prompts, .github/skills, .github/hooks を
      ネイティブに読む(このハーネスの元々の実装)。
    - Claude Code: AGENTS.mdはネイティブ非対応のため CLAUDE.md から `@AGENTS.md` でインポートする。
      サブエージェントは .claude/agents/*.md、Agent SkillsはGitHub Copilotと同一の
      オープン標準(SKILL.md)。hooksは .claude/settings.json
      (matcher + hooks配列の入れ子構造、GitHub Copilotとは形が違う)。
    - Antigravity: AGENTS.mdをネイティブに直接読む(追加作業不要)。GEMINI.mdがAntigravity固有の
      上書き先。.agent/workflows/*.md はプレーンMarkdownの手順書。
      Antigravity IDEはプロジェクト内のスクリプトフックを読まない
      （姉妹プロジェクトCreateApplの実機検証で確認済み）。物理ガードレールはGEMINI.md記載の
      Terminal Permission Mode / GUI Deny Listで代替する。
      **Antigravity独自のSubagents/Hooks機能(2026 I/Oで追加)は本スクリプト作成時点で
      公式ドキュメントのスキーマを検証できなかったため生成対象に含めていない。
      GEMINI.mdに要確認事項として明記してある。**
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN_MARKER = "GENERATED FILE"

# Copilotのtools短縮名 -> Claude Codeのツール名(複数対応可)。
# 'agent'(サブエージェント呼び出し)はClaude Codeの Task ツールに対応する。
TOOL_MAP: dict[str, list[str]] = {
    "read": ["Read"],
    "edit": ["Edit", "Write"],
    "search": ["Grep", "Glob"],
    "execute": ["Bash"],
    "todo": ["TodoWrite"],
    "agent": ["Task"],
    "web": ["WebFetch", "WebSearch"],
    "playwright": [],
}

SUBAGENTS = ["design-critic", "task-worker", "reviewer"]


def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"生成元ファイルが見つかりません: {path}")
    return path.read_text(encoding="utf-8")


def split_frontmatter(text: str) -> tuple[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("frontmatter(--- ... ---)が見つかりません")
    return m.group(1), m.group(2)


def get_scalar(frontmatter: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*'([^']*)'\s*$", frontmatter, re.MULTILINE)
    if m:
        return m.group(1)
    m = re.search(rf"^{re.escape(key)}:\s*([^\n\[{{][^\n]*)$", frontmatter, re.MULTILINE)
    return m.group(1).strip() if m else None


def get_tools(frontmatter: str) -> list[str]:
    m = re.search(r"^tools:\s*\[(.*?)\]\s*$", frontmatter, re.MULTILINE)
    if not m:
        return []
    return [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]


def map_tools(copilot_tools: list[str]) -> list[str]:
    out: list[str] = []
    for t in copilot_tools:
        for claude_tool in TOOL_MAP.get(t, []):
            if claude_tool not in out:
                out.append(claude_tool)
    return out


def gen_header(sources: list[str], comment_style: str = "md") -> str:
    src = ", ".join(sources)
    if comment_style == "md":
        return (
            f"<!-- {GEN_MARKER}。編集しないでください。\n"
            f"     生成元: {src}\n"
            f"     再生成: uv run task gen-tooling -->\n\n"
        )
    return ""


def write_generated(path: Path, content: str, outputs: dict[Path, str]) -> None:
    outputs[path] = content


# ---------- Claude Code: サブエージェント (.claude/agents/*.md) ----------


def gen_claude_subagents(outputs: dict[Path, str]) -> None:
    for name in SUBAGENTS:
        src = ROOT / ".github" / "agents" / f"{name}.agent.md"
        frontmatter, _ = split_frontmatter(read(src))
        description = get_scalar(frontmatter, "description") or ""
        tools = map_tools(get_tools(frontmatter))
        model = get_scalar(frontmatter, "model") or "inherit"
        tools_line = ", ".join(tools)
        fm = (
            "---\n"
            f"name: {name}\n"
            f"description: {description}\n"
            f"tools: {tools_line}\n"
            f"model: {model}\n"
            "---\n\n"
        )
        pointer = (
            f"あなたは {name} サブエージェントです。このファイルは薄いアダプタであり、\n"
            f"振る舞いの正は `.github/agents/{name}.agent.md` にあります。\n\n"
            f"最初に必ず `.github/agents/{name}.agent.md` を読み、その役割定義・観点・"
            "出力形式・制約（読み取り専用かどうか等）に厳密に従って作業してください。\n"
        )
        content = gen_header([f".github/agents/{name}.agent.md"]) + fm + pointer
        write_generated(ROOT / ".claude" / "agents" / f"{name}.md", content, outputs)


# ---------- Claude Code: フェーズコマンド (.claude/commands/*.md) ----------


def gen_claude_commands(outputs: dict[Path, str]) -> None:
    prompts_dir = ROOT / ".github" / "prompts"
    for prompt_path in sorted(prompts_dir.glob("*.prompt.md")):
        stem = prompt_path.stem.removesuffix(".prompt")
        frontmatter, _ = split_frontmatter(read(prompt_path))
        agent_name = get_scalar(frontmatter, "agent")
        description = get_scalar(frontmatter, "description") or ""
        if not agent_name:
            continue
        agent_src = ROOT / ".github" / "agents" / f"{agent_name}.agent.md"
        agent_frontmatter, _ = split_frontmatter(read(agent_src))
        agent_tools = map_tools(get_tools(agent_frontmatter))
        fm = f"---\ndescription: {description}\nallowed-tools: {', '.join(agent_tools)}\n---\n\n"
        pointer = (
            "このコマンドは薄いアダプタです。振る舞いの正は参照先にあります。\n\n"
            f"1. `.github/agents/{agent_name}.agent.md` を読み、その役割定義に従って"
            "この会話のロールを設定してください。\n"
            f"2. その上で `.github/prompts/{prompt_path.name}` の本文の指示を実行してください。\n"
            "3. 役割定義の中の `runSubagent` は、Claude Code では **Task ツール**で\n"
            "   `.claude/agents/` の同名サブエージェント"
            "（design-critic / task-worker / reviewer）を\n"
            "   呼ぶことに読み替えてください。ハンドオフボタンは存在しないため、"
            "フェーズ移行の案内は\n"
            "   「新しいセッションで /<コマンド名> を実行」の形にしてください。\n"
        )
        content = (
            gen_header(
                [f".github/prompts/{prompt_path.name}", f".github/agents/{agent_name}.agent.md"]
            )
            + fm
            + pointer
        )
        write_generated(ROOT / ".claude" / "commands" / f"{stem}.md", content, outputs)


# ---------- Claude Code: Skills (.claude/skills/*/SKILL.md — 薄いポインタ) ----------


def gen_claude_skills(outputs: dict[Path, str]) -> None:
    src_root = ROOT / ".github" / "skills"
    for skill_md in sorted(src_root.glob("*/SKILL.md")):
        rel = skill_md.relative_to(src_root)
        name = rel.parent.name
        frontmatter, _ = split_frontmatter(read(skill_md))
        skill_name = get_scalar(frontmatter, "name") or name
        description = get_scalar(frontmatter, "description") or ""
        fm = f"---\nname: {skill_name}\ndescription: {description}\n---\n\n"
        pointer = (
            f"# {skill_name}（ポインタ）\n\n"
            f"このスキルの手順の正典は `.github/skills/{name}/SKILL.md` にある。\n"
            "それを読み、記載された手順を忠実に実行すること。手順を編集する場合も"
            "正典側を直す\n"
            "（このファイルはClaude Codeが `.claude/skills/` しか探索しないために"
            "置いてある薄いポインタである）。\n"
        )
        content = gen_header([f".github/skills/{name}/SKILL.md"]) + fm + pointer
        write_generated(ROOT / ".claude" / "skills" / rel, content, outputs)


# ---------- Claude Code: hooks + permissions (.claude/settings.json) ----------

CLAUDE_SETTINGS_JSON = """{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PROJECT_DIR}/.github/hooks/scripts/guard-template-edit.sh",
            "shell": "bash",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "bash ${CLAUDE_PROJECT_DIR}/.github/hooks/scripts/guard-harness-config-edit.sh",
            "shell": "bash",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PROJECT_DIR}/.github/hooks/scripts/guard-dangerous-git.sh",
            "shell": "bash",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "bash ${CLAUDE_PROJECT_DIR}/.github/hooks/scripts/guard-databricks-prod.sh",
            "shell": "bash",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Edit|Write|Bash|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PROJECT_DIR}/.github/hooks/scripts/guard-secret-leak.sh",
            "shell": "bash",
            "timeout": 5
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PROJECT_DIR}/.github/hooks/scripts/inject-progress.sh",
            "shell": "bash",
            "timeout": 5
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PROJECT_DIR}/.github/hooks/scripts/inject-progress.sh PreCompact",
            "shell": "bash",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PROJECT_DIR}/.github/hooks/scripts/warn-stale-gate.sh",
            "shell": "bash",
            "timeout": 5
          }
        ]
      }
    ]
  },
  "permissions": {
    "deny": [
      "Edit(.github/agents/**)",
      "Write(.github/agents/**)",
      "Edit(.github/hooks/**)",
      "Write(.github/hooks/**)",
      "Edit(.github/workflows/**)",
      "Write(.github/workflows/**)",
      "Edit(.claude/agents/**)",
      "Edit(.claude/commands/**)",
      "Edit(.claude/settings.json)",
      "Edit(.agent/workflows/**)",
      "Edit(AGENTS.md)",
      "Edit(CLAUDE.md)",
      "Edit(GEMINI.md)",
      "Edit(plugin.json)",
      "Edit(databricks.yml)",
      "Edit(resources/**)",
      "Write(resources/**)"
    ]
  }
}
"""
# 補足: このpermissions.denyはHooksを補強する二重の安全網であり、Hooks(上記PreToolUse)が
# 主たる強制手段。.claude/skills/ は .github/skills/ のコピーで再生成のたびに上書きされる
# ため、あえてdenyに含めない(動的なSkill追加を許容する既存方針と合わせている)。


def gen_claude_settings(outputs: dict[Path, str]) -> None:
    write_generated(ROOT / ".claude" / "settings.json", CLAUDE_SETTINGS_JSON, outputs)


CLAUDE_README = (
    """# .claude/ — Claude Code向け薄いアダプタ（自動生成）

このディレクトリの中身は `.github/agents/`, `.github/prompts/`, `.github/skills/`,
`.github/hooks/` から `scripts/generate_agent_tooling.py` によって自動生成される。
**直接編集しない。** 編集は `.github/` 側で行うこと。

frontmatter（name/description/tools等）は生成時に転写されるため、これらを
変更した場合は再生成が必要。**本文は正典への参照ポインタのみ**（「`.github/agents/...`を
読んで従え」という指示）なので、本文（手順・ペルソナの中身）を変更しただけなら
再生成しなくても常に最新が実行時に読まれる。ただしSkill/Promptの**追加・削除**は
対応するポインタファイルの生成/削除が要るため、いずれの変更後も次を実行しておくと安全。

```bash
uv run task gen-tooling         # 生成
uv run task gen-tooling-check   # 生成結果と現状が一致しているか検査(CIで実行)
```

| ファイル/ディレクトリ | 生成元 | 役割 |
|---|---|---|
"""
    + (
        "| `agents/*.md` "
        "| `.github/agents/{design-critic,task-worker,reviewer}.agent.md` "
        "| Claude Codeのサブエージェント（`Task`ツールで自動的に呼び出される。薄いポインタ） |\n"
        "| `commands/*.md` "
        "| `.github/prompts/*.prompt.md` + 対応する `.github/agents/*.agent.md` "
        "| スラッシュコマンド（薄いポインタ。実行時に生成元を読みに行く） |\n"
        "| `skills/*/SKILL.md` "
        "| `.github/skills/*/SKILL.md` "
        "| Agent Skills（GitHub Copilotと同一のオープン標準。frontmatterのみ転写、本文は薄いポインタ） |\n"
        "| `settings.json` "
        "| `.github/hooks/*.json` + `scripts/` "
        "| Hooks（ゲート・本番保護）+ 補助的なpermissions.deny |\n"
    )
    + """
個人用の上書きは `.claude/settings.local.json`（gitignore対象）に置く。
"""
)


# ---------- Antigravity: workflows (.agent/workflows/*.md) ----------


def gen_antigravity_workflows(outputs: dict[Path, str]) -> None:
    prompts_dir = ROOT / ".github" / "prompts"
    for prompt_path in sorted(prompts_dir.glob("*.prompt.md")):
        stem = prompt_path.stem.removesuffix(".prompt")
        frontmatter, _ = split_frontmatter(read(prompt_path))
        agent_name = get_scalar(frontmatter, "agent")
        description = get_scalar(frontmatter, "description") or ""
        if not agent_name:
            continue
        agent_src = ROOT / ".github" / "agents" / f"{agent_name}.agent.md"
        assert agent_src.exists(), f"参照先エージェントが見つかりません: {agent_src}"
        fm = f"---\ndescription: {description}\n---\n\n"
        pointer = (
            "このワークフローは薄いアダプタです。振る舞いの正は参照先にあります。\n\n"
            f"1. `.github/agents/{agent_name}.agent.md` を読み、その役割定義に従って"
            "振る舞ってください。\n"
            f"2. その上で `.github/prompts/{prompt_path.name}` の本文の指示を実行してください。\n"
            "3. 役割定義の中の `runSubagent`（独立コンテキストでのレビュー・実装分離）は、\n"
            "   Antigravity では **Agent Manager で別のエージェント会話として実行**し、\n"
            "   結果を受け取って続行することに読み替えてください（同一会話で続ける場合は、\n"
            "   独立性が失われることをユーザーに伝えたうえで行うこと）。\n"
            "   ハンドオフボタンは存在しないため、フェーズ移行の案内は\n"
            "   「新しいエージェント会話で /<ワークフロー名> を実行」の形にしてください。\n"
            "4. フック（機械的ガードレール）はこの環境では発火しません（Antigravity IDEは"
            "プロジェクト内の\n"
            "   スクリプトフックを読まない・姉妹プロジェクトの実機検証で確認済み）。"
            "AGENTS.md の指示レベルのルール\n"
            "   （テンプレート直接編集の禁止・push/tag等の事前確認・シークレット非記載）を"
            "自分の判断で\n"
            "   厳守してください。機械的な保護が必要な場合、ユーザーに Terminal Permission Mode /"
            " GUI Deny List\n"
            "   への危険コマンド登録を案内してください（詳細は GEMINI.md）。\n"
        )
        content = (
            gen_header(
                [f".github/prompts/{prompt_path.name}", f".github/agents/{agent_name}.agent.md"]
            )
            + fm
            + pointer
        )
        write_generated(ROOT / ".agent" / "workflows" / f"{stem}.md", content, outputs)


# ---------- 実行 ----------


def collect_outputs() -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    gen_claude_subagents(outputs)
    gen_claude_commands(outputs)
    gen_claude_skills(outputs)
    gen_claude_settings(outputs)
    write_generated(ROOT / ".claude" / "README.md", CLAUDE_README, outputs)
    gen_antigravity_workflows(outputs)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="書き込まず、現状との差分だけ検査する")
    args = parser.parse_args()

    outputs = collect_outputs()

    if args.check:
        mismatches: list[Path] = []
        for path, content in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                mismatches.append(path)
        if mismatches:
            print("生成結果が最新ではありません。以下を再生成してください:")
            for p in mismatches:
                print(f"  - {p.relative_to(ROOT)}")
            print("\n実行: uv run task gen-tooling")
            return 1
        print(f"OK: {len(outputs)}件の生成ファイルは最新です。")
        return 0

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"生成しました: {len(outputs)}件")
    for path in outputs:
        print(f"  - {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
