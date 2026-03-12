"""Git history endpoints."""

from fastapi import APIRouter

from ..data import get_git_diff, get_git_log

router = APIRouter()


@router.get("/log")
async def git_log(limit: int = 200):
    return get_git_log(limit)


@router.get("/diff/{commit_hash}")
async def git_diff(commit_hash: str):
    return get_git_diff(commit_hash)
