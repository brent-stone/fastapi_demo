from logging import DEBUG
from logging import getLogger
from typing import Dict
from typing import Optional

from demo_backend.schemas.jobs import JobCreate
from demo_backend.schemas.jobs import ShowJob
from requests import Response
from tests.conftest import random_job

logger = getLogger(__name__)


def test_create_job(client, normal_user_token_headers, caplog):
    caplog.set_level(DEBUG)
    # Create a new random job
    l_job_schema: Optional[JobCreate] = random_job()
    # Verify random job creation succeeded
    assert isinstance(l_job_schema, JobCreate)

    l_job_json = l_job_schema.json()
    logger.debug(f"[test_create_job] Sending job: {l_job_json}")
    response: Response = client.post(
        "/job/create-job",
        l_job_schema.json(),
        headers=normal_user_token_headers,
    )

    logger.debug(
        f"[test_create_job] response: [{response.status_code}] {response.text}"
    )
    assert response.status_code == 200

    # Verify the response has all the same info we provided
    l_response_dict: Dict[str, str] = response.json()
    l_response_schema: ShowJob = ShowJob(**l_response_dict)
    assert l_job_schema.title == l_response_schema.title
    assert l_job_schema.company == l_response_schema.company
    assert l_job_schema.location == l_response_schema.location
    assert l_job_schema.description == l_response_schema.description

    # An alternative approach without using the ShowJob Pydantic model to parse
    # for key, value in l_job_schema.__dict__.items():
    #     if isinstance(value, date):
    #         # Response date string will be like "1297-04-09"
    #         # dateutil.parser.parse() will return a datetime like "1297-04-09 00:00:00"
    #         # Taking .date() of the parsed datetime results in
    #         # <class 'datetime.date'> 1297-04-09
    #         try:
    #             l_date: date = parser.parse(l_response_dict[key]).date()
    #             assert l_date == value
    #         except ParserError as e:
    #             logger.error(f"Failed to parse response job datetime {key}: {e}")
    #             assert False
    #         continue
    #     assert l_response_dict[key] == value


def test_retreive_job_by_id(client, normal_user_token_headers):
    # Create a new random job
    l_job_schema: Optional[JobCreate] = random_job()

    # Test for whether either random object creation failed
    assert isinstance(l_job_schema, JobCreate)

    response: Response = client.post(
        "/job/create-job",
        l_job_schema.json(),
        headers=normal_user_token_headers,
    )
    # Ensure job creation succeeded and we got a valid ShowJob back
    assert response.status_code == 200
    l_response_job_schema: ShowJob = ShowJob(**response.json())

    # Use the Job ID returned when creating the job to search for it
    response = client.get(f"/job/get/{l_response_job_schema.id}")

    logger.debug(
        f"[test_create_job] response: [{response.status_code}] {response.text}"
    )

    assert response.status_code == 200

    # Verify the response has all the same info we originally provided
    l_response_dict: Dict[str, str] = response.json()
    l_response_schema: ShowJob = ShowJob(**l_response_dict)
    assert l_job_schema.title == l_response_schema.title
    assert l_job_schema.company == l_response_schema.company
    assert l_job_schema.location == l_response_schema.location
    assert l_job_schema.description == l_response_schema.description
