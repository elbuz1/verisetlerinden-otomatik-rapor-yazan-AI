import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.utils.auth import get_current_user
from app.config import get_settings
from app.services.data_parser import data_parser

settings = get_settings()
router = APIRouter(prefix="/api/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "json"}


def _get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _human_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


@router.post("")
@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ext = _get_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Desteklenmeyen dosya tipi: {ext}")

    content = await file.read()
    file_size = len(content)

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="Dosya boyutu cok buyuk (max 100MB)")
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Bos dosya yuklenemez")

    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_name)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    try:
        df = data_parser.parse(file_path, ext)
        columns_info = data_parser.get_columns_info(df)
        preview = data_parser.get_preview(df)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Dosya okunamadi: {str(e)}")

    dataset = Dataset(
        user_id=current_user.id,
        filename=unique_name,
        original_filename=file.filename,
        file_type=ext,
        file_size=file_size,
        file_path=file_path,
        row_count=len(df),
        column_count=len(df.columns),
        columns_info=columns_info,
        status="uploaded",
    )
    db.add(dataset)
    await db.flush()

    return {
        "id": dataset.id,
        "filename": file.filename,
        "file_type": ext,
        "file_size": file_size,
        "file_size_readable": _human_size(file_size),
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns_info": columns_info,
        "preview": preview,
        "status": "uploaded",
        "message": "Dosya basariyla yuklendi",
    }


@router.get("/datasets")
async def list_datasets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    result = await db.execute(
        select(Dataset)
        .where(Dataset.user_id == current_user.id)
        .order_by(Dataset.created_at.desc())
    )
    datasets = result.scalars().all()
    return [
        {
            "id": ds.id,
            "filename": ds.original_filename,
            "file_type": ds.file_type,
            "file_size": ds.file_size,
            "row_count": ds.row_count,
            "column_count": ds.column_count,
            "status": ds.status,
            "created_at": ds.created_at.isoformat() if ds.created_at else None,
        }
        for ds in datasets
    ]


@router.get("/datasets/{dataset_id}")
async def get_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == current_user.id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Veri seti bulunamadi")

    preview = None
    if os.path.exists(dataset.file_path):
        try:
            df = data_parser.parse(dataset.file_path, dataset.file_type)
            preview = data_parser.get_preview(df)
        except Exception:
            pass

    return {
        "id": dataset.id,
        "filename": dataset.original_filename,
        "file_type": dataset.file_type,
        "file_size": dataset.file_size,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "columns_info": dataset.columns_info,
        "status": dataset.status,
        "preview": preview,
        "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
    }
