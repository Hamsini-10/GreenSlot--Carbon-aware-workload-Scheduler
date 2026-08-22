# Test Cases

| # | Scenario | Input | Expected | Result |
|---|----------|-------|----------|--------|
| 1 | Urgent job, no reason given | urgency=urgent, no reason | Rejected with validation message | |
| 2 | Urgent job, valid reason | urgency=urgent, reason="SLA breach" | Scheduled at hour 0 immediately | |
| 3 | Flexible job, no deadline | urgency=flexible, duration=1 | Picks single lowest-carbon hour | |
| 4 | Flexible job, multi-hour duration | duration=3 | Picks lowest average 3-hour window | |
| 5 | Flexible job with tight deadline | duration=5, deadline=8 | Picks best window that fits before deadline | |
| 6 | Two flexible jobs, same session | job A then job B | Job B avoids job A's booked hours | |
| 7 | 4+ urgent jobs in one session | mark 4 jobs urgent | Misuse-pattern banner appears | |
| 8 | API unreachable | disconnect Wi-Fi | Falls back to sample data, shows warning | |
| 9 | Emissions estimate with energy input | energy_kwh=5 | Shows kg CO2 saved calculation | |
| 10 | Empty job name submitted | job_name="" | Shows "please enter a job name" warning | |