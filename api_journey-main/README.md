
# Journey API

The Journey API is a Django REST API that provides CRUD (Create, Read, Update, Delete) operations for managing journeys.

## API Endpoints

### 1. `JourneyAPIView`

The `JourneyAPIView` is a Django REST API view that handles the CRUD operations for the `Journey` model.

### GET Request

### Query Parameters
- `start_index` (optional, default: 0): Specifies the starting index of the journeys to retrieve.
- `end_index` (optional, default: 10): Specifies the ending index of the journeys to retrieve.
- `user_id` (optional): Filters journeys to show only those accessible by the specified user ID. If not provided or set to 0, shows journeys accessible to all users based on hierarchical permissions.

### Authorization
The endpoint employs hierarchical permissions to determine access:
- Users can view journeys associated with their direct and indirect reports based on a manager-child relationship.
- If `user_id` is provided, the API checks permissions for that user. If `user_id` is 0 or not provided, it defaults to the token user's permissions.

### Response
A JSON object containing:
- `total_count`: Total number of journeys matching the criteria.
- `journeys`: An array of journey objects, each including fields such as `id`, `username`, `application_name`, `name`, `description`, `allow_contacts_to_restart`, `published`, `is_deleted`, `segment`, `user`, and `application`.

#### POST Request

- **Endpoint**: `journey/journey`
- **Description**: Creates a new journey.
- **Request Body**: A JSON object containing the journey details.
- **Response**: The created journey object in JSON format.

#### PUT Request

- **Endpoint**: `journey/journey/{journey_id}/`
- **Description**: Updates an existing journey.
- **Request Body**: A JSON object containing the updated journey details.
- **Response**: The updated journey object in JSON format.

#### DELETE Request

- **Endpoint**: `journey/journey/{journey_id}/`
- **Description**: Soft deletes an existing journey.
- **Response**: A success message indicating that the journey has been soft deleted.

### 2. `JourneyShowAPIView`

The `JourneyShowAPIView` is a Django REST API view that handles the retrieval of a specific journey.

#### GET Request

- **Endpoint**: `journey/journey/{journey_id}/`
- **Description**: Retrieves the details of a specific journey.
- **Response**: A JSON object containing the journey details, including the name, description, category, `allow_contacts_to_restart`, and `published` fields.

## Error Handling

The API views handle various exceptions that may occur during the processing of requests. In case of an error, the API views return appropriate HTTP status codes and error messages. The following are the possible error responses:

- **400 Bad Request**: Returned when the request data is invalid or when the required parameters are not provided.
- **404 Not Found**: Returned when the requested journey is not found or has been deleted.
- **500 Internal Server Error**: Returned when an unexpected error occurs during the processing of the request.

The API views also use a logger to log relevant information, warnings, and errors for debugging and monitoring purposes.

### 3. `JourneyEventsListAPIView`

The `JourneyEventsListAPIView` is a Django REST API view that handles the CRUD (Create, Read, Update, Delete) operations for the `JourneyEvents` model.

#### GET Request
- **Endpoint**: `journey/journey-event/{journey_id}`
- **Description**: Retrieves a list of all events for a specific journey.
- **Response**: A list of journey event objects in JSON format.

<!-- #### POST Request
- **Endpoint**: `journey/journey-event/`
- **Description**: Creates a new journey event.
- **Request Body**: A JSON object containing the journey event details.
- **Response**: The created journey event object in JSON format.

#### PUT Request
- **Endpoint**: `journey/event/{event_id}/`
- **Description**: Updates an existing journey event.
- **Request Body**: A JSON object containing the updated journey event details.
- **Response**: A success message indicating that the journey event has been updated. -->
#### POST Request

- **Endpoint**: `journey/journey-event/`
- **Description**: Creates a new journey event.
- **Request Body**: A JSON object containing the journey event details. Include the following required fields:
  - `campaign` (integer): The ID of the campaign associated with the event.
  - `interview_type` (string): Specifies the type of interview event ("bot call", "one on one", etc.).
  - `hiring_manager_ids` (array of integers, optional): IDs of hiring managers associated with the event.
  - Additional optional fields such as `relative_time_period_interval`, `relative_time_period_unit`, `close_link_within_interval`, `close_link_within_unit`, etc.
  
