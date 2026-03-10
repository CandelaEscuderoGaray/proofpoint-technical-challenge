# Data Quality Report

- Total input records: 10
- Total output records: 5
- Discarded entries: 1
- Corrected entries: 5
- Duplicates detected: 4

## Discard Strategy 

Episodes are discarded when essential information is missing:

- Series Name: if missing or empty → discard.
- Episode Number, Episode Title, and Air Date: if all three are missing or invalid →discard. Values 0 and "Unknown" are considered missing.

## Corected Strategy 

Episodes are corrected to ensure consistency and completeness:

- Season Number: missing, empty, negative, or non-numeric values → set to 0.
- Episode Number: missing, empty, negative, or non-numeric values → set to 0.
- Episode Title: missing or empty → replace with "Untitled Episode"; extra whitespace and special characters are cleaned.
- Air Date: missing, empty, or invalid → replace with "Unknown"


## Deduplication Strategy

Episodes are considered duplicates based on normalized Series Name combined with Season Number, Episode Number or Episode Title when one of the numbers is missing.

When duplicates are detected, the record with the highest priority is kept using the following order:

- Valid Air Date over 'Unknown'
- Known Episode Title over 'Untitled Episode'
- Valid Season and Episode numbers
- If still tied, keep the first record encountered
