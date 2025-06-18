# EMSC

Sends near-realtime notifications about earthquakes in a configured area.

Data coming from [EMSC](https://seismicportal.eu/realtime.html).

## Configuration

| Property                        | Description                                                                                                             |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **plugins.emsc.enable**        | Enable the plugin.  Network-specific, channel-specific.                                                                  |
| **plugins.emsc.areaType**      | Area type. One of "all", "none", "circle", "rectangle".  Network-specific, channel-specific.                             |
| **plugins.emsc.areaCircle**    | GPS coordinates of a circular area (needed if `areaType` is set to `circle`).  Network-specific, channel-specific.       |
| **plugins.emsc.areaRectangle** | GPS coordinates of a rectangular area (needed if `areaType` is set to `rectangle`).  Network-specific, channel-specific. |
| **plugins.emsc.minMag**        | Minimal earthquake magnitude.  Network-specific, channel-specific.                                                       |
| **plugins.emsc.messageFormat** | Earthquake alert message format. Network-specific, channel-specific.                                                     |
