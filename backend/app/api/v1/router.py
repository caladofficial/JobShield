from fastapi import APIRouter
from app.api.v1 import auth, jobs, sources, verification, contacts, exports, outreach, analytics, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(verification.router, prefix="/verification", tags=["verification"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
api_router.include_router(outreach.router, prefix="/outreach", tags=["outreach"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])