- **Response**: Returns the created journey event object upon success.

#### PUT Request

- **Endpoint**: `journey/event/{event_id}/`
- **Description**: Updates an existing journey event identified by `event_id`.
- **Request Body**: A JSON object containing the updated journey event details. Include one or more fields to update:
  - `campaign` (integer): Updated campaign ID associated with the event.
  - `interview_type` (string): Updated type of interview event ("bot call", "one on one", etc.).
  - `hiring_manager_ids` (array of integers, optional): Updated IDs of hiring managers associated with the event.
  - Additional optional fields such as `relative_time_period_interval`, `relative_time_period_unit`, `close_link_within_interval`, `close_link_within_unit`, etc.
  
- **Response**: Returns a success message indicating that the journey event with `event_id` has been updated successfully.

## Serializers Validation

### Bot Call

When creating or updating a bot call event (`interview_type` = "bot call"), the following validations are applied:

- Checks if an interview channel exists for the campaign.
- Ensures that a call channel exists for the campaign.
- Requires fields: `skills`, `bot_language`, `bot`, `campaign`.

### One on One

When creating or updating a one-on-one interview event (`interview_type` = "one on one"), the following validations are applied:

- Checks if an interview channel exists for the campaign.
- Requires `hiring_manager_ids` when an interview channel exists.
- Checks if a call channel exists for the campaign if `bot` is included.
- Requires field: `campaign`. Additional fields (`state`, `city`, `addr1`, `addr2`) are required unless `Mark_as_Online` is True.


#### DELETE Request
- **Endpoint**: `/journey/event/{event_id}/`
- **Description**: Soft deletes an existing journey event.
- **Response**: A success message indicating that the journey event has been soft deleted.

### 4. `ShowjourneyeventsListAPIView`

The `ShowjourneyeventsListAPIView` is a Django REST API view that handles the retrieval of a specific journey event.

#### GET Request
- **Endpoint**: `journey/event/{event_id}/`
- **Description**: Retrieves the details of a specific journey event.
- **Response**: A JSON object containing the journey event details.

### Error Handling

The API views handle various exceptions that may occur during the processing of requests. In case of an error, the API views return appropriate HTTP status codes and error messages. The following are the possible error responses:

- **400 Bad Request**: Returned when the request data is invalid or when the required parameters are not provided.
- **404 Not Found**: Returned when the requested journey event is not found or has been deleted.
- **500 Internal Server Error**: Returned when an unexpected error occurs during the processing of the request.

The API views also use a logger to log relevant information, warnings, and errors for debugging and monitoring purposes.

### 5. Add Job API

The Add Job API (`AddJobAPIView`) automates the creation of entries in the `CandidateJourney` table based on jobs from `AddToJobs`.

### Purpose

The API retrieves jobs where `journey_update=False` and `error_occurred=False` from `AddToJobs` and initializes corresponding entries in `CandidateJourney` using the first event (`parent_id=0`) associated with each job's `journey_id`.

### How It Works

1. **GET Request Handling**: 
   - Fetch jobs from `AddToJobs` where `journey_update=False` and `error_occurred=False`.
   - Identify the first event (`parent_id=0`) for each job's `journey_id` from `JourneyEvents`.
   - Calculate the journey start time based on the relative time period (interval and unit) defined in the first event.

2. **CandidateJourney Creation**:
   - Create a new entry in `CandidateJourney` with details fetched from `AddToJobs` and `JourneyEvents`.
   - Include `job_id`, `candidate_id`, `journey_id`, `start_time`, `journey_event_id`, and other relevant metadata.

3. **Flag Update**:
   - Set `journey_update=True` and `error_occurred` appropriately for the processed job in `AddToJobs` to prevent duplicate entries and mark errors.

### Error Handling

- Logs errors if no `JourneyEvents` are found for a job's `journey_id`.
- Marks jobs with `error_occurred=True` if any error occurs during processing.
- Returns appropriate error messages and `500 Internal Server Error` status codes for unexpected errors.

### Usage

To use the Add Job API:
- Send a GET request to `/journey/addtojob-journey-update/`.
- Ensure proper Django environment setup with necessary permissions and authentication.
- Monitor logs for job processing issues or API execution errors.

### 6. Candidate Next Event Addition API

