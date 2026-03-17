from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.future import select
from database import get_async_session
from models.example_model import example, exampleReturnModel, exampleCreateModel


router = APIRouter()

@router.get("/example")
async def example_endpoint():
    # return a simple JSON response
    return {"message": "Verweile doch, du bist so schön!"}


@router.get("/exampleFromDB")
async def example_from_db():
     async for session in get_async_session():
        result = await session.execute(select(example).order_by(example.id))
        examples = result.scalars().all()
        return_list = []
        for _example in examples:
            return_list.append(exampleReturnModel(text=_example.text))
        return return_list

@router.post("/exampleToDB")
async def example_to_db(example_create: exampleCreateModel):
    async for session in get_async_session():
        text = example_create.text
        new_example = example(text=text)
        session.add(new_example)
        await session.commit()
        return {"message": "Example added to the database!"}
