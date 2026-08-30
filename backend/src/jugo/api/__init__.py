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
from jugo.modules.m1_screening.router import router as m1_screening_router
from jugo.modules.m2_risk.router import router as m2_risk_router
from jugo.modules.m3_questions.router import router as m3_questions_router
from jugo.modules.m4_searchmap.router import router as m4_searchmap_router
from jugo.modules.m5_analytics.router import router as m5_analytics_router
from jugo.modules.m6_scheduler.router import router as m6_scheduler_router

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
api_router.include_router(m1_screening_router)
api_router.include_router(m2_risk_router)
api_router.include_router(m3_questions_router)
api_router.include_router(m4_searchmap_router)
api_router.include_router(m5_analytics_router)
api_router.include_router(m6_scheduler_router)

__all__ = ["api_router"]
