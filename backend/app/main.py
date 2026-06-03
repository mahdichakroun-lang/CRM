"""
CRM Internal — FastAPI Application Entry Point.
Architecture: DDD (Domain-Driven Design)
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.infrastructure.middleware import RequestLoggingMiddleware

# ── Import ALL domain models so Base.metadata knows about them ──
from app.domain.auth.models import User                    # noqa: F401
from app.domain.accounts.models import Account              # noqa: F401
from app.domain.contacts.models import Contact              # noqa: F401
from app.domain.leads.models import Lead                    # noqa: F401
from app.domain.deals.models import Deal                    # noqa: F401
from app.domain.activities.models import Activity           # noqa: F401
from app.domain.quotes.models import Quote                  # noqa: F401
from app.domain.tickets.models import Ticket, TicketMessage # noqa: F401
from app.domain.audit.models import AuditLog                # noqa: F401

# ── Import all API routers ──
from app.api.v1 import (
    auth_router,
    users_router,
    accounts_router,
    contacts_router,
    leads_router,
    deals_router,
    activities_router,
    quotes_router,
    tickets_router,
    dashboard_router,
    client_router,
    chatbot_router,
    email_router,
    ml_router,
)

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger = logging.getLogger("crm")
    # ── Startup: Database ──
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")

    # ── Startup: Seed demo users if DB is empty ──
    from app.database import SessionLocal
    from app.seed import seed_demo_users
    db = SessionLocal()
    try:
        seed_demo_users(db)
    finally:
        db.close()

    # ── Startup: RAG Auto-Index ──
    try:
        from app.rag.vector_store import get_collection_stats
        stats = get_collection_stats()
        if stats["total_chunks"] == 0:
            logger.info("🧠 RAG vector store is empty — auto-indexing documents...")
            # from app.rag.indexer import index_documents
            # index_documents(force=True)
            # logger.info("✅ RAG documents indexed successfully")
            logger.info("⚠️ RAG indexing skipped to prevent blocking startup.")
        else:
            logger.info(f"✅ RAG ready: {stats['total_chunks']} chunks in vector store")
    except Exception as e:
        logger.warning(f"⚠️ RAG init skipped: {e}")

    yield
    # ── Shutdown ──


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "CRM Interne — Gestion commerciale (Leads, Deals, Pipeline) "
            "et Helpdesk (Tickets) pour une SSII.\n\n"
            "Architecture DDD · FastAPI · MySQL"
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom middleware ──
    app.add_middleware(RequestLoggingMiddleware)

    # ── Register all API v1 routers ──
    api_prefix = "/api/v1"
    app.include_router(auth_router.router, prefix=api_prefix)
    app.include_router(users_router.router, prefix=api_prefix)
    app.include_router(accounts_router.router, prefix=api_prefix)
    app.include_router(contacts_router.router, prefix=api_prefix)
    app.include_router(leads_router.router, prefix=api_prefix)
    app.include_router(deals_router.router, prefix=api_prefix)
    app.include_router(activities_router.router, prefix=api_prefix)
    app.include_router(quotes_router.router, prefix=api_prefix)
    app.include_router(tickets_router.router, prefix=api_prefix)
    app.include_router(dashboard_router.router, prefix=api_prefix)
    app.include_router(client_router.router, prefix=api_prefix)
    app.include_router(chatbot_router.router, prefix=api_prefix)
    app.include_router(email_router.router, prefix=api_prefix)
    app.include_router(ml_router.router, prefix=api_prefix)

    # ── Health check ──
    @app.get("/health", tags=["System"])
    def health():
        return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

