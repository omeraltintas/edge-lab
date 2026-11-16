"""Deterministik yuk testi verisi.

Kodlar bilerek sabit: `seed000`..`seed999` ve `hotlink`. Boylece k6 tarafi
kodu tahmin edebilir ve iki kosu arasinda ayni satirlar kullanilir.

    python -m edge_lab.seed            # 1000 + 1
    python -m edge_lab.seed --count 50
"""

import argparse

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from edge_lab.db import SessionLocal
from edge_lab.models import Link

OWNER_KEY = "seed-owner"
HOT_CODE = "hotlink"


def code_for(index: int) -> str:
    return f"seed{index:03d}"


def build_rows(count: int) -> list[dict[str, str]]:
    rows = [
        {
            "code": code_for(i),
            "url": f"https://example.com/p/{i}",
            "owner_key": OWNER_KEY,
        }
        for i in range(count)
    ]
    rows.append(
        {
            "code": HOT_CODE,
            "url": "https://example.com/hot",
            "owner_key": OWNER_KEY,
        }
    )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="edge-lab seed")
    parser.add_argument("--count", type=int, default=1000)
    args = parser.parse_args()

    rows = build_rows(args.count)
    statement = pg_insert(Link).values(rows).on_conflict_do_nothing(index_elements=["code"])

    with SessionLocal() as session:
        session.execute(statement)
        session.commit()
        total = session.scalar(select(func.count()).select_from(Link))

    print(f"seeded={len(rows)} total_links={total} hot_code={HOT_CODE}")


if __name__ == "__main__":
    main()
