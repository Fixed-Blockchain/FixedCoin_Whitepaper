# FixedCoin Whitepaper

[Read online](https://fixed-blockchain.github.io/FixedCoin_Whitepaper/),
[download the PDF](FixedCoin_Whitepaper.pdf), or review the
[Markdown source](FixedCoin_Whitepaper.md).

The v30 edition explains the historical mainnet rules, the activated transition
at block **52,560**, and the difficulty and issuance schedule now in effect. Its
code references are pinned to the published FixedCoin Core v30.0.0 source.

## Build

With Python 3 installed:

```sh
python -m pip install -r requirements.txt
python build_whitepaper.py
python build_site.py
```

The PDF renderer uses the fonts bundled with ReportLab. The website is generated
from the same Markdown source under `docs/`, keeping both editions aligned.

GitHub Pages publishes the website from the `docs/` directory on the `main`
branch.

Official code and downloads: [Fixed-Blockchain/fixedcoin](https://github.com/Fixed-Blockchain/fixedcoin).
Contact: **help@fixedcoin.org**.
