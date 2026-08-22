# Test Cases

| # | Scenario | Input | Expected | Result |
|---|----------|-------|----------|--------|
| 1 | Urgent job, no reason given | urgency=urgent, no reason | Rejected with validation message | Passed — showed validation message | |
| 2 | Urgent job, valid reason | urgency=urgent, reason="SLA breach" | Scheduled at hour 0 immediately |  Passed — scheduled at hour 0, intensity 56 ||
| 3 | Flexible job, no deadline | urgency=flexible, duration=1 | Picks single lowest-carbon hour | Passed — picked hour 1 (lowest available), intensity 61.0 | |
| 4 | Flexible job, multi-hour duration | duration=3 | Picks lowest average 3-hour window | Passed — scheduled starting hour 21, avg intensity 77.0 | |
| 5 | Flexible job with tight deadline | duration=5, deadline=8 | Picks best window that fits before deadline | Passed — scheduled starting hour 2, avg intensity 106.4 | |
| 6 | Two flexible jobs, same session | job A then job B | Job B avoids job A's booked hours | Passed — flexible jobs correctly skipped already-booked hours | |
| 7 | 4+ urgent jobs in one session | mark 4 jobs urgent | Misuse-pattern banner appears | Passed — banner appeared briefly after 4th urgent job | |
| 8 | API unreachable | disconnect Wi-Fi | Falls back to sample data, shows warning | Passed — intensity changed from ~54 (live) to 180 (sample) when offline | |
| 9 | Emissions estimate with energy input | energy_kwh=5 | Shows kg CO2 saved calculation |  Partially passed — calculates correctly, but showed negative savings when scheduled hour had higher carbon than already-booked hour 0 (edge case) ||
| 10 | Empty job name submitted | job_name="" | Shows "please enter a job name" warning |  Passed — showed "Please enter a job name first." ||