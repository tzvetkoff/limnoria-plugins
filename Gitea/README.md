# Gitea

Gitea webhooks integration.

## Webhooks

Currently known webhooks:

- [`create`](./doc/webhook.create.md)
- [`delete`](./doc/webhook.delete.md)
- [`fork`](./doc/webhook.fork.md)
- [`issue_comment`](./doc/webhook.issue_comment.md)
- [`issues`](./doc/webhook.issues.md)
- [`pull_request_approved`](./doc/webhook.pull_request_approved.md)
- [`pull_request_rejected`](./doc/webhook.pull_request_rejected.md)
- [`pull_request`](./doc/webhook.pull_request.md)
- [`push`](./doc/webhook.push.md)
- [`release`](./doc/webhook.release.md)

See the [doc](doc) directory for payload samples, or enable `gitea.debug` and collect samples for yourself.

Note that the payload is flattened so this is what you get when the message is constructed.


## Message formats.

Each webhook event has its own configurable message format: `gitea.format.<event>`.

By default these are empty so you'll have to configure these yourself.

When evaluating the template, [`str.format_map()`](https://docs.python.org/3/library/stdtypes.html#str.format_map) is used.


## Future improvements

Current "template" evaluation is not powerful enough and requires payload flattening.

In the future, I intend to replace it with either a custom minimalistic template engine or a full-blown template engine like [Mako](https://www.makotemplates.org/).
