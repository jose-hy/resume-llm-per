CREATE TABLE applied_to (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id text,
    job_title text,
    url text,
    location text,
    remote boolean,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP,
    applied_to_count smallint DEFAULT 0,
    UNIQUE (job_id, job_title)
);