The Candidate Next Event Addition API (`CandidateNextEventAdditionAPIView`) automates the handling of completed and cancelled campaigns in the `CandidateJourney` and `AddToJobs` tables.

### Purpose

This API identifies completed and cancelled campaigns in `CandidateJourney`, updates their statuses in `AddToJobs`, and adds next events to `CandidateJourney` based on qualifying criteria.

### How It Works

1. **GET Request Handling**: 
   - Retrieves completed and cancelled campaigns from `CandidateJourney`.
   - Processes each event to update its status in `AddToJobs` and potentially add the next event to `CandidateJourney`.

2. **Processing Completed Campaigns**: 
   - Checks for completed campaigns (`campaign_status='completed'`).
   - Retrieves the corresponding `JourneyEvents` and `CandidateStatuses`.
   - Determines if the campaign is rejected or qualifies for the next event based on qualifying criteria.
   - Adds the next event to `CandidateJourney` if conditions are met and updates `AddToJobs` accordingly.

3. **Processing Cancelled Campaigns**:
   - Checks for cancelled campaigns (`campaign_status='cancelled'`).
   - Updates the status of the associated job in `AddToJobs` to 'cancelled'.

4. **Response Handling**:
   - Returns a success message if events are processed successfully, along with status updates in `AddToJobs`.
   - Logs errors encountered during the processing of campaigns.

### Error Handling

- Logs errors if no `JourneyEvents`, `CandidateStatuses`, or `AddToJobs` entries are found.
- Returns appropriate error messages and `500 Internal Server Error` status codes for unexpected errors.

### Usage

To use the Candidate Next Event Addition API:
- Send a GET request to `/journey/addnextevent-by-camapignstatus/`.
- Ensure proper Django environment setup with necessary permissions and authentication.
- Monitor logs for job processing issues or API execution errors.

### 7. Job Dashboard API

The Job Dashboard API (`JobDashboardView`) retrieves detailed information about a specific job and its associated journey events, categorized by candidate statuses.

### Purpose

This API fetches and aggregates data related to a job's journey events and the status of candidates associated with those events.

### How It Works

1. **GET Request Handling**: 
   - Accepts a `job_id` parameter and optionally a `status` filter as query parameters.
   - Validates input using `JobDashboardSerializer`. Returns a `400 Bad Request` if validation fails.

2. **Data Retrieval and Aggregation**:
   - Fetches details of the job from `JobDetails` based on the provided `job_id`.
   - Retrieves candidate statuses from `CandidateStatuses` based on the provided `status`.
   - Retrieves journey events from `JourneyEvents` associated with the job's `journey_id`.
   - Counts the number of candidates in each status for each journey event using `CampaignTriggers`.

3. **Response Format**:
   - Constructs a JSON response where each journey event's details are categorized under its interview type.
   - Each interview type includes counts of candidates in each status, mapped by their display names.

4. **Error Handling**:
   - Logs warnings if the job or journey events are not found, or if no statuses match the provided criteria.
   - Returns appropriate error messages and status codes (`400` for not found or validation errors, `500` for unexpected errors).

### Usage

To use the Job Dashboard API:
- Send a GET request to `job-candidatestatus-counts/<job_id>`, where `<job_id>` is the ID of the job.
- Optionally, include `?status=<status>` to filter results by candidate status.
- Ensure proper Django environment setup with necessary permissions and authentication.
- Monitor logs for warnings or errors encountered during API execution.

### 8. CandidateView API

The `CandidateView` API endpoint facilitates the retrieval of candidate details based on specified criteria.

#### Purpose

This API fetches candidate details from `CandidateDetails` based on provided parameters such as `status_id`, `journey_id`, `journey_event_id`, `job_id`, `start_index`, and `end_index`.

#### How It Works

1. **POST Request Handling**: 
   - Handles POST requests to retrieve candidate details.
   - Utilizes `CandidateSerializer` for data validation. Returns a `400 Bad Request` if validation fails.

2. **Data Retrieval**:
   - Retrieves candidate IDs from `CampaignTriggers` based on `status_id`, `journey_id`, `journey_event_id`, and `job_id`.
   - Fetches candidate details from `CandidateDetails` for the retrieved IDs within the specified index range (`start_index` to `end_index`).

