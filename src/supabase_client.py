# src/supabase_client.py
# Подключение к Supabase для хранения пользователей и матчинга

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from supabase import create_client, Client
from src.config import cfg

load_dotenv()

SUPABASE_URL = cfg.SUPABASE_URL
SUPABASE_KEY = cfg.SUPABASE_KEY

_client: Optional[Client] = None


def get_client() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL и SUPABASE_KEY должны быть в .env")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


# ---- Пользователи ----

async def save_user(
    telegram_id: int,
    username: Optional[str] = None,
    gender: str = "",
    age: int = 0,
    looking_for: str = ""
) -> dict:
    """Создаёт или обновляет пользователя."""
    client = get_client()
    data = {
        "telegram_id": telegram_id,
        "username": username or "",
        "gender": gender,
        "age": age,
        "looking_for": looking_for,
        "updated_at": "now()"
    }
    # UPSERT
    result = client.table("users").upsert(
        data,
        on_conflict="telegram_id"
    ).execute()
    return result.data[0] if result.data else {}


async def get_user(telegram_id: int) -> Optional[dict]:
    client = get_client()
    result = client.table("users").select("*").eq("telegram_id", telegram_id).execute()
    return result.data[0] if result.data else None


# ---- Результаты теста ----

async def save_result(
    telegram_id: int,
    indotype_code: str,
    vectors: Dict[str, float],
    mods: Dict[str, float],
    gender: str = "",
    age: int = 0,
    looking_for: str = ""
) -> dict:
    """Сохраняет результат теста пользователя."""
    client = get_client()
    data = {
        "telegram_id": telegram_id,
        "indotype_code": indotype_code,
        "vectors": vectors,
        "mods": mods,
        "gender": gender,
        "age": age,
        "looking_for": looking_for
    }
    result = client.table("results").insert(data).execute()
    return result.data[0] if result.data else {}


async def get_latest_result(telegram_id: int) -> Optional[dict]:
    client = get_client()
    result = client.table("results") \
        .select("*") \
        .eq("telegram_id", telegram_id) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
    return result.data[0] if result.data else None


async def get_all_results() -> List[dict]:
    """Все результаты для матчинга."""
    client = get_client()
    result = client.table("results").select("*").execute()
    return result.data or []


async def delete_old_result(telegram_id: int) -> None:
    """Удаляет старые результаты пользователя перед повторным прохождением."""
    client = get_client()
    client.table("results").delete().eq("telegram_id", telegram_id).execute()


# ---- Лайки / матчи ----

async def save_like(from_id: int, to_id: int, direction: str = "like"):
    client = get_client()
    data = {
        "from_user_id": from_id,
        "to_user_id": to_id,
        "direction": direction
    }
    client.table("likes").upsert(
        data,
        on_conflict="from_user_id, to_user_id"
    ).execute()


async def get_mutual_likes(user_id: int) -> List[dict]:
    """Ищем взаимные лайки (симпатии)."""
    client = get_client()
    result = client.table("likes") \
        .select("*, users!likes_to_user_id_fkey(*)") \
        .eq("from_user_id", user_id) \
        .eq("direction", "like") \
        .execute()
    return result.data or []


# ---- Совместимости (кешированные) ----

async def save_compatibility(user_a: int, user_b: int, score: float):
    client = get_client()
    data = {
        "user_a_id": min(user_a, user_b),
        "user_b_id": max(user_a, user_b),
        "score": round(score, 2)
    }
    client.table("compatibility").upsert(
        data,
        on_conflict="user_a_id, user_b_id"
    ).execute()


async def get_best_matches(
    telegram_id: int,
    limit: int = 5,
    min_score: float = 50.0
) -> List[dict]:
    """Топ-5 совместимых пользователей."""
    client = get_client()
    result = client.table("compatibility") \
        .select("*, users!compatibility_user_b_id_fkey(*)") \
        .or_(f"user_a_id.eq.{telegram_id},user_b_id.eq.{telegram_id}") \
        .gte("score", min_score) \
        .order("score", desc=True) \
        .limit(limit) \
        .execute()
    return result.data or []
