-- Assign each event to a session: a new session starts at a visitor's first event, or after a gap of
-- more than session_gap_minutes since their previous event. Bot-like visitors are excluded here.
with e as (
    select
        ev.*,
        lag(ev.event_ts) over (partition by ev.visitor_id order by ev.event_ts, ev.event_key) as prev_ts
    from {{ ref('stg_retailrocket__events') }} ev
    where ev.visitor_id not in (select visitor_id from {{ ref('int_bot_visitors') }})
),

flagged as (
    select
        *,
        case
            when prev_ts is null then 1
            when {{ dbt.datediff('prev_ts', 'event_ts', 'second') }} > {{ var('session_gap_minutes') }} * 60 then 1
            else 0
        end as is_new_session
    from e
)

select
    *,
    sum(is_new_session) over (partition by visitor_id order by event_ts, event_key rows unbounded preceding) as session_number,
    cast(visitor_id as varchar) || '-' || cast(
        sum(is_new_session) over (partition by visitor_id order by event_ts, event_key rows unbounded preceding)
        as varchar)                                                                                        as session_id
from flagged
