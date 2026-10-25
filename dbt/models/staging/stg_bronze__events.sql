select
    event_id,
    user_id,
    event_ts,
    event_name
from {{ source('bronze', 'events') }}
