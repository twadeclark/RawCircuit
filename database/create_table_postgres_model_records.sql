CREATE TABLE IF NOT EXISTS public.model_records
(
    id integer NOT NULL DEFAULT nextval('model_records_id_seq'::regclass),
    model_name text COLLATE pg_catalog."default" NOT NULL,
    attempt_time timestamp with time zone,
    success bit(1),
    disposition text COLLATE pg_catalog."default",
    template text COLLATE pg_catalog."default",
    CONSTRAINT model_records_pkey PRIMARY KEY (id),
    CONSTRAINT model_records_model_name_key UNIQUE (model_name)
)
