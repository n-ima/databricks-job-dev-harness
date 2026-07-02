"""雛形の単体テスト。実装フェーズで設計ID・受け入れ条件に対応するテストへ置き換える。

テストは docs/02-implementation/traceability.md で設計IDと対応づける。
正常・境界・異常・再実行のうち関係する観点を必ず含める。
"""

from sample_job.main import build_greeting


def test_build_greeting_includes_environment() -> None:
    assert build_greeting("dev") == "sample-job placeholder run on dev"
