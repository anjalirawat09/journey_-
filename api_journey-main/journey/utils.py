import logging
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import viewsets, status
from .models import Journey, JourneyEvents, AddToJobs, CandidateJourney, CandidateDetails, CandidateStatuses, CampaignTriggers,JobDetails,SegmentCategories,BotDetails, Campaigns,CampaignEvent,CampaignChannel,JourneyEventHiringManager,Segments,StepType,SubmitPanel,JourneyEventHiringManager,SubmitClient,Client,JobCandidateHistories,Assessment,InterviewType
from .serializers import JourneySerializer, JourneyEventsSerializer, JobDashboardSerializer, CandidateSerializer,AddToJobsSerializer,JobDetailsSerializer,CandidateJourneySerializer,CampaignEventsSerializer,CampaignTriggersSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response

logger = logging.getLogger('journey')

def create_job_candidate_histories(comment, add_to_jobs_entry, event):
    """
    Create an entry in JobCandidateHistories table.
    
    :param comment: Comment to be added
    :param add_to_jobs_entry: The AddToJobs entry being updated
    :param event: The CandidateJourney event associated with the entry
    """
    try:
        JobCandidateHistories.objects.create(
            comment=comment,
            is_interview=0,
            application_id=event.application_id,
            atj_id=add_to_jobs_entry.id,
            candidate_id=event.candidate_id,
            job_id=event.job_id,
            status_id=event.status_id,
            user_id=event.user_id
        )
    except Exception as e:
        logger.error(f"An error occurred while creating job_candidate_histories entry: {str(e)}")


def convert_unit(interval, unit, valid_units):
    if interval and unit:
        if unit in valid_units:
            return valid_units[unit]
        else:
            return Response({"message": "Invalid unit in relative_time_period."}, status=status.HTTP_400_BAD_REQUEST)
    return None

def validate_interview_type_sequence(last_event, current_interview_type):
    if last_event:
        if last_event.interview_type.lower() == 'book calendar' and current_interview_type.lower() != 'interview reminder':
            return {"message": "As the previous event is book calendar, the next event must be interview reminder."}
        elif last_event.interview_type.lower() != 'book calendar' and current_interview_type.lower() == 'interview reminder':
            return {"message": "First create book calendar event, then only you can create interview reminder."}
    else:
        if current_interview_type.lower() == 'interview reminder':
            return {"message": "The first event cannot be interview reminder."}
    return None

def handle_hiring_managers(event, new_hiring_manager_ids, user_id, application_id):
    existing_hiring_manager_records = JourneyEventHiringManager.objects.filter(journey_event=event.id)
    existing_hiring_manager_ids = [record.hiring_manager_id for record in existing_hiring_manager_records if not record.is_deleted]

    for record in existing_hiring_manager_records:
        if record.hiring_manager_id not in new_hiring_manager_ids:
            record.is_deleted = True
            record.save()

    for manager_id in new_hiring_manager_ids:
        if manager_id not in existing_hiring_manager_ids:
            JourneyEventHiringManager.objects.create(
                journey_event=event,
                hiring_manager_id=manager_id,
                user_id=user_id,
                application_id=application_id,
                is_deleted=False
            )


def get_first_event(journey_id, job_id):
    try:
        first_event = JourneyEvents.objects.get(journey_id=journey_id, is_deleted=False, parent_id=0)
        return first_event
    except JourneyEvents.DoesNotExist:
        error_message = f"No JourneyEvents found for job with job_id={job_id} and journey_id={journey_id} and parent_id=0"
        return {"error": error_message}

def calculate_start_time(event):
    if event.immediately:
        return timezone.now()

    interval = event.relative_time_period_interval
    unit = event.relative_time_period_unit

    unit_mapping = {
        'seconds': 'seconds',
        'minutes': 'minutes',
        'hours': 'hours',
        'days': 'days',
        'milliseconds': 'milliseconds',
        'microseconds': 'microseconds',
        'weeks': 'weeks'
    }

    if unit not in unit_mapping:
        raise ValueError(f"Invalid unit for relative_time_period_unit: {unit}")

    timedelta_kwargs = {unit_mapping[unit]: interval}
    return timezone.now() + timezone.timedelta(**timedelta_kwargs)

def handle_interview_type(first_event, candidate_journey, job):
    if first_event.interview_type.lower() == 'submit to panel':
        hiring_manager_ids = JourneyEventHiringManager.objects.filter(journey_event_id=first_event.id).values_list('hiring_manager_id', flat=True)
        SubmitPanel.objects.create(
            candidate_id=job.candidate_id,
            journey_id=first_event.journey_id,
            journey_event_id=first_event.id,
            candidate_journey_id=candidate_journey.id,
            hiring_manager_ids=list(hiring_manager_ids)
        )
    elif first_event.interview_type.lower() == 'submit to client':
        SubmitClient.objects.create(
            candidate_id=job.candidate_id,
            journey_id=first_event.journey_id,
            journey_event_id=first_event.id,
            candidate_journey_id=candidate_journey.id,
            client_id=first_event.client_id
        )
