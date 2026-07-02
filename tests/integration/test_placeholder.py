"""結合テストの雛形。

デプロイ済みのDatabricksリソース（devターゲット）に対して実行するテストは
必ず `integration` markerを付け、`uv run task integration` で実行する。
production dataへは接続しない。合成データ・devカタログのみを使う。
"""

import pytest


@pytest.mark.integration
def test_placeholder() -> None:
    pytest.skip("実装フェーズでdevターゲットのJob実行結果を検証するテストに置き換える")
