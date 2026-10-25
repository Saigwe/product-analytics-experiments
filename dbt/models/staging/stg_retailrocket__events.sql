select
    row_number() over (order by timestamp, visitorid, event, itemid)   as event_key,
    make_timestamp(timestamp * 1000)                                    as event_ts,
    cast(make_timestamp(timestamp * 1000) as date)                      as event_date,
    visitorid                                                           as visitor_id,
    event                                                               as event_type,
    itemid                                                              as item_id,
    transactionid                                                       as transaction_id
from {{ source('bronze', 'events') }}
