# Test Cases

| # | Scenario | Input | Expected | Result |
|---|----------|-------|----------|--------|
| 1 | Urgent job, no reason given | urgency=urgent, no reason | Rejected with validation message | Passed — showed "Please provide a reason" warning, message now persists (no longer flashes away) |
| 2 | Urgent job, valid reason | urgency=urgent, reason="SLA breach" | Scheduled at hour 0 immediately | Passed — scheduled at hour 0, recommendation message stayed visible |
| 3 | Flexible job, no deadline | urgency=flexible, duration=1 | Picks single lowest-carbon hour | Passed — picked lowest available hour |
| 4 | Flexible job, multi-hour duration | duration=3 | Picks lowest average 3-hour window | Passed — picked lowest average window |
| 5 | Flexible job with deadline | duration=5, deadline=8 | Picks best window that fits before deadline | Passed — scheduled within deadline window |
| 6 | Two flexible jobs, same session | job A then job B | Job B avoids job A's booked hours | Passed — second job skipped already-booked hour |
| 7 | 4+ urgent jobs in one session | mark 4 jobs urgent | Misuse-pattern banner appears | Passed — banner appeared and now stays visible instead of flashing |
| 8 | API unreachable | disconnect Wi-Fi | Falls back to sample data, shows warning | Passed — carbon intensity switched to sample values (e.g. 180) |
| 9 | Combined cost+carbon optimization | check "Optimize for cost AND carbon" | Slider appears, recommendation shows price | Passed — slider appeared, price shown in result message |
| 10 | Department tagging | enter a department name | Appears in "Savings by department" | Passed — department showed correctly in breakdown |
| 11 | CSV export | click download button | File downloads with job data | Passed — CSV downloaded with correct job data |
| 12 | Forecast anomaly | (occurs naturally with live data) | Warning banner shows if forecast/actual differ significantly | Passed — anomaly warning appeared when forecast/actual gap exceeded threshold |