def update_add_to_jobs_status(event, status, comment):
    try:
        add_to_jobs_entry = AddToJobs.objects.get(id=event.add_to_job_id)
        add_to_jobs_entry.journey_status = status
        add_to_jobs_entry.status_id = event.status_id
        add_to_jobs_entry.save()

        create_job_candidate_histories(
            comment=comment,
            add_to_jobs_entry=add_to_jobs_entry,
            event=event
        )
        return True
    except AddToJobs.DoesNotExist:
        logger.error(f"No AddToJobs entry found for id {event.add_to_job_id}")
    except Exception as e:
        logger.error(f"An error occurred while updating AddToJobs: {str(e)}")
    return False

def process_completed_campaign(event):
    try:
        status_id = event.status_id
        candidate_status = CandidateStatuses.objects.get(id=status_id)

        if candidate_status.root_name.lower() == 'rejected':
            return update_add_to_jobs_status(event, 'completed', 
                'Status updated to completed from candidate journey as it is rejected')

        current_event = JourneyEvents.objects.get(id=event.journey_event_id, journey_id=event.journey_id)

        if event.qualifying_criteria >= current_event.qualifying_criteria:
            next_event = JourneyEvents.objects.filter(
                journey_id=event.journey_id, 
                parent_id=current_event.parent_id + 1, 
                is_deleted=False
            ).first()

            if next_event:
                if event.is_next_event_added == 0:
                    candidate_journey = CandidateJourney.objects.create(
                        journey_id=next_event.journey_id,
                        journey_event_id=next_event.id,
                        add_to_job_id=event.add_to_job_id,
                        campaign_id=next_event.campaign_id,
                        bot_id=next_event.bot_id,
                        user_id=event.user_id,
                        application_id=event.application_id,
                        job_id=event.job_id,
                        status_id=event.status_id,
                        candidate_id=event.candidate_id,
                        campaign_status=0
                    )
                    logger.info(f"Entries created successfully in candidate_journey for journey_id '{next_event.journey_id}' and journey_event_id '{next_event.id}'")

                    if next_event.interview_type.lower() == 'submit to panel':
                        submit_to_panel(next_event, candidate_journey, event.candidate_id)
                    elif next_event.interview_type.lower() == 'submit to client':
                        submit_to_client(next_event, candidate_journey, event.candidate_id)

                    event.is_next_event_added = 1
                    event.save()

                    return update_add_to_jobs_status(event, 'completed', 
                        'Status updated to completed from candidate journey for the next event')
                else:
                    logger.error(f"Next event already added for event id {event.id}")
            else:
                return update_add_to_jobs_status(event, 'completed', 
                    'Status updated to completed as no next event found from candidate journey')
        else:
            return update_add_to_jobs_status(event, 'rejected', 
                'Status updated to rejected from candidate journey due to less qualifying criteria')
    except JourneyEvents.DoesNotExist:
        logger.error(f"No JourneyEvents found for journey_id {event.journey_id} and parent_id {event.journey_event_id}")
    except CandidateStatuses.DoesNotExist:
        logger.error(f"No CandidateStatuses entry found for status_id {status_id}")
    except Exception as e:
        logger.error(f"An error occurred while processing completed campaigns: {str(e)}")
    return False

def submit_to_panel(next_event, candidate_journey, candidate_id):
    hiring_manager_ids = JourneyEventHiringManager.objects.filter(journey_event_id=next_event.id).values_list('hiring_manager_id', flat=True)
    SubmitPanel.objects.create(
        candidate_id=candidate_id,
        journey_id=next_event.journey_id,
        journey_event_id=next_event.id,
        candidate_journey_id=candidate_journey.id,
        hiring_manager_ids=list(hiring_manager_ids)
    )
    logger.info(f"Entries created in submit panel for journey id '{next_event.journey_id}' and journey_event_id '{next_event.id}'")

def submit_to_client(next_event, candidate_journey, candidate_id):
    SubmitClient.objects.create(
        candidate_id=candidate_id,
        journey_id=next_event.journey_id,
        journey_event_id=next_event.id,
        candidate_journey_id=candidate_journey.id,
        client_id=next_event.client_id
    )
    logger.info(f"Entries created in submit client for journey id '{next_event.journey_id}' and journey_event_id '{next_event.id}'")

def process_cancelled_campaign(event):
    return update_add_to_jobs_status(event, 'cancelled', 'Status updated to cancelled from candidate journey')
