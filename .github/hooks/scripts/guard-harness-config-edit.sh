#!/usr/bin/env bash
# PreToolUse hook: ハーネス自体の運用ルール(エージェント定義/フック/AGENTS.md等)への
# 無断編集をdenyする。プロンプトインジェクションによる自己権限昇格・ガードレール解除を防ぐ。
# 注意: .github/skills/ は動的なSkill追加を許容するため対象外にしている。
# .claude/agents,commands,settings.json / .agent/workflows / CLAUDE.md / GEMINI.md は
# .github/ 側から自動生成される(scripts/generate_agent_tooling.py)。生成物も同様に保護する。
# .claude/skills/ は .github/skills/ のコピーで再生成のたび上書きされるため対象外にしている。
input=$(cat)
file=$(printf '%s' "$input" | grep -oE '"(file_path|filePath|path)"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed -E 's/.*:[[:space:]]*"([^"]*)"/\1/')

protected_pattern='(^|/)\.github/agents/|(^|/)\.github/hooks/|(^|/)\.github/workflows/|(^|/)AGENTS\.md$|(^|/)CLAUDE\.md$|(^|/)GEMINI\.md$|(^|/)plugin\.json$|(^|/)\.vscode/settings\.json$|(^|/)\.claude/agents/|(^|/)\.claude/commands/|(^|/)\.claude/settings\.json$|(^|/)\.agent/workflows/'

if [[ -n "$file" ]] && printf '%s' "$file" | grep -Eiq "$protected_pattern"; then
  printf '%s\n' '{"continue": true, "hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": "ハーネスの運用ルール自体(agents/hooks/workflows/AGENTS.md/CLAUDE.md/GEMINI.md/plugin.json/settings.json、および.claude・.agentの生成物)はエージェントが自動で書き換えません。変更が必要な場合は.github/側を人間が直接編集し、scripts/generate_agent_tooling.pyを再実行してください。"}}'
else
  printf '%s\n' '{"continue": true}'
fi
