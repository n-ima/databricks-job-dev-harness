"""Jobエントリーポイントの雛形。

実装フェーズで設計IDに対応するモジュールへ置き換える。
業務ロジックは可能な限りSpark非依存の純粋関数に分離し、tests/unit/でテストする。
"""

import argparse


def build_greeting(environment: str) -> str:
    """Spark非依存の純粋関数の例。業務ルールはこの形で分離する。"""
    return f"sample-job placeholder run on {environment}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", default="dev")
    parser.add_argument("--catalog", default="")
    parser.add_argument("--schema", default="")
    args, _ = parser.parse_known_args()
    print(build_greeting(args.environment))


if __name__ == "__main__":
    main()
