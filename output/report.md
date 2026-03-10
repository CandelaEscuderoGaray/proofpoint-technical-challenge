# Data Quality Report

- Total input records: 10
- Total output records: 5
- Discarded entries: 1
- Corrected entries: 5
- Duplicates detected: 4

## Deduplication Strategy

Episodes are considered duplicates based on normalized Series Name combined with Season Number, Episode Number or Episode Title when one of the numbers is missing.

When duplicates are detected, the record with the highest priority is kept using the following order:

- Valid Air Date over 'Unknown'
- Known Episode Title over 'Untitled Episode'
- Valid Season and Episode numbers
- If still tied, keep the first record encountered
