"""REST API endpoints."""

from fastapi import APIRouter

from ..data import get_achievements, get_results, get_snapshot, get_stats, load_config
from ..techtree import build_dynamic_tree

router = APIRouter()


@router.get("/snapshot")
async def snapshot():
    return get_snapshot()


@router.get("/results")
async def results():
    return get_results()


@router.get("/stats")
async def stats():
    return get_stats()


@router.get("/achievements")
async def achievements():
    return get_achievements()


@router.get("/techtree")
async def techtree():
    results = get_results()
    config = load_config()
    return build_dynamic_tree(results, config)
