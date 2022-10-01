from typing import List
from typing import Optional

from demo_backend.api.v1.routes.route_login import get_current_user_from_token
from demo_backend.database import get_db
from demo_backend.database.models.jobs import Job
from demo_backend.database.models.users import User
from demo_backend.database.repository.jobs import create_new_job
from demo_backend.database.repository.jobs import delete_job_by_id
from demo_backend.database.repository.jobs import list_jobs
from demo_backend.database.repository.jobs import retreive_job
from demo_backend.database.repository.jobs import update_job_by_id
from demo_backend.schemas.jobs import JobCreate
from demo_backend.schemas.jobs import ShowJob
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

router = APIRouter()


def _job_to_show_job(a_job: Job) -> ShowJob:
    return ShowJob(
        id=a_job.id,
        title=a_job.title,
        company=a_job.company,
        company_url=a_job.company_url,
        location=a_job.location,
        description=a_job.description,
        date_posted=a_job.date_posted,
    )


@router.post("/create-job", response_model=ShowJob)
def create_job(
    l_job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    owner_id = current_user.id
    l_job: Job = create_new_job(job=l_job, db=db, owner_id=owner_id)
    return _job_to_show_job(l_job)


@router.get("/get/{id}", response_model=ShowJob)
def retreive_job_by_id(id: int, db: Session = Depends(get_db)):
    l_job: Optional[Job] = retreive_job(id=id, db=db)
    if not l_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job id {id} does not exist",
        )
    return _job_to_show_job(l_job)


@router.get("/all", response_model=List[ShowJob])
def retreive_all_jobs(db: Session = Depends(get_db)):
    l_jobs: List[Job] = list_jobs(db=db)
    l_show_jobs: List[ShowJob] = []
    for l_job in l_jobs:
        l_show_jobs.append(_job_to_show_job(l_job))
    return l_show_jobs


@router.put("/update/{id}")
def update_job(
    id: int,
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    owner_id = current_user.id
    job_retrieved = retreive_job(id=id, db=db)
    if not job_retrieved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {id} does not exist",
        )
    if job_retrieved.owner_id == current_user.id or current_user.is_superuser:
        _ = update_job_by_id(id=id, job=job, db=db, owner_id=owner_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to update.",
        )
    return {"detail": "Successfully updated data."}


@router.delete("/delete/{id}")
def delete_job(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    job = retreive_job(id=id, db=db)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {id} does not exist",
        )
    if job.owner_id == current_user.id or current_user.is_superuser:
        delete_job_by_id(id=id, db=db, owner_id=current_user.id)
        return {"detail": "Job Successfully deleted"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!"
    )
