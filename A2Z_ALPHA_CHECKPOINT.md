# A2Z-Scanner — Binance Alpha Continuity Checkpoint

Repo: /workspaces/A2Z-Scanner
Branch: main
Git push: OFF — never push.

## Main project rule
- Existing code inspect first.
- Do not create duplicate implementations.
- One short terminal command at a time.
- User replies "Done".
- Do not request output unless needed.
- No automatic trade execution.
- Scanner provides alerts/signals for manual verification.

## Current project state
Binance Futures data layer is expanded and compiling.
Existing binance_data.py functions include:
- get_price()
- get_24h_ticker()
- get_klines()
- get_open_interest()
- get_funding_rate()
- get_order_book()
- get_exchange_info()
- get_usdt_futures_symbols()

527 Binance USDT perpetual Futures symbols were discovered.

20 priority coins:
ETH, SOL, XRP, XMR, KSM, ETC, LINK, ENA, SUI, NEAR,
BANK, UNI, ICP, INJ, DOR, ADA, ARB, APT, HYPE, DOT.

DORUSDT was verified unavailable on Binance Futures.
Do not guess a replacement.

## Binance Alpha requirement
Binance Alpha must be a SEPARATE discovery/data layer.
Do not treat ALPHAUSDT as the Alpha universe.
Alpha tokens are dynamically discovered from Binance Alpha.

Official Binance Skills Hub was cloned temporarily at:
/tmp/binance-skills-hub

Verified official Alpha references:
- alpha.md
- alpha-streams.md

## Verified live Alpha endpoints
Base:
https://www.binance.com/bapi/defi/v1/public/

Working:
1. Alpha token list:
bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list

2. Alpha exchange info:
bapi/defi/v1/public/alpha-trade/get-exchange-info

3. Alpha ticker:
bapi/defi/v1/public/alpha-trade/ticker?symbol=ALPHA_387USDT

4. Alpha klines:
bapi/defi/v1/public/alpha-trade/klines?symbol=ALPHA_387USDT&interval=4h&limit=3

5. Alpha aggregated trades:
bapi/defi/v1/public/alpha-trade/agg-trades?symbol=ALPHA_387USDT&limit=5

Tested successfully with HTTP 200.

Alpha ticker returned fields including:
symbol, priceChange, priceChangePercent, weightedAvgPrice,
lastPrice, lastQty, openPrice, highPrice, lowPrice,
volume, quoteVolume, openTime, closeTime, firstId, lastId, count.

Alpha kline response provides timestamp, OHLC, volume and related candle fields.

Alpha token list returned fields including:
tokenId, chainId, chainName, contractAddress, name, symbol,
price, volume24h, marketCap and many additional fields.

Alpha symbol format verified:
ALPHA_<id>USDT
Example:
ALPHA_387USDT

## Depth status
Tried:
alpha-trade/depth
Result: HTTP 404

Tried:
alpha-trade/full-depth
Result: HTTP 404

Therefore DO NOT implement Alpha depth using guessed paths.
Keep depth as UNAVAILABLE until exact supported endpoint is verified.

## Config change already made
src/config.py now contains:
BINANCE_ALPHA_BASE_URL = os.getenv("BINANCE_ALPHA_BASE_URL", "https://www.binance.com")

Existing Binance Futures URL remains:
BINANCE_BASE_URL = https://fapi.binance.com

## Backup
Created:
src/binance_data.py.alpha_backup

Existing project backups must be preserved.

## Last completed step
Existing src/binance_data.py was inspected after Alpha API verification.
Next step:
Inspect the first ~45 lines of src/binance_data.py and then create a separate src/binance_alpha.py only if architecture confirms this is safe.

## IMPORTANT
Do not restart old work.
Do not delete backups.
Do not git push.
Do not automatically execute trades.
Do not guess Alpha API endpoints.
Continue from this checkpoint.
