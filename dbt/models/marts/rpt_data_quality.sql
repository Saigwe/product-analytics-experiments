-- What was excluded and why, so metric consumers can see it: bot-like visitors and their share of views.
with ev as (
    select
        count(*) filter (where event_type = 'view')                     as all_views,
        count(distinct visitor_id)                                      as all_visitors
    from {{ ref('stg_retailrocket__events') }}
)

select
    (select count(*) from {{ ref('int_bot_visitors') }})                as bot_visitors,
    ev.all_visitors,
    (select sum(total_views) from {{ ref('int_bot_visitors') }})       as bot_views,
    ev.all_views,
    cast((select sum(total_views) from {{ ref('int_bot_visitors') }}) as double) / ev.all_views as bot_view_share
from ev
