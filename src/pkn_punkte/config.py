from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class LoginSelectors:
    username: str
    password: str
    submit: str
    success_marker: str


@dataclass(frozen=True)
class EntrySelectors:
    vnr: str
    date: str
    duration_minutes: str
    participant_efn: str
    participant_name: str
    submit: str
    confirmation_marker: str


@dataclass(frozen=True)
class Selectors:
    login: LoginSelectors
    entry: EntrySelectors


@dataclass(frozen=True)
class Portal:
    login_url: str
    entry_url: str


@dataclass(frozen=True)
class Timing:
    min_action_delay_sec: float
    max_action_delay_sec: float
    page_timeout_ms: int


@dataclass(frozen=True)
class Paths:
    input_csv: Path
    state_file: Path
    log_file: Path
    screenshots_dir: Path


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str


@dataclass(frozen=True)
class Config:
    portal: Portal
    vnr: str
    selectors: Selectors
    timing: Timing
    paths: Paths
    credentials: Credentials


def _load_credentials() -> Credentials:
    load_dotenv()
    username = os.environ.get("PKN_USERNAME", "").strip()
    password = os.environ.get("PKN_PASSWORD", "").strip()

    if not password:
        service = os.environ.get("PKN_KEYRING_SERVICE", "").strip()
        user = os.environ.get("PKN_KEYRING_USER", "").strip() or username
        if service and user:
            try:
                import keyring  # type: ignore[import-not-found]
            except ImportError as exc:
                raise RuntimeError(
                    "PKN_KEYRING_SERVICE set but 'keyring' not installed. "
                    "Install with: pip install pkn-punkte[keychain]"
                ) from exc
            password = keyring.get_password(service, user) or ""

    if not username or not password:
        raise RuntimeError(
            "Missing credentials. Set PKN_USERNAME and PKN_PASSWORD in .env "
            "or configure PKN_KEYRING_SERVICE/PKN_KEYRING_USER."
        )
    return Credentials(username=username, password=password)


def load_config(path: Path) -> Config:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))

    portal = Portal(
        login_url=raw["portal"]["login_url"],
        entry_url=raw["portal"].get("entry_url", "") or "",
    )

    login = raw["selectors"]["login"]
    entry = raw["selectors"]["entry"]
    selectors = Selectors(
        login=LoginSelectors(
            username=login["username"],
            password=login["password"],
            submit=login["submit"],
            success_marker=login.get("success_marker", "") or "",
        ),
        entry=EntrySelectors(
            vnr=entry.get("vnr", "") or "",
            date=entry.get("date", "") or "",
            duration_minutes=entry.get("duration_minutes", "") or "",
            participant_efn=entry.get("participant_efn", "") or "",
            participant_name=entry.get("participant_name", "") or "",
            submit=entry.get("submit", "") or "",
            confirmation_marker=entry.get("confirmation_marker", "") or "",
        ),
    )

    t = raw["timing"]
    timing = Timing(
        min_action_delay_sec=float(t["min_action_delay_sec"]),
        max_action_delay_sec=float(t["max_action_delay_sec"]),
        page_timeout_ms=int(t["page_timeout_ms"]),
    )

    p = raw["paths"]
    paths = Paths(
        input_csv=Path(p["input_csv"]),
        state_file=Path(p["state_file"]),
        log_file=Path(p["log_file"]),
        screenshots_dir=Path(p["screenshots_dir"]),
    )

    return Config(
        portal=portal,
        vnr=str(raw.get("vnr", "") or ""),
        selectors=selectors,
        timing=timing,
        paths=paths,
        credentials=_load_credentials(),
    )
