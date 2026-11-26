# Studio Round Ledger

- **Maximum Rounds Allowed**: `5`
- **Rule**: Inspect real output, score all bars in `BARS.md`, and modify **only the single weakest item** per round. Never lower quality settings silently.

| Round | Artifact Inspected | Bar Scores Summary | Weakest Bar Targeted | Single Fix Applied | Verdict |
|---:|---|---|---|---|---|
| 1 | `round_01_preview_check` | `BAR-01:4, BAR-02:3, BAR-03:4, BAR-04:4, BAR-05:4` | `BAR-02` (3/5) | Applied object scale transforms and added 1.5 mm 3-segment bevels to hero hard edges. | CONTINUE |
| 2 | `round_02_verification` | `BAR-01:4, BAR-02:4, BAR-03:4, BAR-04:4, BAR-05:4` | `NONE` (All >= 4/5) | Verified bevel specular catchlights in REVIEW crop; locked output for delivery. | PASS |