3. **Response Format**:
   - Constructs a JSON response where each object contains detailed information about a candidate within the specified index range.
   - Includes attributes such as `first_name`, `last_name`, `email`, `mobile_no`, and other relevant candidate details.
   - Each candidate object also includes `total_count`, indicating the total number of candidates matching the filter criteria.

4. **Error Handling**:
   - Logs warnings or errors for validation issues, data retrieval problems, or unexpected errors.
   - Returns appropriate error messages and status codes (`400` for validation errors, `500` for unexpected errors).

#### Usage

To use the CandidateView API:
- Send a POST request to the endpoint `'candidate_details-for-statuscounts/'`.
- Provide the necessary parameters (`status_id`, `journey_id`, `journey_event_id`, `job_id`, `start_index`, `end_index`) in the request body.
- Ensure proper Django environment setup with necessary permissions and authentication.
- Monitor logs for warnings or errors encountered during API execution.


# Journey Management API Documentation

## Overview

This document provides documentation for the Journey Management API, which facilitates management of journey events, segment categories, bots, campaigns, and user data.

## API Endpoints

### Get Segment Categories

- **Endpoint**: `/journey/get-segment-categories/<int:journey_id>/`
- **Method**: GET
- **Description**: Retrieves segment categories associated with a specific journey identified by `journey_id`.
- **Response**: Returns a JSON array containing segment category details including `id` and `category_name`.

### Get Bots by Segment Category

- **Endpoint**: `/journey/get-bots-by-segment-category/<int:segment_category_id>/`
- **Method**: GET
- **Description**: Retrieves bots belonging to a specific segment category identified by `segment_category_id`.
- **Response**: Returns a JSON array of bots with `bot_id` and `bot_name`.

### Get Campaigns by Segment Category

- **Endpoint**: `/journey/get-campaigns-by-segment-category/<int:segment_category_id>/`
- **Method**: GET
- **Description**: Retrieves campaigns associated with a specific segment category identified by `segment_category_id`.
- **Response**: Returns a JSON array of campaigns with `id` and `campaign_name`.

### Check Campaign Interview

- **Endpoint**: `/journey/get-campaign-event-details/<int:campaign_id>/`
- **Method**: GET
- **Description**: Checks the presence of interview or bot call channels for a specific campaign identified by `campaign_id`.
- **Query Parameters**: 
  - `interview_type` (string): Type of interview to check ('one on one' or 'bot call').
- **Response**: Returns messages indicating the presence or absence of interview and bot call channels.

### Get Users by Application ID

- **Endpoint**: `/journey/managers/by-application/`
- **Method**: GET
- **Description**: Retrieves users (managers) associated with a specific application identified by `application_id`.
- **Response**: Returns a JSON array of users with `id` and `username`.


### Get Segments by Application ID

- **Endpoint**: `/journey/segments/by-application/`
- **Method**: GET
- **Description**: Retrieves segments associated with a specific application identified by `application_id`.
- **Response**: Returns a JSON array of segments with `id` and `segment_name`.

# Journey Flow API Documentation

## Overview

This document provides comprehensive documentation for the Journey Management API, detailing each available endpoint and the input/output format for each request and response. The API is designed to manage journey events, candidate journeys, job data, and campaign data efficiently.

## API Endpoints

### Get Job Data

- **Endpoint**: `/journey/job_data/<int:candidate_id>/<int:job_id>/`
- **Method**: GET
- **Description**: Retrieves job data for a specific candidate and job.
- **Input**:
  - `candidate_id`: ID of the candidate.
  - `job_id`: ID of the job.
- **Response**:
  - List of objects containing:
    - `add_to_jobs_data`
    - `job_details_data`

### Get Journey Details

- **Endpoint**: `/journey/journey-details/<int:candidate_id>/<int:job_id>/`
- **Method**: GET
- **Description**: Retrieves journey details for a specific candidate and job.
- **Input**:
  - `candidate_id`: ID of the candidate.
  - `job_id`: ID of the job.
- **Response**:
  - `journey_details`
    - `events_count`

### Get Candidate Journey Details

- **Endpoint**: `/journey/candidate-journey-details/<int:candidate_id>/<int:job_id>/`
- **Method**: GET
- **Description**: Retrieves candidate journey details, including completed and in-process events, and reschedule counts.
- **Input**:
  - `candidate_id`: ID of the candidate.
  - `job_id`: ID of the job.
