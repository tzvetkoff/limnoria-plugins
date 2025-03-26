# NIGGG

Fetches and announces earthquakes from https://ndc.niggg.bas.bg/.

## Configuration

| Property                        | Description                                                          |
| ------------------------------- | -------------------------------------------------------------------- |
| **plugins.niggg.enable**        | Enable the plugin.  Network-specific, channel-specific.              |
| **plugins.niggg.messageFormat** | Earthquake alert message format. Network-specific, channel-specific. |
| **plugins.niggg.schedule**      | Cron schedule when to poll for new data.  Global.                    |
| **plugins.niggg.timeout**       | Fetch timeout in seconds.  Global.                                   |
