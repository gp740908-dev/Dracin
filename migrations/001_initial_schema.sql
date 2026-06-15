CREATE TYPE access_level AS ENUM ('free', 'premium', 'exclusive');
CREATE TYPE series_status AS ENUM ('ongoing', 'completed');

CREATE TABLE series (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  cover_image_url VARCHAR(1024),
  description TEXT,
  genres TEXT[] NOT NULL DEFAULT '{}',
  total_episodes INTEGER NOT NULL DEFAULT 0,
  release_date DATE,
  view_count INTEGER NOT NULL DEFAULT 0,
  status series_status NOT NULL DEFAULT 'ongoing',
  is_exclusive BOOLEAN NOT NULL DEFAULT FALSE,
  access_level access_level NOT NULL DEFAULT 'free',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE episodes (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  cover_image_url VARCHAR(1024),
  video_path VARCHAR(1024) NOT NULL,
  description TEXT,
  genres TEXT[] NOT NULL DEFAULT '{}',
  episode_number INTEGER NOT NULL,
  duration INTEGER,
  release_date DATE,
  view_count INTEGER NOT NULL DEFAULT 0,
  status series_status NOT NULL DEFAULT 'ongoing',
  is_exclusive BOOLEAN NOT NULL DEFAULT FALSE,
  access_level access_level NOT NULL DEFAULT 'free',
  series_id INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE
);

CREATE TABLE partner_api_keys (
  id SERIAL PRIMARY KEY,
  partner_name VARCHAR(255) NOT NULL,
  api_key_hash VARCHAR(128) UNIQUE NOT NULL,
  allowed_access_level access_level NOT NULL DEFAULT 'free',
  allowed_origins TEXT[] NOT NULL DEFAULT '{}',
  rate_limit_per_minute INTEGER NOT NULL DEFAULT 120,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE request_logs (
  id SERIAL PRIMARY KEY,
  api_key_id INTEGER REFERENCES partner_api_keys(id),
  path VARCHAR(512) NOT NULL,
  method VARCHAR(16) NOT NULL,
  status_code INTEGER NOT NULL,
  is_exclusive_access BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
