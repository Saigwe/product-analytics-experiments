-- Classic day-N retention for each weekly cohort of new visitors: the share active exactly N days after
-- their first day (N = 1, 7, 30). A cohort only reports day N once its last member has had N days.
with users as (
    select
        visitor_id,
        min(activity_date)                                              as first_date
    from {{ ref('fct_user_day') }}
    group by 1
),

cohorted as (
    select *, cast({{ dbt.date_trunc('week', 'first_date') }} as date) as cohort_week from users
),

cohorts as (
    select cohort_week, count(*) as cohort_users, max(first_date) as last_join
    from cohorted
    group by 1
),

returns as (
    select c.cohort_week, d.visitor_id, {{ dbt.datediff('c.first_date', 'd.activity_date', 'day') }} as day_n
    from cohorted c
    join {{ ref('fct_user_day') }} d on d.visitor_id = c.visitor_id
),

last_day as (select max(activity_date) as d from {{ ref('fct_user_day') }})

select
    co.cohort_week,
    co.cohort_users,
    {% for n in [1, 7, 30] %}
    case when {{ dbt.dateadd('day', n, 'co.last_join') }} <= l.d
         then cast(count(distinct case when r.day_n = {{ n }} then r.visitor_id end) as double) / co.cohort_users
    end                                                                     as d{{ n }}_retention{{ ',' if not loop.last }}
    {% endfor %}
from cohorts co
cross join last_day l
left join returns r on r.cohort_week = co.cohort_week
group by co.cohort_week, co.cohort_users, co.last_join, l.d