- **Response**:
  - `candidate_journey_details`
  - `completed_events`
  - `in_process_events`

### Get Campaign Data

- **Endpoint**: `/journey/campaign-data/<int:candidate_journey_id>/`
- **Method**: GET
- **Description**: Retrieves campaign data for a specific candidate journey.
- **Input**:
  - `candidate_journey_id`: ID of the candidate journey.
- **Response**:
  - List of objects containing:
    - `campaign_trigger_data`
    - `campaign_event_data`

### Get Journey Event Details

- **Endpoint**: `/journey/journey-event-details/<int:candidate_id>/<int:job_id>/`
- **Method**: GET
- **Description**: Retrieves journey event details, including step status, results, ratings, and reschedule counts.
- **Input**:
  - `candidate_id`: ID of the candidate.
  - `job_id`: ID of the job.
- - **Response**:
  ```json
  {
    "events": [
      {
        "step_started_time": "YYYY-MM-DDTHH:MM:SSZ",
        "step_ended": "YYYY-MM-DDTHH:MM:SSZ",
        "status": "completed",
        "result": "pass",
        "rating": 80,
        "reschedule_count": 2,
        "Other journey event details"
      },
      {
        "step_started_time": "YYYY-MM-DDTHH:MM:SSZ",
        "step_ended": null,
        "status": "in process",
        "result": "fail",
        "rating": 60,
        "reschedule_count": 0,
        "Other journey event details"
      },
       "Additional journey events"
    ],
    "global_info": {
      "completed_events": 5,
      "in_process_events": 2,
      "current_step": 6,
      "total_steps": 8
    },
  }
### Candidate Calls Emails SMS Details

- **Endpoint**: `/journey/candidate-job-details/<int:candidate_id>/<int:job_id>/`
- **Method**: GET
- **Description**: Retrieves details of calls, emails, and SMS for a specific candidate and job, including reschedule counts.
- **Input**:
  - `candidate_id`: ID of the candidate.
  - `job_id`: ID of the job.
- **Response**:
  ```json
  [
    {
      "id": 61,
      "calls": 1,
      "sms": 1,
      "emails": 1,
      "reschedule": 96
    },
    {
      "id": 62,
      "calls": 1,
      "sms": 1,
      "emails": 1,
      "reschedule": 1
    }
  ]
### Procedure Explanation

The stored procedure `smsemailcallfrequency` is designed to retrieve and calculate counts of calls, SMS, emails, and reschedules related to a specific candidate and job. Here's a detailed explanation of its functionality:

1. **Fetching `journey_id`**:
   - It begins by fetching the `journey_id` from the `add_to_jobs` table based on the provided `candidate_id` and `job_id`.
   - This step ensures that the correct journey associated with the candidate and job is identified for further processing.

2. **Temporary Table Creation**:
   - After obtaining `journey_id`, the procedure creates a temporary table named `temp_results` to store intermediate results.
   - This temporary table has columns for `journey_event_id`, `calls_count`, `sms_count`, `emails_count`, and `reschedule_count`.

3. **Populating `temp_results`**:
   - The procedure inserts `journey_event_id` into `temp_results` by selecting from the `journey_events` table where `journey_id` matches the fetched `journey_id` and `is_deleted` is `0`.
   - This step gathers all relevant events associated with the identified journey.

4. **Updating Counts**:
   - The counts of calls, SMS, and emails are updated in `temp_results` using left joins with `calls`, `sms_logs`, and `email_logs` tables respectively.
   - Each join calculates the count of respective interactions (`calls_count`, `sms_count`, `emails_count`) for each `journey_event_id`.

5. **Reschedule Count Update**:
   - The reschedule count in `temp_results` is updated by joining with the `candidate_journey` table.
   - It calculates the number of reschedules (`reschedule_count`) for each `journey_event_id` associated with the fetched `journey_id`.

6. **Final Result Selection**:
   - After updating counts, the procedure selects and returns `journey_event_id`, `calls_count`, `sms_count`, `emails_count`, and `reschedule_count` from `temp_results`.
   - This provides a comprehensive view of interactions and reschedules for the specified candidate and job.

