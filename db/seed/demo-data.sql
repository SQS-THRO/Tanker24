--
-- PostgreSQL database dump
--

\restrict zWajtr9aKU9Pjz7Sm8mIimybqv0K5gZF3kfo23K9IREBPHWmTxVT0bOfRdoXUbh

-- Dumped from database version 18.3 (Debian 18.3-1.pgdg13+1)
-- Dumped by pg_dump version 18.3 (Debian 18.3-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_invitation_key_id_fkey;
ALTER TABLE IF EXISTS ONLY public.stations DROP CONSTRAINT IF EXISTS stations_owner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.history_records DROP CONSTRAINT IF EXISTS history_records_fuel_type_id_fkey;
ALTER TABLE IF EXISTS ONLY public.history_records DROP CONSTRAINT IF EXISTS history_records_car_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cars DROP CONSTRAINT IF EXISTS cars_owner_id_fkey;
DROP INDEX IF EXISTS public.ix_users_email;
DROP INDEX IF EXISTS public.ix_tankerkoenig_stations_tankerkoenig_id;
DROP INDEX IF EXISTS public.ix_invitation_keys_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.tankerkoenig_stations DROP CONSTRAINT IF EXISTS uix_tankerkoenig_id;
ALTER TABLE IF EXISTS ONLY public.tankerkoenig_stations DROP CONSTRAINT IF EXISTS tankerkoenig_stations_pkey;
ALTER TABLE IF EXISTS ONLY public.stations DROP CONSTRAINT IF EXISTS stations_pkey;
ALTER TABLE IF EXISTS ONLY public.invitation_keys DROP CONSTRAINT IF EXISTS invitation_keys_pkey;
ALTER TABLE IF EXISTS ONLY public.history_records DROP CONSTRAINT IF EXISTS history_records_pkey;
ALTER TABLE IF EXISTS ONLY public.fuel_types DROP CONSTRAINT IF EXISTS fuel_types_pkey;
ALTER TABLE IF EXISTS ONLY public.fuel_types DROP CONSTRAINT IF EXISTS fuel_types_name_key;
ALTER TABLE IF EXISTS ONLY public.cars DROP CONSTRAINT IF EXISTS cars_pkey;
ALTER TABLE IF EXISTS ONLY public.cars DROP CONSTRAINT IF EXISTS cars_license_plate_number_key;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.tankerkoenig_stations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.stations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.invitation_keys ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.history_records ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.fuel_types ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.cars ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.tankerkoenig_stations_id_seq;
DROP TABLE IF EXISTS public.tankerkoenig_stations;
DROP SEQUENCE IF EXISTS public.stations_id_seq;
DROP TABLE IF EXISTS public.stations;
DROP SEQUENCE IF EXISTS public.invitation_keys_id_seq;
DROP TABLE IF EXISTS public.invitation_keys;
DROP SEQUENCE IF EXISTS public.history_records_id_seq;
DROP TABLE IF EXISTS public.history_records;
DROP SEQUENCE IF EXISTS public.fuel_types_id_seq;
DROP TABLE IF EXISTS public.fuel_types;
DROP SEQUENCE IF EXISTS public.cars_id_seq;
DROP TABLE IF EXISTS public.cars;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cars; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.cars (
    id integer NOT NULL,
    type character varying(100) NOT NULL,
    license_plate_number character varying(20) NOT NULL,
    owner_id integer NOT NULL
);


ALTER TABLE public.cars OWNER TO myuser;

--
-- Name: cars_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.cars_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cars_id_seq OWNER TO myuser;

--
-- Name: cars_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.cars_id_seq OWNED BY public.cars.id;


--
-- Name: fuel_types; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.fuel_types (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.fuel_types OWNER TO myuser;

--
-- Name: fuel_types_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.fuel_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fuel_types_id_seq OWNER TO myuser;

--
-- Name: fuel_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.fuel_types_id_seq OWNED BY public.fuel_types.id;


--
-- Name: history_records; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.history_records (
    id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    mileage double precision NOT NULL,
    price_per_litre double precision NOT NULL,
    litres double precision NOT NULL,
    car_id integer NOT NULL,
    fuel_type_id integer NOT NULL
);


ALTER TABLE public.history_records OWNER TO myuser;

--
-- Name: history_records_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.history_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.history_records_id_seq OWNER TO myuser;

--
-- Name: history_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.history_records_id_seq OWNED BY public.history_records.id;


--
-- Name: invitation_keys; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.invitation_keys (
    id integer NOT NULL,
    key character varying(32) NOT NULL
);


ALTER TABLE public.invitation_keys OWNER TO myuser;

--
-- Name: invitation_keys_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.invitation_keys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invitation_keys_id_seq OWNER TO myuser;

--
-- Name: invitation_keys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.invitation_keys_id_seq OWNED BY public.invitation_keys.id;


--
-- Name: stations; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.stations (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    latitude double precision,
    longitude double precision,
    owner_id integer NOT NULL
);


ALTER TABLE public.stations OWNER TO myuser;

--
-- Name: stations_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.stations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stations_id_seq OWNER TO myuser;

--
-- Name: stations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.stations_id_seq OWNED BY public.stations.id;


--
-- Name: tankerkoenig_stations; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.tankerkoenig_stations (
    id integer NOT NULL,
    tankerkoenig_id character varying(36) NOT NULL,
    name character varying(100) NOT NULL,
    brand character varying(100) NOT NULL,
    street character varying(200),
    house_number character varying(20),
    post_code integer,
    place character varying(100),
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    distance double precision,
    diesel double precision,
    e5 double precision,
    e10 double precision,
    is_open boolean NOT NULL,
    cached_at timestamp without time zone NOT NULL,
    cache_lat double precision,
    cache_lon double precision,
    cache_radius double precision
);


ALTER TABLE public.tankerkoenig_stations OWNER TO myuser;

--
-- Name: tankerkoenig_stations_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.tankerkoenig_stations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tankerkoenig_stations_id_seq OWNER TO myuser;

--
-- Name: tankerkoenig_stations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.tankerkoenig_stations_id_seq OWNED BY public.tankerkoenig_stations.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(320) NOT NULL,
    hashed_password character varying(1024) NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    is_verified boolean NOT NULL,
    forename character varying(100) NOT NULL,
    surname character varying(100) NOT NULL,
    invitation_key_id integer
);


ALTER TABLE public.users OWNER TO myuser;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO myuser;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: cars id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.cars ALTER COLUMN id SET DEFAULT nextval('public.cars_id_seq'::regclass);


--
-- Name: fuel_types id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.fuel_types ALTER COLUMN id SET DEFAULT nextval('public.fuel_types_id_seq'::regclass);


--
-- Name: history_records id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.history_records ALTER COLUMN id SET DEFAULT nextval('public.history_records_id_seq'::regclass);


--
-- Name: invitation_keys id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.invitation_keys ALTER COLUMN id SET DEFAULT nextval('public.invitation_keys_id_seq'::regclass);


--
-- Name: stations id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.stations ALTER COLUMN id SET DEFAULT nextval('public.stations_id_seq'::regclass);


--
-- Name: tankerkoenig_stations id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tankerkoenig_stations ALTER COLUMN id SET DEFAULT nextval('public.tankerkoenig_stations_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: cars; Type: TABLE DATA; Schema: public; Owner: myuser
--



--
-- Data for Name: fuel_types; Type: TABLE DATA; Schema: public; Owner: myuser
--



--
-- Data for Name: history_records; Type: TABLE DATA; Schema: public; Owner: myuser
--



--
-- Data for Name: invitation_keys; Type: TABLE DATA; Schema: public; Owner: myuser
--

INSERT INTO public.invitation_keys VALUES (1, '901563b82fa7adcbbc2a7e885f143c57');
INSERT INTO public.invitation_keys VALUES (2, '901563b82fa7adcbbc2a7e885f143c58');


--
-- Data for Name: stations; Type: TABLE DATA; Schema: public; Owner: myuser
--



--
-- Data for Name: tankerkoenig_stations; Type: TABLE DATA; Schema: public; Owner: myuser
--

INSERT INTO public.tankerkoenig_stations VALUES (31, '4c7b7a7f-d642-4bcd-8d29-eec72cbbd2a2', 'BK Tankstelle Manfred Mühlberger', 'BK', 'Münchner Straße', '29', 83043, 'Bad Aibling', 47.866146, 12.003221, 1, 1.909, 1.979, 1.919, true, '2026-05-15 16:03:13.069807', 47.865839217787574, 11.989173889160158, 5);
INSERT INTO public.tankerkoenig_stations VALUES (32, '2c4ddd6c-74b8-42f3-992a-d89044e458f6', 'Shell Bad Aibling Rosenheimer Str 68', 'Shell', 'Rosenheimer Str', '68', 83043, 'Bad Aibling', 47.855742, 12.015652, 2.3, 1.919, 1.989, 1.929, true, '2026-05-15 16:03:13.069807', 47.865839217787574, 11.989173889160158, 5);
INSERT INTO public.tankerkoenig_stations VALUES (33, '5a456548-a01c-4f0e-93c1-61ed13c770ca', 'Aral Tankstelle', 'ARAL', 'Aiblinger Au', '52 a', 83059, 'Kolbermoor', 47.851147, 12.017452, 2.7, 1.929, 1.999, 1.939, true, '2026-05-15 16:03:13.069807', 47.865839217787574, 11.989173889160158, 5);
INSERT INTO public.tankerkoenig_stations VALUES (34, '0a3ed70f-3854-4126-8b12-2d492a058b36', 'Esso Station', 'ESSO', 'Albert-Mayer-Str. 22', '', 83052, 'Bruckmühl', 47.882083, 11.933078, 4.6, 1.939, 1.929, 1.869, true, '2026-05-15 16:03:13.069807', 47.865839217787574, 11.989173889160158, 5);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: myuser
--

INSERT INTO public.users VALUES (1, 'max@tanker24.eu', '$argon2id$v=19$m=65536,t=3,p=4$JARPv/ADUWTo0Ts++1EzHA$ua3OHKCkng4dyK9kX9BMEmgjGYsclwV5ME0KP+lHr/k', true, false, false, 'Max', 'Mustermann', 1);


--
-- Name: cars_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.cars_id_seq', 1, false);


--
-- Name: fuel_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.fuel_types_id_seq', 1, false);


--
-- Name: history_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.history_records_id_seq', 1, false);


--
-- Name: invitation_keys_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.invitation_keys_id_seq', 2, true);


--
-- Name: stations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.stations_id_seq', 1, false);


--
-- Name: tankerkoenig_stations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.tankerkoenig_stations_id_seq', 34, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: cars cars_license_plate_number_key; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.cars
    ADD CONSTRAINT cars_license_plate_number_key UNIQUE (license_plate_number);


--
-- Name: cars cars_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.cars
    ADD CONSTRAINT cars_pkey PRIMARY KEY (id);


--
-- Name: fuel_types fuel_types_name_key; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.fuel_types
    ADD CONSTRAINT fuel_types_name_key UNIQUE (name);


--
-- Name: fuel_types fuel_types_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.fuel_types
    ADD CONSTRAINT fuel_types_pkey PRIMARY KEY (id);


--
-- Name: history_records history_records_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.history_records
    ADD CONSTRAINT history_records_pkey PRIMARY KEY (id);


--
-- Name: invitation_keys invitation_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.invitation_keys
    ADD CONSTRAINT invitation_keys_pkey PRIMARY KEY (id);


--
-- Name: stations stations_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_pkey PRIMARY KEY (id);


--
-- Name: tankerkoenig_stations tankerkoenig_stations_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tankerkoenig_stations
    ADD CONSTRAINT tankerkoenig_stations_pkey PRIMARY KEY (id);


--
-- Name: tankerkoenig_stations uix_tankerkoenig_id; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tankerkoenig_stations
    ADD CONSTRAINT uix_tankerkoenig_id UNIQUE (tankerkoenig_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_invitation_keys_key; Type: INDEX; Schema: public; Owner: myuser
--

CREATE UNIQUE INDEX ix_invitation_keys_key ON public.invitation_keys USING btree (key);


--
-- Name: ix_tankerkoenig_stations_tankerkoenig_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE UNIQUE INDEX ix_tankerkoenig_stations_tankerkoenig_id ON public.tankerkoenig_stations USING btree (tankerkoenig_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: myuser
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: cars cars_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.cars
    ADD CONSTRAINT cars_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: history_records history_records_car_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.history_records
    ADD CONSTRAINT history_records_car_id_fkey FOREIGN KEY (car_id) REFERENCES public.cars(id);


--
-- Name: history_records history_records_fuel_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.history_records
    ADD CONSTRAINT history_records_fuel_type_id_fkey FOREIGN KEY (fuel_type_id) REFERENCES public.fuel_types(id);


--
-- Name: stations stations_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: users users_invitation_key_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_invitation_key_id_fkey FOREIGN KEY (invitation_key_id) REFERENCES public.invitation_keys(id);


--
-- PostgreSQL database dump complete
--

\unrestrict zWajtr9aKU9Pjz7Sm8mIimybqv0K5gZF3kfo23K9IREBPHWmTxVT0bOfRdoXUbh

