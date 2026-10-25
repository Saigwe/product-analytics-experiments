-- Weekly signup cohorts: share of each cohort active N weeks after signup.
with activity as (
    select distinct
        u.user_id,
        cast({{ dbt.date_trunc('week', 'u.signup_date') }} as date)                 as cohort_week,
        {{ dbt.datediff('u.signup_date', 'cast(e.event_ts as date)', 'day') }} // 7  as week_number
    from {{ ref('stg_bronze__users') }} u
    join {{ ref('stg_bronze__events') }} e on e.user_id = u.user_id
),

cohort_size as (
    select cast({{ dbt.date_trunc('week', 'signup_date') }} as date) as cohort_week, count(*) as users
    from {{ ref('stg_bronze__users') }}
    group by 1
)

select
    a.cohort_week,
    a.week_number,
    count(distinct a.user_id)                       as active_users,
    max(c.users)                                    as cohort_users,
    100.0 * count(distinct a.user_id) / max(c.users) as retention_pct
from activity a
join cohort_size c on c.cohort_week = a.cohort_week
group by 1, 2
