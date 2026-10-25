-- Daily active visitors, 28-day active visitors ending that day, and stickiness (DAU / MAU).
-- MAU is only reported once 28 days of history exist.
with days as (
    select distinct activity_date from {{ ref('fct_user_day') }}
),

first_day as (select min(activity_date) as d from days),

counts as (
    select
        d.activity_date,
        (select count(*) from {{ ref('fct_user_day') }} u where u.activity_date = d.activity_date) as dau,
        case when d.activity_date >= {{ dbt.dateadd('day', 27, 'f.d') }} then (
            select count(distinct u.visitor_id) from {{ ref('fct_user_day') }} u
            where u.activity_date between {{ dbt.dateadd('day', -27, 'd.activity_date') }} and d.activity_date
        ) end                                                                                   as mau_28d
    from days d
    cross join first_day f
)

select *, cast(dau as double) / nullif(mau_28d, 0) as stickiness
from counts
