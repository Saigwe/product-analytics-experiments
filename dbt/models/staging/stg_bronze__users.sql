select
    user_id,
    cast(signup_date as date)           as signup_date,
    platform
from {{ source('bronze', 'users') }}
