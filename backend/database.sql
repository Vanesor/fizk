DROP TABLE IF EXISTS "user" CASCADE;

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,                     -- Auto-incrementing primary key
    username VARCHAR(100) UNIQUE NOT NULL,     -- Unique username, required
    email VARCHAR(255) UNIQUE NOT NULL,        -- Unique email, required
    hashed_password VARCHAR(255) NOT NULL,     -- Store HASHED password, required
    pubkey VARCHAR(66) UNIQUE NOT NULL,        -- Compressed Public Key hex (02/03 + 32 bytes), unique, required
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP -- Timestamp of creation (TIMESTAMPTZ stores timezone)
);

CREATE INDEX IF NOT EXISTS idx_user_username ON "user" (username);
CREATE INDEX IF NOT EXISTS idx_user_email ON "user" (email);
CREATE INDEX IF NOT EXISTS idx_user_pubkey ON "user" (pubkey);

-- Grant permissions (adjust user/db names as needed)
-- Example:
-- GRANT ALL PRIVILEGES ON TABLE "user" TO zkp_user;
-- GRANT USAGE, SELECT ON SEQUENCE user_id_seq TO zkp_user;