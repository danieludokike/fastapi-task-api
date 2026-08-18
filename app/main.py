from typing import List
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import Base, engine, get_db
from app.schemas import TaskCreate, TaskResponse, TaskUpdate

app = FastAPI(title="Task Management API")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post(
    "/tasks/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_task(
    task: TaskCreate, db: AsyncSession = Depends(get_db)
):
    return await crud.create_task(db=db, task=task)


@app.get("/tasks/", response_model=List[TaskResponse])
async def read_tasks(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await crud.get_tasks(db=db, skip=skip, limit=limit)


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def read_task(task_id: int, db: AsyncSession = Depends(get_db)):
    db_task = await crud.get_task(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(
    task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)
):
    updated_task = await crud.update_task(
        db=db, task_id=task_id, task_data=task
    )
    if updated_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return updated_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(
    task_id: int, db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_task(db=db, task_id=task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return None