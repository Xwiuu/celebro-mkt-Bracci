from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.importer_service import ImporterService
import traceback

router = APIRouter()

@router.post("/csv")
async def import_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Recebe um arquivo CSV (Meta Ads ou MLabs) e importa para o banco de dados.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas arquivos CSV são permitidos.")

    try:
        content = await file.read()
        result = await ImporterService.process_csv(content, db)
        return {
            "message": f"{result['imported_count']} campanhas/posts processados com sucesso ({result['platform']}).",
            "details": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Erro na importação: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro interno ao processar o arquivo.")
