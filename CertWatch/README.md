# CertWatch

Sends notifications about expiring certificates.

## Configuration

| Property                                        | Description                                                                                                   |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **plugins.certwatch.hosts**                     | List of hosts (or host:port) to scan TLS certificates from.  Network-specific, channel-specific.              |
| **plugins.certwatch.messageFormatExpiringMany** | Notification message format for certificates expiring in more than 1 day. Network-specific, channel-specific. |
| **plugins.certwatch.messageFormatExpiringOne**  | Notification message format for certificates expiring in 1 day. Network-specific, channel-specific.           |
| **plugins.certwatch.messageFormatExpiringZero** | Notification message format for certificates expiring today. Network-specific, channel-specific.              |
| **plugins.certwatch.messageFormatExpired**      | Notification message format for expired certificates. Network-specific, channel-specific.                     |
| **plugins.certwatch.schedule**                  | Time (H:M) schedule when to poll for new data.  Global.                                                       |
| **plugins.certwatch.timeout**                   | Fetch timeout in seconds.  Global.                                                                            |
