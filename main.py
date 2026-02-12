"""
This is main script where flask application is initialized.

Running this file directly should be avoided, it is ideal to run app.py or debug.py
"""
from dotenv import load_dotenv

from scripts.services.user_management import user_management_router
from scripts.services.home import home_router
from scripts.services.formula import formula_router
from scripts.services.formula_comparison import formula_comparison_router
from scripts.utils.security_utils.decorators import get_current_user

load_dotenv()

import gc
import os

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scripts.services.login import login_router
from jose import JWTError, jwt
from passlib.context import CryptContext
from scripts.services.plm import plm_router
from scripts.services.role_management import role_management_router
from scripts.services.table_config import table_config_router

secure_access = os.environ.get("SECURE_ACCESS", default=False)
gc.collect()

router = APIRouter(tags=["ping"])


@router.get("/api/formulation_tool/healthcheck")
async def ping():
    return {"status": 200}


app = FastAPI(
    title="Formulation Tool",
    version="1.0.0",
    description="Formulation Tool Web App",
    # root_url=Service.MODULE_PROXY,
    # openapi_url=os.environ.get("SW_OPENAPI_URL"),
    # docs_url=os.environ.get("SW_DOCS_URL"),
    # redoc_url=None,
)

# Compress(app)

# Register Routes

app.include_router(login_router)
app.include_router(home_router)
app.include_router(formula_router)
app.include_router(plm_router)
app.include_router(role_management_router)
app.include_router(formula_comparison_router)
app.include_router(table_config_router)

auth_enabled = [Depends(get_current_user)] if secure_access in [True, "true", "True"] else None

# Added dependency to each router instead while assigning app
    # because login_router doesn't have authentication
app.include_router(user_management_router, dependencies=auth_enabled)

origins = ["*"]

# if os.environ.get("ENABLE_CORS") in (True, "true", "True") and os.environ.get("CORS_URLS"):
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
    expose_headers=["*"]
)
