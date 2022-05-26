# RateSX

Fetches crypto currency prices from https://rate.sx/.

## Configuration

| Property                  | Description
| -                         | -
| **plugins.ratesx.enable** | Enable the plugin.  Network-speficic, channel-speficic.

## Usage

```
rate BTC
=> 1 BTC = 31337.000000 USD

rate 2 BTC
=> 2 BTC = 62674.000000 USD

rate 3 BTC in EUR
=> 3 BTC = 84846.000000 EUR
```
