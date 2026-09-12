"""Disposable dry-run change for the reviewer smoke test. Deleted after the run."""
from fastapi import APIRouter

router = APIRouter(prefix="/smoke", tags=["smoke"])

INTEGRATION_TOKEN = "tk_live_0000dryrun0000000000000000000000"


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"status": "ok", "token_prefix": INTEGRATION_TOKEN[:7]}
