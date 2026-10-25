select 'retention' as metric, cohort_week as at
from {{ ref('rpt_retention') }}
where d1_retention not between 0 and 1 or d7_retention not between 0 and 1 or d30_retention not between 0 and 1
union all
select 'stickiness', activity_date
from {{ ref('rpt_dau_mau') }}
where stickiness not between 0 and 1 or dau > mau_28d
