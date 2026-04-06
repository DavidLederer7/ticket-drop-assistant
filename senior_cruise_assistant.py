#!/usr/bin/env python3
"""
Manual checkout assistant for fast ticket drops.

This tool intentionally does not click purchase controls, solve CAPTCHAs, or
submit payment. It provides timing, reminders, a local dashboard, and quick
access to the event page and user-supplied ticket metadata.
"""

from __future__ import annotations

import argparse
import datetime as dt
import http.server
import json
import os
import pathlib
import socketserver
import subprocess
import sys
import threading
import time
import tempfile
import urllib.parse
import webbrowser
from dataclasses import dataclass
from zoneinfo import ZoneInfo


ROOT = pathlib.Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "senior_cruise_config.json"
DEFAULT_PORT = 8765


@dataclass
class Config:
    event_url: str
    organizer_url: str
    event_title: str
    drop_iso: str
    timezone: str
    promo_code: str
    uni: str
    preferred_browser: str | None
    notification_offsets: list[int]
    primary_open_offset_seconds: int
    backup_open_offset_seconds: int
    refresh_warning_offset_seconds: int

    @property
    def drop_dt(self) -> dt.datetime:
        parsed = dt.datetime.fromisoformat(self.drop_iso)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=ZoneInfo(self.timezone))
        return parsed.astimezone(ZoneInfo(self.timezone))


DEFAULT_CONFIG = {
    "event_title": "Eventbrite Ticket Drop",
    "event_url": "https://www.eventbrite.com/",
    "organizer_url": "https://www.eventbrite.com/",
    "drop_iso": "2026-04-06T17:00:00-04:00",
    "timezone": "America/New_York",
    "promo_code": "",
    "uni": "",
    "preferred_browser": None,
    "notification_offsets": [300, 60, 10, 0],
    "primary_open_offset_seconds": 120,
    "backup_open_offset_seconds": 15,
    "refresh_warning_offset_seconds": 10,
}


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def ensure_config() -> None:
    if CONFIG_PATH.exists():
        return
    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8")


def load_config() -> Config:
    ensure_config()
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return Config(**payload)


def notify(title: str, body: str) -> None:
    payload = json.dumps({"title": title, "body": body})
    script = (
        "set payload to "
        + payload
        + '\n'
        + 'display notification (body of payload) with title (title of payload)'
    )
    subprocess.run(["osascript", "-e", script], check=False)


def copy_to_clipboard(value: str) -> None:
    subprocess.run(["pbcopy"], input=value.encode("utf-8"), check=False)


def open_url(url: str, browser_name: str | None = None) -> None:
    if browser_name:
        subprocess.run(["open", "-a", browser_name, url], check=False)
        return
    webbrowser.open(url, new=2)


def focus_browser(browser_name: str | None) -> None:
    if not browser_name:
        return
    script = f'tell application "{browser_name}" to activate'
    subprocess.run(["osascript", "-e", script], check=False)


def build_dashboard_html(config: Config, port: int) -> str:
    query = urllib.parse.urlencode(
        {
            "title": config.event_title,
            "event_url": config.event_url,
            "organizer_url": config.organizer_url,
            "drop_iso": config.drop_dt.isoformat(),
            "timezone": config.timezone,
            "promo_code": config.promo_code,
            "uni": config.uni,
            "primary_open_offset_seconds": str(config.primary_open_offset_seconds),
            "backup_open_offset_seconds": str(config.backup_open_offset_seconds),
            "refresh_warning_offset_seconds": str(config.refresh_warning_offset_seconds),
        }
    )
    return f"http://127.0.0.1:{port}/dashboard/index.html?{query}"


def build_dashboard_file(config: Config) -> str:
    template = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    bootstrap = {
        "title": config.event_title,
        "eventUrl": config.event_url,
        "organizerUrl": config.organizer_url,
        "dropIso": config.drop_dt.isoformat(),
        "timezone": config.timezone,
        "promoCode": config.promo_code,
        "uni": config.uni,
    }
    injected = template.replace(
        'const params = new URLSearchParams(window.location.search);\n      const state = {\n        title: params.get("title") || "Senior Cruise",\n        eventUrl: params.get("event_url") || "#",\n        organizerUrl: params.get("organizer_url") || "#",\n        dropIso: params.get("drop_iso"),\n        timezone: params.get("timezone") || "America/New_York",\n        promoCode: params.get("promo_code") || "",\n        uni: params.get("uni") || "",\n      };',
        f"const state = {json.dumps(bootstrap)};",
    )
    temp_path = pathlib.Path(tempfile.gettempdir()) / "senior_cruise_dashboard.html"
    temp_path.write_text(injected, encoding="utf-8")
    return temp_path.as_uri()


def make_handler() -> type[http.server.SimpleHTTPRequestHandler]:
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)

        def log_message(self, fmt: str, *args) -> None:
            return

    return Handler


def start_server(port: int) -> ReusableTCPServer:
    server = ReusableTCPServer(("127.0.0.1", port), make_handler())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def seconds_until(target: dt.datetime) -> int:
    return max(0, int((target - dt.datetime.now(target.tzinfo)).total_seconds()))


