--
-- PostgreSQL database dump
--

\restrict 6e3NzTrahjgMT3S0z9ccVuYWf75mXgfpwEaNAQSYhrhs6shqijsplVoBh9BwUJL

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
ALTER TABLE IF EXISTS ONLY public.history_records DROP CONSTRAINT IF EXISTS history_records_fuel_type_id_fkey;
ALTER TABLE IF EXISTS ONLY public.history_records DROP CONSTRAINT IF EXISTS history_records_car_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cars DROP CONSTRAINT IF EXISTS cars_owner_id_fkey;
DROP INDEX IF EXISTS public.ix_users_email;
DROP INDEX IF EXISTS public.ix_stations_tankerkoenig_id;
DROP INDEX IF EXISTS public.ix_invitation_keys_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.stations DROP CONSTRAINT IF EXISTS uix_tankerkoenig_id;
ALTER TABLE IF EXISTS ONLY public.stations DROP CONSTRAINT IF EXISTS stations_pkey;
ALTER TABLE IF EXISTS ONLY public.invitation_keys DROP CONSTRAINT IF EXISTS invitation_keys_pkey;
ALTER TABLE IF EXISTS ONLY public.history_records DROP CONSTRAINT IF EXISTS history_records_pkey;
ALTER TABLE IF EXISTS ONLY public.fuel_types DROP CONSTRAINT IF EXISTS fuel_types_pkey;
ALTER TABLE IF EXISTS ONLY public.fuel_types DROP CONSTRAINT IF EXISTS fuel_types_name_key;
ALTER TABLE IF EXISTS ONLY public.cars DROP CONSTRAINT IF EXISTS cars_pkey;
ALTER TABLE IF EXISTS ONLY public.cars DROP CONSTRAINT IF EXISTS cars_license_plate_number_key;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.stations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.invitation_keys ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.history_records ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.fuel_types ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.cars ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
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
    "timestamp" timestamp with time zone NOT NULL,
    mileage double precision NOT NULL,
    price_per_litre double precision NOT NULL,
    litres double precision NOT NULL,
    car_id integer NOT NULL,
    fuel_type_id integer NOT NULL,
    tankerkoenig_station_id character varying NOT NULL
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
-- Name: users id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: cars; Type: TABLE DATA; Schema: public; Owner: myuser
--

INSERT INTO public.cars VALUES (1, 'Pickup', 'HO-DF-7841', 1);
INSERT INTO public.cars VALUES (2, 'Schraeghecklimo', 'HO-LE-5889', 1);


--
-- Data for Name: fuel_types; Type: TABLE DATA; Schema: public; Owner: myuser
--

INSERT INTO public.fuel_types VALUES (1, 'diesel');
INSERT INTO public.fuel_types VALUES (2, 'e5');
INSERT INTO public.fuel_types VALUES (3, 'e10');


--
-- Data for Name: history_records; Type: TABLE DATA; Schema: public; Owner: myuser
--

INSERT INTO public.history_records VALUES (1, '2026-06-18 13:22:00+00', 66515, 1.669, 50.1, 1, 1, 'cd8ba6a6-9569-1ed6-8bd0-a6511bd08b15');
INSERT INTO public.history_records VALUES (2, '2026-06-18 13:22:00+00', 121100, 1.819, 25.12, 2, 2, 'e8e0e0a8-a6c5-4d25-824d-d6160e6fd5c7');
INSERT INTO public.history_records VALUES (4, '2026-06-18 13:24:00+00', 121500, 1.819, 37.75, 2, 2, '57861146-40bf-4231-ba1a-2db4c7ee66df');


--
-- Data for Name: invitation_keys; Type: TABLE DATA; Schema: public; Owner: myuser
--

INSERT INTO public.invitation_keys VALUES (1, '901563b82fa7adcbbc2a7e885f143c58');
INSERT INTO public.invitation_keys VALUES (2, '901563b82fa7adcbbc2a7e885f143c57');


--
-- Data for Name: stations; Type: TABLE DATA; Schema: public; Owner: myuser
--

