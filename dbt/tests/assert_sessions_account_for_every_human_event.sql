-- Every non-bot event lands in exactly one session: session event counts add up to the source.
with src as (
    select count(*) as n
    from {{ ref('stg_retailrocket__events') }}
    where visitor_id not in (select visitor_id from {{ ref('int_bot_visitors') }})
)

select src.n, s.n
from src, (select sum(events) as n from {{ ref('fct_sessions') }}) s
where src.n <> s.n
