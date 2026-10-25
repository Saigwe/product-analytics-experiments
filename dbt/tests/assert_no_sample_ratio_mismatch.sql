-- Sample-ratio mismatch guard: a 50/50 split must land between 45% and 55%.
select experiment_id, variant, users, 1.0 * users / sum(users) over (partition by experiment_id) as share
from {{ ref('rpt_experiment_results') }}
qualify share < 0.45 or share > 0.55
