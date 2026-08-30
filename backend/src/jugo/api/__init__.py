from __future__ import annotations

from fastapi import APIRouter

from jugo.domains.applications.router import router as applications_router
from jugo.domains.auth.router import router as auth_router
from jugo.domains.candidates.router import router as candidates_router
from jugo.domains.files.router import router as files_router
from jugo.domains.funnel.router import router as funnel_router
from jugo.domains.organization.router import router as organization_router
from jugo.domains.resumes.router import router as resumes_router
from jugo.domains.search.router import router as search_router
from jugo.domains.vacancies.router import router as vacancies_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(candidates_router)
api_router.include_router(resumes_router)
api_router.include_router(vacancies_router)
api_router.include_router(applications_router)
api_router.include_router(funnel_router)
api_router.include_router(search_router)
api_router.include_router(files_router)
api_router.include_router(organization_router)

__all__ = ["api_router"]
