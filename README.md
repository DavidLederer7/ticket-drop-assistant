# Ticket Drop Assistant

Local macOS helper for fast Eventbrite ticket drops. This tool is intentionally limited to manual-assist behavior: countdown, notifications, clipboard helpers, browser launch, and optional page highlighting. It does not buy the ticket for you, submit payment, or click through checkout.

## Files

- `senior_cruise_assistant.py`: Python entry point.
- `senior_cruise_config.json`: Local config, created automatically on first run.
- `dashboard/index.html`: Local dashboard with countdown, copy buttons, and checklist.
- `helper/eventbrite_helper.js`: Optional helper that highlights relevant fields on the Eventbrite page.
- `Setup Ticket Assistant.command`: Double-click to fill in event details and personal info.
- `Test Ticket Assistant.command`: Double-click to run a dry test.
- `Run Ticket Assistant.command`: Double-click to start the live assistant.

## Run

```bash
python3 senior_cruise_assistant.py --setup
python3 senior_cruise_assistant.py --dry-run
python3 senior_cruise_assistant.py --open-now
```

Recommended first run:

1. Double-click `Setup Ticket Assistant.command`
2. The ticket link and drop time are already prefilled for Monday, April 6, 2026 at 5:00 PM EDT. Enter your promo code and your UNI or school ID
3. Double-click `Test Ticket Assistant.command`
4. Double-click `Run Ticket Assistant.command` on the day of the drop

If you prefer Terminal, these commands still work:

```bash
python3 senior_cruise_assistant.py --setup
python3 senior_cruise_assistant.py --dry-run
python3 senior_cruise_assistant.py --open-now
```

Default behavior:

- starts a local server at `http://127.0.0.1:8765`
- prints the preflight checklist in the terminal
- opens the dashboard and Eventbrite page at `T-120s`
- opens a backup Eventbrite tab at `T-15s`
- sends macOS notifications at `T-5m`, `T-1m`, `T-10s`, and `T=0`
- copies the promo code to the clipboard when the primary open event fires, if one is set

## Config

On first run, the script writes `senior_cruise_config.json`. Adjust only if needed:

- `preferred_browser`: macOS app name, for example `"Google Chrome"` or `"Safari"`. Leave `null` to use the default browser.
- `notification_offsets`: notification schedule in seconds before the drop.
- `primary_open_offset_seconds`: when to open the main event page.
- `backup_open_offset_seconds`: when to open a backup tab.
- `promo_code`: optional, can also be typed directly into the dashboard
- `uni`: optional, can also be typed directly into the dashboard

The default config is generic and safe to share.

## Optional Eventbrite Helper

If you use a userscript manager or Chrome DevTools Snippets:

1. Open the Eventbrite page.
2. Load `helper/eventbrite_helper.js`.
3. The script adds a small overlay with detected state and highlights promo/access code fields, quantity controls, and likely checkout buttons.

The helper never clicks anything and does not bypass CAPTCHAs or platform restrictions.

## Sharing

Simplest options:

1. GitHub: make the repo public or share the private repo with specific people. They can clone it, run `--setup`, and use their own details.
2. ZIP file: click `Code` on GitHub, choose `Download ZIP`, and send that ZIP to people directly.

Best GitHub workflow for other users:

1. Share the repo link.
2. Tell them to download the repo or run `git clone`.
3. Tell them to double-click `Setup Ticket Assistant.command`.
4. Then they should double-click `Test Ticket Assistant.command`.
5. On the day of the drop, they should double-click `Run Ticket Assistant.command`.
