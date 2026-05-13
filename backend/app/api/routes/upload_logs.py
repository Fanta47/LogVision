from __future__ import annotations

import secrets
from datetime import datetime
import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db_session

router = APIRouter(prefix="/api/logs", tags=["logs-upload"])

ALLOWED_APPLICATIONS: dict[str, set[str]] = {
    "MegaCash": {
        "Persistence",
        "MegaCashSLALogger",
        "MegaCashGetLazy",
        "MegaCashmapping",
        "MegaBroker",
        "MegaCashCacheViewLog",
        "EasyTest",
        "ExportImportConfig",
        "IODevices",
        "LifeCycleLog",
        "logInit",
        "Default",
        "BasicStruct",
        "BroadcastLogger",
    },
    "MegaCor": {
        "Persistence",
        "QuartzScheduler",
        "MegaCorSLALogger",
        "MegaBroker",
        "MegaCorCacheViewLog",
        "MegaCorGetLazy",
        "MegaCormapping",
        "MegaCorNotification",
        "Default",
        "EasyTest",
        "ExportImportConfig",
        "IODevices",
        "LifeCycleLog",
        "logInit",
        "BasicStruct",
        "BroadcastLogger",
        "DCLogger",
    },
    "MegaCommon": {
        "UploadedFiles",
        "QuartzScheduler",
        "Persistence",
        "MegaCommonSLALogger",
        "MegaCommonmapping",
        "MegaBroker",
        "MegaCommonCacheViewLog",
        "MegaCommonGetLazy",
        "IODevices",
        "LifeCycleLog",
        "logInit",
        "Default",
        "EasyTest",
        "ExportImportConfig",
        "BroadcastLogger",
        "BasicStruct",
    },
    "MegaCustody": {
        "Persistence",
        "QuartzScheduler",
        "SLALogger",
        "MegaCustodymapping",
        "MegaCustodySLALogger",
        "MegaBroker",
        "MegaCustodyCacheViewLog",
        "MegaCustodyGetLazy",
        "LifeCycleLog",
        "logInit",
        "Default",
        "EasyTest",
        "ExportImportConfig",
        "IODevices",
        "BasicStruct",
        "BroadcastLogger",
    },
}

UPLOAD_ROOT = Path(os.getenv("UPLOAD_ROOT", "uploads/raw"))


def build_upload_uid() -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = secrets.token_hex(4)
    return f"u_{stamp}_{suffix}"


@router.post("/upload")
async def upload_log_file(
    file: UploadFile = File(...),
    application_key: str = Form(...),
    component_name: str = Form(...),
    db: Session = Depends(get_db_session),
) -> dict:
    if application_key not in ALLOWED_APPLICATIONS:
        raise HTTPException(status_code=400, detail="application_key non autorisee")
    if component_name not in ALLOWED_APPLICATIONS[application_key]:
        raise HTTPException(status_code=400, detail="component_name non autorise pour cette application")

    original_name = file.filename or "uploaded.log"
    suffix = Path(original_name).suffix.lower()
    if suffix not in {".log", ".txt"}:
        raise HTTPException(status_code=400, detail="Seuls les fichiers .log et .txt sont autorises")

    upload_uid = build_upload_uid()
    target_dir = UPLOAD_ROOT / application_key / component_name
    target_dir.mkdir(parents=True, exist_ok=True)

    stored_file_name = f"{upload_uid}.log"
    target_path = target_dir / stored_file_name
    payload = await file.read()
    target_path.write_bytes(payload)

    status_value = "uploaded"
    try:
        db.execute(
            text(
                """
                INSERT INTO log_upload(
                  upload_uid, original_file_name, stored_file_name, stored_path,
                  application_key, component_name, status
                ) VALUES (
                  :upload_uid, :original_file_name, :stored_file_name, :stored_path,
                  :application_key, :component_name, :status
                )
                """
            ),
            {
                "upload_uid": upload_uid,
                "original_file_name": original_name,
                "stored_file_name": stored_file_name,
                "stored_path": str(target_path.as_posix()),
                "application_key": application_key,
                "component_name": component_name,
                "status": status_value,
            },
        )
        db.commit()
    except SQLAlchemyError:
        db.rollback()

    return {
        "upload_uid": upload_uid,
        "original_file_name": original_name,
        "stored_file_name": stored_file_name,
        "stored_path": str(target_path.as_posix()),
        "application_key": application_key,
        "component_name": component_name,
        "status": status_value,
    }


@router.get("/uploads")
def list_uploads(db: Session = Depends(get_db_session)) -> list[dict]:
    try:
        rows = db.execute(
            text(
                """
                SELECT upload_uid, original_file_name, stored_file_name, stored_path,
                       application_key, component_name, uploaded_at, status
                FROM log_upload
                ORDER BY uploaded_at DESC
                LIMIT 500
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]
    except SQLAlchemyError:
        return []


@router.get("/uploads/{upload_uid}")
def get_upload(upload_uid: str, db: Session = Depends(get_db_session)) -> dict:
    try:
        row = db.execute(
            text(
                """
                SELECT *
                FROM log_upload
                WHERE upload_uid = :upload_uid
                """
            ),
            {"upload_uid": upload_uid},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="upload introuvable")
        return dict(row)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="base de donnees indisponible")
