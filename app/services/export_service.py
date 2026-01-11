from __future__ import annotations

import csv
from io import StringIO
from typing import Iterable, Mapping


def to_csv_bytes(
    *,
    headers: list[str],
    rows: Iterable[Mapping[str, object]],
) -> bytes:
    """
    Converte rows (dicts) em CSV (UTF-8) e retorna bytes.
    """
    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {k: ("" if row.get(k) is None else row.get(k)) for k in headers}
        )
    return buf.getvalue().encode("utf-8")