INSERT INTO public.stations VALUES (3, 'f78bb4ef-0197-4c9c-aaf1-638bdebd2990', 'AVIA Tankstelle', 'AVIA', 'Ebersberger Str.', '31', 83022, 'Rosenheim', 47.864554, 12.121973, 0.5, 1.689, 1.829, 1.769, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (4, '57861146-40bf-4231-ba1a-2db4c7ee66df', 'ROSENHEIM - HUBERTUSSTRASSE 9', 'AGIP ENI', 'Hubertusstrasse', '9', 83022, 'Rosenheim', 47.855971678089, 12.110580426176, 0.9, 1.669, 1.819, 1.759, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (25, 'e8e0e0a8-a6c5-4d25-824d-d6160e6fd5c7', 'Walther Tankstelle', 'bft - Walther', 'Lackermannweg', '10', 83071, 'Stephanskirchen', 47.8652, 12.166, 3.7, 1.689, 1.819, 1.759, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (26, 'a877c7d9-ac7e-4106-b5dd-08d87dd2add1', 'Aral Tankstelle', 'ARAL', 'Rosenheimer Stra├ƒe', '30 a', 83059, 'Kolbermoor', 47.849876, 12.067706, 3.9, 1.679, 1.839, 1.779, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (2, 'cd8ba6a6-9569-1ed6-8bd0-a6511bd08b15', 'JET ROSENHEIM EBERSBERGSTR. 104', 'JET', 'EBERSBERGSTR.', '104', 83024, 'ROSENHEIM', 47.87321, 12.11096, 1.1, 1.669, 1.819, 1.759, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (1, 'fb456de7-807a-42aa-9510-c92bb58d9c3a', 'Shell Rosenheim Westerndorfer Str. 70', 'Shell', 'Westerndorfer Str.', '70', 83024, 'Rosenheim', 47.875147, 12.111214, 1.3, 1.679, 1.829, 1.769, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (16, '0f269d49-b196-49c4-b21d-df11a40cd3ff', 'Shell Rosenheim Aeussere Muenchener Str. 43', 'Shell', 'Aeussere Muenchener Str.', '43', 83026, 'Rosenheim', 47.852527, 12.100894, 1.7, 1.679, 1.829, 1.769, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (17, '7aac5ce2-e2e0-4f6b-a353-f953966bf1d0', 'Aral Tankstelle', 'ARAL', 'Kufsteiner Stra├ƒe', '57', 83022, 'Rosenheim', 47.848766, 12.127539, 1.9, 1.689, 1.839, 1.779, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (18, '51d4b592-a095-1aa0-e100-80009459e03a', 'JET ROSENHEIM KUFSTEINER STR. 85', 'JET', 'KUFSTEINER STR.', '85', 83026, 'ROSENHEIM', 47.8439, 12.1242, 2.3, 1.669, 1.819, 1.759, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (19, 'ce8fefd6-070c-4b99-8c5b-f24c06f00b6a', 'Tankstelle am Kaufland', 'Kaufland', '├äu├ƒere M├╝nchner Str.', '100', 83026, 'Rosenheim', 47.8485, 12.0918, 2.4, 1.659, 1.809, 1.749, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (20, '3d00f71d-afb6-4eab-bfad-f72bd4b643fa', 'Esso Tankstelle', 'ESSO', 'SALZBURGER STR. 43', '', 83071, 'STEPHANSKIRCHEN', 47.8589, 12.150872, 2.7, 1.699, 1.829, 1.839, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (21, '96915c76-348d-4dbc-9ce9-81dbd9bf2f8c', 'ALLGUTH GmbH  c/o Ralph Anton Reinhard', 'ALLGUTH', 'Kufsteiner Str.', '124', 83026, 'Rosenheim', 47.838541, 12.120173, 2.8, 1.659, 1.809, 1.749, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (22, '894dc0c5-383c-4328-91d8-ac14ab549c53', 'Aral Tankstelle', 'ARAL', 'Salzburger Stra├ƒe', '64', 83071, 'Stephanskirchen', 47.860394, 12.15434, 2.9, 1.699, 1.829, 1.769, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (23, 'c5c38c4f-9d55-4904-93c8-1be19e28cc90', 'Kolbermoor, Rosenheimer Str.', 'HEM', 'Rosenheimer Str.', '60', 83059, 'Kolbermoor', 47.84908, 12.07719, 3.3, 1.669, 1.819, 1.759, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);
INSERT INTO public.stations VALUES (24, '492294ce-7213-4204-95a1-8c0e6b8a7387', 'Esso Station', 'ESSO', 'Renkenweg 1', '', 83026, 'Rosenheim', 47.843253, 12.082456, 3.4, 1.679, 1.829, 1.779, true, '2026-06-18 15:23:58.332012', 47.86349273331226, 12.115859985351564, 5);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: myuser
--

INSERT INTO public.users VALUES (1, 'max@tanker24.eu', '$argon2id$v=19$m=65536,t=3,p=4$0HyAOKjOHHRymPEu71T0AQ$h9PmD1XUjOiMIzER0s1fuYdh6lVOKr9M8t9hmClj3rQ', true, false, false, 'Max', 'Mustermann', 2);


--
-- Name: cars_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.cars_id_seq', 2, true);


--
-- Name: fuel_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.fuel_types_id_seq', 3, true);


--
-- Name: history_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.history_records_id_seq', 4, true);


--
-- Name: invitation_keys_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.invitation_keys_id_seq', 2, true);


--
-- Name: stations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.stations_id_seq', 26, true);


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
-- Name: stations uix_tankerkoenig_id; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.stations
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
-- Name: ix_stations_tankerkoenig_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE UNIQUE INDEX ix_stations_tankerkoenig_id ON public.stations USING btree (tankerkoenig_id);


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
-- Name: users users_invitation_key_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_invitation_key_id_fkey FOREIGN KEY (invitation_key_id) REFERENCES public.invitation_keys(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 6e3NzTrahjgMT3S0z9ccVuYWf75mXgfpwEaNAQSYhrhs6shqijsplVoBh9BwUJL

