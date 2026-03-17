from fastapi import APIRouter, HTTPException, Depends

router = APIRouter()

@router.get("/example")
async def example_endpoint():
    # return a simple JSON response
    return {"message": "Verweile doch, du bist so schön!"}
