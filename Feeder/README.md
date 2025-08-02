# Feeder

RSS/Atom feed scanner.

## Configuration

| Property                      | Description                                                                          |
| ----------------------------- | ------------------------------------------------------------------------------------ |
| **plugins.feeder.feeds**      | JSON-serialized configuration of feeds, custom titles, formats, etc.  Global.        |
| **plugins.feeder.schedule**   | Cron schedule when to poll feeds.  Global.                                           |
| **plugins.feeder.timeout**    | Fetch timeout in seconds.  Global.                                                   |
| **plugins.feeder.format**     | Default announcement format.  Network-specific.                                      |
| **plugins.feeder.lastN**      | Maximum number of messages to announce.  Network-specific.                           |
| **plugins.feeder.announces**  | JSON-serialized configuration of channels feeds are announced to.  Network-specific. |