7. **Temporary Table Cleanup**:
   - Finally, the procedure drops the `temp_results` temporary table to clean up resources and ensure no lingering data affects subsequent operations.

This procedure efficiently aggregates interaction and reschedule data, making it suitable for reporting and analytics purposes within the application.

# AddToJobsJobDetails API

## Endpoint

`GET /journey/add-to-jobs-job-details/`

## Description

The `AddToJobsJobDetails` API endpoint retrieves job details associated with a specific candidate. It uses a stored procedure to fetch comprehensive job and candidate-related information based on the provided `candidate_id`. This API provides a detailed view of the jobs that a candidate is linked to, including various attributes related to both the job and the candidate’s interaction with it.

## Request

### Query Parameters

- `candidate_id` (required): The unique ID of the candidate for whom job details are to be fetched.

## Stored Procedure Details

The `AddToJobsJobDetails` API uses the stored procedure `fetch_add_to_jobs_and_job_details` to fetch the relevant job and candidate information.

### Procedure Explanation:

- **Input Handling:**

  The procedure takes a `candidate_id` as input, which is used to filter job records associated with that candidate.

- **Data Retrieval:**

  The procedure retrieves data from the `add_to_jobs` table, which contains records of jobs linked to the candidate.
  It joins this data with the `job_details` table to include detailed job information, such as job titles, descriptions, salaries, and other attributes.

- **Output:**

  The procedure returns a joined result set containing both job and candidate information, filtered by the `candidate_id` and excluding deleted records.


# CampaignTriggersView API

## Endpoint

`GET /journey/campaign_details/`

## Description

The `CampaignTriggersView` API endpoint retrieves campaign trigger details associated with a specific campaign. It utilizes the stored procedure `fetch_campaign_triggers_and_status` to fetch comprehensive trigger and status information based on the provided `campaign_id`. This API provides insights into the triggers and statuses related to the specified campaign.

## Request

### Query Parameters

- `campaign_id` (required): The unique ID of the campaign for which trigger details are to be retrieved.

## Response

### Success Response

- **Status Code:** 200 OK
- **Content-Type:** application/json

**Response Body:**

An array of objects where each object contains the following details:

- `trigger_id`: The unique identifier of the trigger.
- `trigger_name`: The name of the trigger.
- `status`: The display name of the trigger status.
- `timestamp`: The date and time when the trigger was created or last updated.

### Error Responses

- **Status Code:** 400 Bad Request
- **Content-Type:** application/json

**Possible Error Responses:**

- **Missing `campaign_id`:**

  - If the `campaign_id` is not provided in the query parameters, the response will include:
    - `error`: A message indicating that `campaign_id` is required.

- **Internal Server Error:**

  - If there is an issue processing the request, such as an exception being thrown, the response will include:
    - `error`: A message detailing the issue.

## Stored Procedure Details

The `CampaignTriggersView` API uses the stored procedure `fetch_campaign_triggers_and_status` to fetch the relevant trigger and status information.

### Procedure Explanation:

- **Input Handling:**

  The procedure takes a `campaign_id` as input, which is used to filter trigger records associated with that campaign.

- **Data Retrieval:**

  The procedure retrieves data from the `campaign_triggers` table, which contains records of triggers related to the campaign.
  It joins this data with the `candidate_statuses` table to include the display name of the status associated with each trigger.

- **Output:**

  The procedure returns a result set containing both trigger details and the display name of their statuses, filtered by the `campaign_id`.

# CallsByCampaignTriggerView API

## Endpoint

`GET /journey/calls/by-campaign-trigger/`

## Description

The `CallsByCampaignTriggerView` API endpoint retrieves call records associated with a specific campaign trigger. It executes a SQL query to fetch call details based on the provided `campaign_trigger_id`. This API provides information about calls linked to a particular campaign trigger.

## Request

### Query Parameters

- `campaign_trigger_id` (required): The unique ID of the campaign trigger for which call details are to be retrieved.

## Response

### Success Response

- **Status Code:** 200 OK
- **Content-Type:** application/json

**Response Body:**

An array of objects where each object contains details about the call records associated with the specified campaign trigger. Each object includes:

- Various attributes related to the call records.

### Error Responses

- **Status Code:** 400 Bad Request
- **Content-Type:** application/json

