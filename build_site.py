"""Build the GitHub Pages edition from the canonical Markdown whitepaper."""
from pathlib import Path
import re
import shutil

import markdown


ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SOURCE = ROOT / "FixedCoin_Whitepaper.md"
PDF = ROOT / "FixedCoin_Whitepaper.pdf"


def article_html() -> str:
    source = SOURCE.read_text(encoding="utf-8")
    source = re.sub(
        r"\A# FixedCoin\s+Technical Whitepaper \| Core v30\.0\.0\s+"
        r"7 November 2026 \| Mainnet edition\s+",
        "",
        source,
        count=1,
    )
    rendered = markdown.markdown(
        source,
        extensions=["fenced_code", "sane_lists", "tables", "toc"],
        output_format="html5",
    )
    return re.sub(
        r"(<table>.*?</table>)",
        r'<div class="table-scroll" tabindex="0" role="region" '
        r'aria-label="Scrollable data table">\1</div>',
        rendered,
        flags=re.DOTALL,
    )


def page(article: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#081723">
  <meta name="description" content="FixedCoin Core v30 technical whitepaper: activated consensus, ASERT V2 and the 21,000 FIX emission schedule.">
  <meta property="og:title" content="FixedCoin Technical Whitepaper - Core v30.0.0">
  <meta property="og:description" content="The active FixedCoin mainnet rules, monetary schedule and ASERT V2 transition at block 52,560.">
  <meta property="og:type" content="article">
  <meta property="og:image" content="assets/fixedcoin256.png">
  <title>FixedCoin Technical Whitepaper - Core v30.0.0</title>
  <link rel="icon" href="assets/fixedcoin256.png">
  <link rel="stylesheet" href="styles.css">
  <script>document.documentElement.classList.add('js')</script>
  <script defer src="app.js"></script>
</head>
<body>
  <a class="skip-link" href="#whitepaper">Skip to the whitepaper</a>
  <header class="site-header">
    <div class="topbar">
      <a class="brand" href="#top" aria-label="FixedCoin whitepaper home">
        <img src="assets/fixedcoin256.png" alt="" width="44" height="44">
        <span><strong>FixedCoin</strong><small>Technical Whitepaper</small></span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="page-nav">Contents</button>
      <nav class="header-links" aria-label="Primary">
        <a href="FixedCoin_Whitepaper.pdf">Download PDF</a>
        <a href="https://github.com/Fixed-Blockchain/fixedcoin/releases/tag/v30.0.0">Core v30</a>
      </nav>
    </div>
  </header>

  <main id="top">
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-copy">
        <p class="eyebrow"><span class="status-dot"></span>Mainnet rules active</p>
        <h1 id="hero-title">FixedCoin<br><span>Core v30.0.0</span></h1>
        <p class="hero-lead">A precise account of FixedCoin's historical rules, the activated transition at block 52,560, ASERT V2 and the long-term emission schedule.</p>
        <div class="hero-actions">
          <a class="button primary" href="FixedCoin_Whitepaper.pdf">Read the PDF</a>
          <a class="button secondary" href="#whitepaper">Read online</a>
        </div>
      </div>
      <div class="coin-stage" aria-hidden="true">
        <div class="orbit orbit-one"></div>
        <div class="orbit orbit-two"></div>
        <img src="assets/fixedcoin256.png" alt="" width="256" height="256">
      </div>
    </section>

    <section class="facts" aria-label="Key consensus facts">
      <div><span>Activation</span><strong>52,560</strong></div>
      <div><span>Activated</span><strong>16 Oct 2026</strong></div>
      <div><span>Supply cap</span><strong>21,000 FIX</strong></div>
      <div><span>Target spacing</span><strong>600 seconds</strong></div>
    </section>

    <div class="reading-layout">
      <aside id="page-nav" class="contents" aria-label="Whitepaper contents">
        <p>Contents</p>
        <a href="#one-network-a-defined-activation-point">Overview</a>
        <a href="#1-network-parameters-and-activation">1. Network and activation</a>
        <a href="#2-historical-monetary-rules">2. Historical monetary rules</a>
        <a href="#3-the-v30-emission-schedule">3. Emission schedule</a>
        <a href="#4-difficulty-adjustment">4. Difficulty adjustment</a>
        <a href="#5-validation-frozen-output-and-wallets">5. Validation and wallets</a>
        <a href="#6-current-operator-guidance-and-references">6. Operator guidance</a>
        <a href="#appendix-a-exact-consensus-mathematics">Appendix A. Exact mathematics</a>
        <div class="contents-meta">
          <span>Edition</span>
          <strong>7 November 2026</strong>
          <span>Reference release</span>
          <strong>v30.0.0</strong>
        </div>
      </aside>

      <article id="whitepaper" class="whitepaper">
        {article}
      </article>
    </div>
  </main>

  <footer>
    <div>
      <strong>FixedCoin</strong>
      <span>Peer-to-peer SHA-256 currency</span>
    </div>
    <div class="footer-links">
      <a href="https://fixedcoin.org/">fixedcoin.org</a>
      <a href="https://github.com/Fixed-Blockchain/fixedcoin">Source code</a>
      <a href="mailto:help@fixedcoin.org">help@fixedcoin.org</a>
    </div>
  </footer>
</body>
</html>
"""


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    if not PDF.exists():
        raise FileNotFoundError("Build FixedCoin_Whitepaper.pdf before the web edition")
    (DOCS / "index.html").write_text(page(article_html()), encoding="utf-8")
    shutil.copy2(PDF, DOCS / PDF.name)
    print(DOCS / "index.html")


if __name__ == "__main__":
    main()
