# Smurf

Fetches URL titles

## Configuration

| Property                             | Description                                                          |
| ------------------------------------ | -------------------------------------------------------------------- |
| **plugins.smurf.enable**             | Enable the plugin.  Network-speficic, channel-speficic.              |
| **plugins.smurf.reportErrors**       | Whether to report errors.  Network-speficic, channel-speficic.       |
| **plugins.smurf.smurfMultipleURLs**  | Whether to smurf multiple URLs.  Network-speficic, channel-speficic. |
| **plugins.smurf.ignoreUrlRegexp**    | Ignore URL regexp.  Network-speficic, channel-speficic.              |

## Usage

```
# private command
<user>    smurf https://pfoo.org/
<bot>     >> pfoo! (at pfoo.org)

# channel command
<user>    bot, smurf https://pfoo.org/
<bot>     user, >> pfoo! (at pfoo.org)

# free message in a channel (if enabled)
<user>    Hey man, check out https://pfoo.org/ and https://polizei.wtf/
<bot>     >> pfoo! (at pfoo.org)
<bot>     >> polizei.wtf (at polizei.wtf)
```