def format_delta(seconds: int) -> str:
    minutes, secs = divmod(max(0, seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    return f"{minutes:02d}m {secs:02d}s"


def print_preflight(config: Config, dashboard_url: str) -> None:
    drop_text = config.drop_dt.strftime("%A, %B %d, %Y at %I:%M:%S %p %Z")
    promo_text = config.promo_code if config.promo_code else "<enter your promo code>"
    uni_text = config.uni if config.uni else "<enter your UNI or school ID>"
    lines = [
        "",
        f"Event: {config.event_title}",
        f"Drop:  {drop_text}",
        f"URL:   {config.event_url}",
        "",
        "Preflight checklist",
        "[ ] Signed into Eventbrite in the target browser",
        "[ ] Card and billing autofill already saved",
        f"[ ] Promo code ready: {promo_text}",
        f"[ ] UNI ready: {uni_text}",
        "[ ] System clock synced",
        "",
        "Manual sequence at drop",
        "1. Refresh the event page",
        "2. Apply the promo code if required",
        "3. Select one ticket",
        "4. Enter your UNI or school ID if prompted",
        "5. Proceed through checkout and confirm manually",
        "",
        f"Dashboard: {dashboard_url}",
        f"Optional helper script: {ROOT / 'helper' / 'eventbrite_helper.js'}",
        "",
    ]
    print("\n".join(lines))


def run_schedule(config: Config, dashboard_url: str, dry_run: bool) -> int:
    notify_offsets = sorted(set(config.notification_offsets), reverse=True)
    opened_primary = False
    opened_backup = False
    sent_offsets: set[int] = set()
    drop_dt = config.drop_dt

    if dry_run:
        print("Dry run mode: no waiting loop will be started.")
        return 0

    while True:
        now = dt.datetime.now(ZoneInfo(config.timezone))
        remaining = int((drop_dt - now).total_seconds())

        if not opened_primary and remaining <= config.primary_open_offset_seconds:
            notify("Ticket Drop Assistant", "Opening Eventbrite and dashboard.")
            open_url(dashboard_url, config.preferred_browser)
            open_url(config.event_url, config.preferred_browser)
            focus_browser(config.preferred_browser)
            if config.promo_code:
                copy_to_clipboard(config.promo_code)
            opened_primary = True

        if not opened_backup and remaining <= config.backup_open_offset_seconds:
            notify("Ticket Drop Assistant", "Opening backup event tab.")
            open_url(config.event_url, config.preferred_browser)
            opened_backup = True

        for offset in notify_offsets:
            if remaining <= offset and offset not in sent_offsets:
                if offset == 0:
                    message = "Tickets should be live now. Refresh and proceed manually."
                elif offset == config.refresh_warning_offset_seconds:
                    message = "Refresh warning. Get your cursor ready on the event page."
                else:
                    message = f"T-{format_delta(offset)} until ticket drop."
                notify("Ticket Drop Assistant", message)
                sent_offsets.add(offset)

        status = f"\rTime to drop: {format_delta(remaining)}"
        sys.stdout.write(status)
        sys.stdout.flush()

        if remaining <= -5:
            print("\nDrop window reached. Leaving dashboard server running until interrupted.")
            return 0

        time.sleep(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manual checkout assistant for the Eventbrite drop.")
    parser.add_argument("--dry-run", action="store_true", help="Print the checklist and exit.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Local dashboard port.")
    parser.add_argument("--setup", action="store_true", help="Fill in event and user details interactively.")
    parser.add_argument(
        "--open-now",
        action="store_true",
        help="Open the dashboard and event page immediately after startup.",
    )
    return parser.parse_args()


def prompt(current: str | None, label: str, placeholder: str) -> str:
    suffix = f" [{current}]" if current else ""
    response = input(f"{label}{suffix}: ").strip()
    if response:
        return response
    if current:
        return current
    return placeholder


def interactive_setup() -> Config:
    ensure_config()
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    print("Enter the values you want to use. Press Enter to keep the current value.")
    data["event_title"] = prompt(data.get("event_title"), "Event title", DEFAULT_CONFIG["event_title"])
    data["event_url"] = prompt(data.get("event_url"), "Event URL", DEFAULT_CONFIG["event_url"])
    data["organizer_url"] = prompt(data.get("organizer_url"), "Organizer URL", data["event_url"])
    data["drop_iso"] = prompt(data.get("drop_iso"), "Drop time ISO", DEFAULT_CONFIG["drop_iso"])
    data["timezone"] = prompt(data.get("timezone"), "Timezone", DEFAULT_CONFIG["timezone"])
    data["promo_code"] = prompt(data.get("promo_code"), "Promo code", "")
    data["uni"] = prompt(data.get("uni"), "UNI or school ID", "")
    browser_placeholder = data.get("preferred_browser") or ""
    data["preferred_browser"] = prompt(browser_placeholder, "Preferred browser app name", "")
    if not data["preferred_browser"]:
        data["preferred_browser"] = None
    CONFIG_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Saved config to {CONFIG_PATH}")
    return Config(**data)


def main() -> int:
    args = parse_args()
    config = interactive_setup() if args.setup else load_config()
    server = None

    try:
        server = start_server(args.port)
        dashboard_url = build_dashboard_html(config, args.port)
    except OSError:
        dashboard_url = build_dashboard_file(config)

    print_preflight(config, dashboard_url)

    if args.open_now:
        open_url(dashboard_url, config.preferred_browser)
        open_url(config.event_url, config.preferred_browser)

    try:
        return run_schedule(config, dashboard_url, dry_run=args.dry_run)
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
