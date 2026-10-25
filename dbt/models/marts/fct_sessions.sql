-- One row per session: when, how long, what happened, and how far down the funnel it got.
select
    session_id,
    visitor_id,
    session_number,
    min(event_ts)                                               as session_start,
    cast(min(event_ts) as date)                                 as session_date,
    {{ dbt.datediff('min(event_ts)', 'max(event_ts)', 'second') }} as duration_s,
    count(*)                                                    as events,
    count(*) filter (where event_type = 'view')                 as views,
    count(*) filter (where event_type = 'addtocart')            as add_to_carts,
    count(distinct transaction_id)                              as transactions,
    bool_or(event_type = 'view')                                as has_view,
    bool_or(event_type = 'addtocart')                           as has_add_to_cart,
    bool_or(event_type = 'transaction')                         as has_purchase
from {{ ref('int_events_sessionised') }}
group by 1, 2, 3
