from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Entry:
    name: str
    efn: str
    session_date: date
    duration_minutes: int

    @property
    def key(self) -> str:
        return f"{self.efn}|{self.session_date.isoformat()}"


def load_entries(path: Path) -> list[Entry]:
    entries: list[Entry] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"name", "efn", "date", "duration_minutes"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns: {sorted(missing)}")
        for row_num, row in enumerate(reader, start=2):
            entries.append(
                Entry(
                    name=row["name"].strip(),
                    efn=row["efn"].strip(),
                    session_date=date.fromisoformat(row["date"].strip()),
                    duration_minutes=int(row["duration_minutes"]),
                )
            )
    return entries
