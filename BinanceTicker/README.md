# BinanceTicker

Fetches crypto currency prices using Binance's ticker API.

## Configuration

| Property                          | Description                                                    |
| --------------------------------- | -------------------------------------------------------------- |
| **plugins.binanceticker.timeout** | Fetch timeout in seconds.  Network-specific, channel-specific. |

## Usage

```
rate BTC
=> 1 BTC = 31337.000000 USD

rate 2 BTC
=> 2 BTC = 62674.000000 USD

rate 3 BTC in EUR
=> 3 BTC = 84846.000000 EUR
```
