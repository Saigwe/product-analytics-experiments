-- One row per visitor per active day: the grain for DAU/MAU, retention and experiment metrics.
select
    visitor_id,
    session_date                                as activity_date,
    count(*)                                    as sessions,
    sum(views)                                  as views,
    sum(add_to_carts)                           as add_to_carts,
    sum(transactions)                           as transactions,
    min(min(session_date)) over (partition by visitor_id) as first_active_date
from {{ ref('fct_sessions') }}
group by 1, 2
