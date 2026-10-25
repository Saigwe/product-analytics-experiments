-- Visitors whose behaviour looks automated: more than bot_max_views_per_day item views on any one day.
-- Excluded from product metrics (a crawler isn't a customer), but kept and counted so the share is visible.
select
    visitor_id,
    max(views)  as max_views_in_a_day,
    sum(views)  as total_views
from (
    select visitor_id, event_date, count(*) as views
    from {{ ref('stg_retailrocket__events') }}
    where event_type = 'view'
    group by 1, 2
)
group by 1
having max(views) > {{ var('bot_max_views_per_day') }}
