# from typing import Optional
# from demo_backend.database.models.jobs import Job
# from demo_backend.database.models.users import User
# from demo_backend.database.repository.jobs import create_new_job
# from demo_backend.database.repository.jobs import retreive_job
# from demo_backend.database.repository.login import get_user
# from demo_backend.schemas.jobs import JobCreate
# from demo_backend.schemas.users import UserCreate
# from sqlalchemy.orm import Session
# from tests.conftest import random_job, random_user
# def test_create_and_read_job(db_session: Session):
#     # Create a new random job
#     l_job_schema: Optional[JobCreate] = random_job()
#     # Create a new random user
#     l_owner: Optional[UserCreate] = random_user(db_session=db_session, add_to_db=True)
#     # Test for whether either random object creation failed
#     assert isinstance(l_job_schema, JobCreate)
#     assert isinstance(l_owner, UserCreate)
#     # Get the user id for the new user from the database
#     l_owner_from_db: Optional[User] = get_user(a_email=l_owner.email, db=db_session)
#     # Ensure we successfuly retrieved the user from the database
#     assert isinstance(l_owner_from_db, User)
#     assert isinstance(l_owner_from_db.id, int)
#     # Create a new job with the random user's ID
#     l_job: JobCreate = create_new_job(
#         job=l_job_schema, db=db_session, owner_id=l_owner_from_db.id
#     )
#     # Read the new job using the random user's ID
#     retreived_job: Optional[Job] = retreive_job(id=l_job.id, db=db_session)
#     assert isinstance(retreive_job, Job)
#     # Ensure all the fields remained unmolested while writing and reading from the
#     # database.
#     assert retreived_job.title == l_job_schema.title
#     assert retreived_job.company == l_job_schema.company
#     assert retreived_job.company_url == l_job_schema.company_url
#     assert retreived_job.location == l_job_schema.location
#     assert retreived_job.description == l_job_schema.description
#     assert retreived_job.date_posted == l_job_schema.date_posted
#     assert retreived_job.owner_id == l_owner_from_db.id
