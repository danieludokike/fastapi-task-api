from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import TaskModel
from app.schemas import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, task: TaskCreate) -> TaskModel:
    db_task = TaskModel(**task.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def get_tasks(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[TaskModel]:
    result = await db.execute(select(TaskModel).offset(skip).limit(limit))
    return result.scalars().all()


async def get_task(db: AsyncSession, task_id: int) -> Optional[TaskModel]:
    result = await db.execute(
        select(TaskModel).where(TaskModel.id == task_id)
    )
    return result.scalar_one_or_none()


async def update_task(
    db: AsyncSession, task_id: int, task_data: TaskUpdate
) -> Optional[TaskModel]:
    db_task = await get_task(db, task_id)
    if not db_task:
        return None

    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    await db.commit()
    await db.refresh(db_task)
    return db_task


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    db_task = await get_task(db, task_id)
    if not db_task:
        return False

    await db.delete(db_task)
    await db.commit()
    return True