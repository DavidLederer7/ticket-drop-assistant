# Ticket Drop Assistant

Static ticket-drop helper for fast Eventbrite releases. It is designed to work on GitHub Pages with no backend and no database. Each user enters their email, promo code, and UNI or school ID in the browser, and those values are saved only in that browser on that device. Refreshing the page on the same device/browser keeps them there.

## Files

- `index.html`: GitHub Pages app with countdown, links, and local browser storage.
- `dashboard/index.html`: older local dashboard version.
- `helper/eventbrite_helper.js`: Optional helper that highlights relevant fields on the Eventbrite page.
- `Test Ticket Assistant.command`: Double-click to run a dry test and open the dashboard in Google Chrome.
- `Run Ticket Assistant.command`: Double-click to start the live assistant.

## GitHub Pages

1. Push this repo to GitHub.
2. Open your repo on GitHub.
3. Go to `Settings` > `Pages`.
4. Under `Build and deployment`, choose `Deploy from a branch`.
5. Choose branch `main` and folder `/ (root)`.
6. Save.
7. GitHub will publish the site at a URL like `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`.

## How It Works

- A user opens the GitHub Pages site.
- They enter their email, promo code, and UNI or school ID.
- After an email is entered, the page auto-saves those values in browser local storage under that email.
- Returning on the same browser and device reloads their saved values automatically.
- There is no shared database and no server-side account system.

## Local Mac Flow

If you still want the Mac launcher version:

```bash
python3 senior_cruise_assistant.py --dry-run
python3 senior_cruise_assistant.py --open-now
```

## Optional Eventbrite Helper

If you use a userscript manager or Chrome DevTools Snippets:

1. Open the Eventbrite page.
2. Load `helper/eventbrite_helper.js`.
3. The script adds a small overlay with detected state and highlights promo/access code fields, quantity controls, and likely checkout buttons.

The helper never clicks anything and does not bypass CAPTCHAs or platform restrictions.

## Sharing

Simplest options:

1. GitHub Pages: share the published site URL and users can use it immediately in the browser.
2. ZIP file: click `Code` on GitHub, choose `Download ZIP`, and send that ZIP to people directly.

Best GitHub Pages workflow for other users:

1. Share the published site URL.
2. Tell users to enter their email, promo code, and UNI or school ID.
3. Tell them the page auto-saves on the same browser and device.
4. On the same device and browser, their values will still be there next time.
