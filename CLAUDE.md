@AGENTS.md

<!--
  Claude CodeはAGENTS.mdをネイティブに読み込まないため、このファイルから
  @AGENTS.md インポート構文で読み込んでいる(2026年7月時点。Claude Code側が
  AGENTS.mdをネイティブサポートした場合、このファイルの意義は薄れるが、
  互換性のため残してよい)。

  フェーズ別のエージェント人格は .claude/commands/*.md(スラッシュコマンド実行時に
  そのエージェントとして振る舞う)、独立サブエージェントは .claude/agents/*.md
  (design-critic / task-worker / reviewer。Taskツールで自動的に呼び出される)
  として提供している。いずれも .github/agents/ から自動生成されたものなので、
  変更は .github/agents/ 側で行い、`uv run task gen-tooling` を再実行すること。

  詳細は .claude/README.md を参照。
-->
