# Sedster

Replaces messages with sed-style regular expressions.

Basically a trimmed down version of Limnoria's own `SedRegex` plugin.

## Configuration

| Property                                | Description                                                    |
| --------------------------------------- | -------------------------------------------------------------- |
| **plugins.sedster.enable**              | Enable the plugin.                                             |
| **plugins.sedster.ignoreRegex**         | Whether to ignore messages that look like regular expressions. |
| **plugins.sedster.boldReplacementText** | Whether the replacement text should be bold.                   |
| **plugins.sedster.displayErrors**       | Whether to display errors in IRC.                              |
| **plugins.sedster.processTimeout**      | Regular expression processing timeout.                         |
