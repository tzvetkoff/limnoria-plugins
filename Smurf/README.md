# Smurf

Fetches URL titles.

## Configuration

| Property                             | Description                                                               |
| ------------------------------------ | ------------------------------------------------------------------------- |
| **plugins.smurf.enable**             | Enable the plugin.  Network-specific, channel-specific.                   |
| **plugins.smurf.timeout**            | Fetch timeout in seconds.  Network-specific, channel-specific.            |
| **plugins.smurf.reportErrors**       | Whether to report errors.  Network-specific, channel-specific.            |
| **plugins.smurf.showRecirectChain**  | Whether to show full redirect chain.  Network-specific, channel-specific. |
| **plugins.smurf.smurfMultipleURLs**  | Whether to smurf multiple URLs.  Network-specific, channel-specific.      |
| **plugins.smurf.ignoreUrlRegexp**    | Ignore URL regexp.  Network-specific, channel-specific.                   |

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
