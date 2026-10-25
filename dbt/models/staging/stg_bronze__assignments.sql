select
    user_id,
    experiment_id,
    variant
from {{ source('bronze', 'assignments') }}
