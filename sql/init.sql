-- Инициализация БД для Trezorium Dating
-- Запустить в Supabase SQL Editor

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS results (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL REFERENCES users(telegram_id),
    indotype_code VARCHAR(10) NOT NULL,
    vectors JSONB DEFAULT '{}',
    mods JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_results_telegram ON results(telegram_id);
CREATE INDEX IF NOT EXISTS idx_results_created ON results(created_at DESC);

CREATE TABLE IF NOT EXISTS likes (
    id BIGSERIAL PRIMARY KEY,
    from_user_id BIGINT NOT NULL REFERENCES users(telegram_id),
    to_user_id BIGINT NOT NULL REFERENCES users(telegram_id),
    direction VARCHAR(10) DEFAULT 'like',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(from_user_id, to_user_id)
);

CREATE INDEX IF NOT EXISTS idx_likes_from ON likes(from_user_id);
CREATE INDEX IF NOT EXISTS idx_likes_to ON likes(to_user_id);

CREATE TABLE IF NOT EXISTS compatibility (
    user_a_id BIGINT NOT NULL REFERENCES users(telegram_id),
    user_b_id BIGINT NOT NULL REFERENCES users(telegram_id),
    score DECIMAL(5,2) NOT NULL DEFAULT 0,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY(user_a_id, user_b_id)
);

CREATE INDEX IF NOT EXISTS idx_compatibility_score ON compatibility(score DESC);
