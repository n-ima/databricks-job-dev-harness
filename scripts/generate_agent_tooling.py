#!/usr/bin/env python3
"""Databricksハーネスの唯一の正(.github/agents, .github/prompts, .github/skills,
.github/hooks, AGENTS.md)から、Claude Code(.claude/)とAntigravity(.agent/)向けの
設定ファイルを生成する。

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
      オープン標準(SKILL.md)のため .claude/skills/ へそのままコピーする。
      hooksは .claude/settings.json (matcher + hooks配列の入れ子構造、GitHub Copilotとは形が違う)。
    - Antigravity: AGENTS.mdをネイティブに直接読む(追加作業不要)。GEMINI.mdがAntigravity固有の
      上書き先。.agent/workflows/*.md はプレーンMarkdownの手順書。
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
        frontmatter, body = split_frontmatter(read(src))
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
        content = gen_header([f".github/agents/{name}.agent.md"]) + fm + body.strip() + "\n"
        write_generated(ROOT / ".claude" / "agents" / f"{name}.md", content, outputs)


# ---------- Claude Code: フェーズコマンド (.claude/commands/*.md) ----------

PHASE_TRANSITION_NOTE = (
    "\n\n---\n\n"
    "## フェーズ遷移（Claude Codeでの操作）\n\n"
    "GitHub Copilotのハンドオフボタンに相当する操作です。次のフェーズに進む場合は、"
    "**新しいチャットを開いて** 対応するスラッシュコマンドを実行してください。\n"
    "対応表は [README.md](../../README.md) の\n"
    "「フェーズとエージェント／プロンプト対応表」を参照してください。\n\n"
    "サブエージェント（design-critic / task-worker / reviewer）の呼び出しは、\n"
    "上記の指示に従って必要なタイミングで Task ツールを使い自動的に行われます。\n"
    "人が明示的に呼び出す必要はありません。\n"
)


def gen_claude_commands(outputs: dict[Path, str]) -> None:
    prompts_dir = ROOT / ".github" / "prompts"
    for prompt_path in sorted(prompts_dir.glob("*.prompt.md")):
        stem = prompt_path.stem.removesuffix(".prompt")
        frontmatter, body = split_frontmatter(read(prompt_path))
        agent_name = get_scalar(frontmatter, "agent")
        description = get_scalar(frontmatter, "description") or ""
        if not agent_name:
            continue
        agent_src = ROOT / ".github" / "agents" / f"{agent_name}.agent.md"
        agent_frontmatter, agent_body = split_frontmatter(read(agent_src))
        agent_tools = map_tools(get_tools(agent_frontmatter))
        fm = f"---\ndescription: {description}\nallowed-tools: {', '.join(agent_tools)}\n---\n\n"
        persona = (
            f"# あなたはこのプロジェクト専属の「{agent_name}」エージェントとして振る舞います\n\n"
            "以降このセッションでは、次の人格定義に従って行動してください"
            f"（生成元: `.github/agents/{agent_name}.agent.md`）。\n\n"
            f"{agent_body.strip()}\n\n"
            "---\n\n"
            f"## このコマンドの手順（生成元: `.github/prompts/{prompt_path.name}`）\n\n"
            f"{body.strip()}\n"
        )
        content = (
            gen_header(
                [f".github/prompts/{prompt_path.name}", f".github/agents/{agent_name}.agent.md"]
            )
            + fm
            + persona
            + PHASE_TRANSITION_NOTE
        )
        write_generated(ROOT / ".claude" / "commands" / f"{stem}.md", content, outputs)


# ---------- Claude Code: Skills (.claude/skills/ — .github/skills/のコピー) ----------


def gen_claude_skills(outputs: dict[Path, str]) -> None:
    src_root = ROOT / ".github" / "skills"
    for skill_md in sorted(src_root.glob("*/SKILL.md")):
        rel = skill_md.relative_to(src_root)
        content = read(skill_md)
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
    """# .claude/ — Claude Code向け設定（自動生成）

このディレクトリの中身は `.github/agents/`, `.github/prompts/`, `.github/skills/`,
`.github/hooks/` から `scripts/generate_agent_tooling.py` によって自動生成される。
**直接編集しない。** 編集は `.github/` 側で行い、以下を再実行すること。

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
        "| Claude Codeのサブエージェント（`Task`ツールで自動的に呼び出される） |\n"
        "| `commands/*.md` "
        "| `.github/prompts/*.prompt.md` + 対応する `.github/agents/*.agent.md` "
        "| スラッシュコマンド。実行するとそのフェーズのエージェント人格を引き継ぐ |\n"
        "| `skills/*/SKILL.md` "
        "| `.github/skills/*/SKILL.md` "
        "| Agent Skills（GitHub Copilotと同一のオープン標準。コピーそのまま） |\n"
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
        frontmatter, body = split_frontmatter(read(prompt_path))
        agent_name = get_scalar(frontmatter, "agent")
        description = get_scalar(frontmatter, "description") or ""
        if not agent_name:
            continue
        agent_src = ROOT / ".github" / "agents" / f"{agent_name}.agent.md"
        _, agent_body = split_frontmatter(read(agent_src))
        content = (
            gen_header(
                [f".github/prompts/{prompt_path.name}", f".github/agents/{agent_name}.agent.md"]
            )
            + f"# {stem}\n\n{description}\n\n---\n\n"
            + f"## エージェント人格（生成元: `.github/agents/{agent_name}.agent.md`）\n\n"
            + f"{agent_body.strip()}\n\n---\n\n"
            + f"## 手順（生成元: `.github/prompts/{prompt_path.name}`）\n\n{body.strip()}\n"
            + "\n---\n\n## フェーズ遷移\n\n"
            + "次のフェーズに進む場合は、新しいエージェントセッション（Manager Surface）で"
            + "対応するワークフローを実行してください。対応表は README.md を参照してください。\n"
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
