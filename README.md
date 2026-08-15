# NQ Research Platform

A research platform for identifying, testing, and scoring NQ futures
trading strategies, focused on the 8:30 AM New York open. Built step by
step as a learning project — see `docs/ROADMAP.md` for the full plan and
where we currently are.

## What's in this folder

- `docs/ROADMAP.md` — the full 5-stage plan in plain English, plus notes
  on data sources and known limitations.
- `src/data_fetch.py` — pulls REAL NQ minute-bar data from Yahoo Finance.
  **This requires normal internet access and will NOT run inside the
  cloud sandbox Claude used to build this** (that sandbox blocks access to
  financial data sites). Run this on your own Mac once it's set up (see
  below).
- `src/generate_sample_data.py` — generates FAKE, clearly-labeled
  synthetic NQ data so we can build and test everything else without
  being blocked by the sandbox's network restrictions.
- `src/plot_open.py` — draws a chart of price action around the 8:30 AM
  NY open for the last several days of whatever data is in `data/`.
- `data/` — CSV files of price data (synthetic for now).
- `charts/` — chart images produced by the scripts.

## Getting set up on your own Mac (so you can pull REAL data)

You'll want this eventually so `data_fetch.py` can actually reach Yahoo
Finance. Here's exactly what to install and click:

### 1. Install Python
1. Open Safari (or any browser) and go to **python.org/downloads**.
2. Click the big yellow **"Download Python 3.x.x"** button (it auto-detects
   Mac).
3. Open the downloaded `.pkg` file from your Downloads folder.
4. Click **Continue** through the installer screens, then **Install**, and
   enter your Mac password when asked.
5. When it finishes, open the **Terminal** app (press `Cmd+Space`, type
   "Terminal", press Enter).
6. Type `python3 --version` and press Enter. You should see something like
   `Python 3.12.x`. If you see that, it worked.

### 2. Install a code editor (optional but recommended)
1. Go to **code.visualstudio.com**.
2. Click **Download for Mac**.
3. Open the downloaded file, drag the VS Code icon into your Applications
   folder.
4. Open VS Code from Applications (or Spotlight search).

### 3. Get this project folder onto your Mac
Once you download the ZIP file I send you in this conversation, unzip it
(double-click it in Finder) and note where it lands — usually your
Downloads folder. You can move the unzipped `nq_research_platform` folder
somewhere permanent, like your Documents folder.

### 4. Install the Python packages this project needs
1. Open Terminal.
2. Type `cd ` (with a trailing space), then drag the `nq_research_platform`
   folder from Finder into the Terminal window — this auto-fills the full
   path. Press Enter.
3. Type this exactly and press Enter:
   ```
   pip3 install yfinance pandas numpy matplotlib
   ```
   This downloads and installs the four toolkits this project depends on.
   It may take a minute or two.

### 5. Run it
Still in Terminal, in the project folder, type:
```
python3 src/data_fetch.py
```
This pulls the last ~59 days of real NQ 1-minute bars from Yahoo Finance
and saves them into `data/`. Then run:
```
python3 src/plot_open.py
```
This will now automatically prefer the REAL data file over the synthetic
one, and save an updated chart into `charts/`.

## Backing this project up to GitHub (do this once your Mac is set up)

GitHub is a free website that stores a permanent copy of your project's
code and its full history. This matters because this project's `git`
history currently only exists on your own Mac — if that machine's disk
ever fails, the history goes with it. GitHub gives you an off-machine
backup. It does NOT change how we write code together; it's just a safety
net underneath it.

### 1. Create a free GitHub account
1. Go to **github.com** in a browser and click **Sign up**.
2. Follow the prompts (email, password, username). Verify your email when
   it asks.

### 2. Create a new empty repository
1. Once logged in, click the **+** icon top-right, then **New repository**.
2. Name it something like `nq-research-platform`.
3. Leave it **Private** (recommended — this is your personal trading
   research, no reason to make it public) unless you want it public.
4. Do NOT check "Add a README" or any other initialize option — we already
   have those files locally and don't want conflicts.
5. Click **Create repository**. GitHub will show you a page with some
   commands — you don't need to copy those, use the steps below instead.

### 3. Create a Personal Access Token (this is like a revocable password)
1. Click your profile picture (top-right) → **Settings**.
2. Scroll down the left sidebar to **Developer settings** (at the very
   bottom).
3. Click **Personal access tokens** → **Tokens (classic)** → **Generate
   new token (classic)**.
4. Give it a name like `nq-research-platform-mac`, set an expiration (90
   days is fine — you can always make a new one later), and check the box
   next to **repo** (this grants access to push code, nothing else).
5. Click **Generate token** and COPY the code it shows you immediately —
   GitHub only shows it once. Paste it somewhere safe temporarily (like
   Notes app) — you'll use it in place of a password in the next step.

### 4. Connect and push your local project
In Terminal, inside the `nq_research_platform` folder, run these one at a
time (replace `YOUR-USERNAME` with your actual GitHub username):
```
git remote add origin https://github.com/YOUR-USERNAME/nq-research-platform.git
git branch -M main
git push -u origin main
```
When it asks for a username, type your GitHub username. When it asks for
a password, paste the Personal Access Token from step 3 (typing/pasting a
password in Terminal shows nothing on screen — that's normal, it's still
registering keystrokes).

From then on, any time we make changes, running `git add -A`, then
`git commit -m "describe what changed"`, then `git push` will update the
backup on GitHub.

## What's next

See `docs/ROADMAP.md` — next up is Stage 2: turning one specific trading
setup you have in mind into a rule the computer can detect automatically
in the data.
