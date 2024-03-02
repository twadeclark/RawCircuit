CREATE TABLE IF NOT EXISTS public.articles
(
    id integer NOT NULL DEFAULT nextval('articles_id_seq'::regclass),
    aggregator text COLLATE pg_catalog."default",
    source_id text COLLATE pg_catalog."default",
    source_name text COLLATE pg_catalog."default",
    author text COLLATE pg_catalog."default",
    title text COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    url text COLLATE pg_catalog."default",
    url_to_image text COLLATE pg_catalog."default",
    published_at timestamp without time zone,
    content text COLLATE pg_catalog."default",
    scraped_website_content text COLLATE pg_catalog."default",
    processed_timestamp timestamp with time zone,
    added_timestamp timestamp with time zone,
    scraped_timestamp timestamp with time zone,
    rec_order integer,
    CONSTRAINT articles_pkey PRIMARY KEY (id),
    CONSTRAINT articles_url_key UNIQUE (url)
)