**Possible Error Responses:**

- **Missing `campaign_trigger_id`:**

  - If the `campaign_trigger_id` is not provided in the query parameters, the response will include:
    - `error`: A message indicating that `campaign_trigger_id` is required.

- **Internal Server Error:**

  - If there is an issue processing the request, such as an exception being thrown, the response will include:
    - `error`: A message detailing the issue.

## SQL Query Details

The `CallsByCampaignTriggerView` API uses a SQL query to fetch the relevant call records.

### Query Explanation:

- **Input Handling:**

  The query takes a `campaign_trigger_id` as input to filter call records associated with that specific campaign trigger.

- **Data Retrieval:**

  The query retrieves data from the `calls` table, filtering by the `campaign_trigger_id`.

- **Output:**

  The query returns a result set containing call records linked to the specified campaign trigger.

# EmailLogsByCampaignTriggerView API

## Endpoint

`GET /journey/email-logs/by-campaign-trigger/`

## Description

The `EmailLogsByCampaignTriggerView` API endpoint retrieves email log records associated with a specific campaign trigger. It executes a SQL query to fetch email logs based on the provided `campaign_trigger_id`. This API provides information about emails sent or logged in relation to a particular campaign trigger.

## Request

### Query Parameters

- `campaign_trigger_id` (required): The unique ID of the campaign trigger for which email logs are to be retrieved.

## Response

### Success Response

- **Status Code:** 200 OK
- **Content-Type:** application/json

**Response Body:**

An array of objects where each object contains details about the email log records associated with the specified campaign trigger. Each object includes:

- Various attributes related to the email logs.

### Error Responses

- **Status Code:** 400 Bad Request
- **Content-Type:** application/json

**Possible Error Responses:**

- **Missing `campaign_trigger_id`:**

  - If the `campaign_trigger_id` is not provided in the query parameters, the response will include:
    - `error`: A message indicating that `campaign_trigger_id` is required.

- **Internal Server Error:**

  - If there is an issue processing the request, such as an exception being thrown, the response will include:
    - `error`: A message detailing the issue.

## SQL Query Details

The `EmailLogsByCampaignTriggerView` API uses a SQL query to fetch the relevant email log records.

### Query Explanation:

- **Input Handling:**

  The query takes a `campaign_trigger_id` as input to filter email log records associated with that specific campaign trigger.

- **Data Retrieval:**

  The query retrieves data from the `email_logs` table, filtering by the `campaign_trigger_id`.

- **Output:**

  The query returns a result set containing email log records linked to the specified campaign trigger.

# GetAssessmentsByApplicationIdView API

## Endpoint

`GET /journey/assessments/by-applicationid/`

## Description

The `GetAssessmentsByApplicationIdView` API endpoint retrieves assessment records associated with a specific application ID. It filters assessments based on the `application_id` provided in the request's user data. This API provides a list of assessments related to a particular application.

## Request

### Headers

- `UserData`: Contains the `application_id` which is used to filter assessments.

### Response

#### Success Response

- **Status Code:** 200 OK
- **Content-Type:** application/json

**Response Body:**

An array of objects where each object contains:

- `id`: The unique identifier of the assessment.
- `assessment_name`: The name of the assessment.

#### Error Responses

- **Status Code:** 400 Bad Request
- **Content-Type:** application/json

**Possible Error Responses:**

- **Missing `application_id`:**

  - If `application_id` is not present in the request's user data, the response will include:
    - `error`: A message indicating that `application_id` is a required parameter.

- **Status Code:** 404 Not Found
- **Content-Type:** application/json

**Possible Error Responses:**

- **No Assessments Found:**

  - If no assessments are found for the given `application_id`, the response will include:
    - `error`: A message indicating that no assessments were found for the given `application_id`.

- **Status Code:** 500 Internal Server Error
- **Content-Type:** application/json

**Possible Error Responses:**

- **General Error:**

  - If an exception occurs while processing the request, the response will include:
    - `error`: A message detailing the issue.

## Logging

- **Info Logs:**

  - Logs the number of assessments fetched and the `application_id`.

- **Warning Logs:**

  - Logs a warning when no assessments are found for the given `application_id`.

- **Error Logs:**

  - Logs errors if an exception occurs during the request processing.

