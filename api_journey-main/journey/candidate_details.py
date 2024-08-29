from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count, Q, F
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from .models import Journey, JourneyEvents, AddToJobs, CandidateJourney, CandidateDetails, CandidateStatuses, CampaignTriggers,JobDetails,SegmentCategories,BotDetails, Campaigns,CampaignEvent,CampaignChannel,JourneyEventHiringManager,Segments,StepType,SubmitPanel,JourneyEventHiringManager,SubmitClient,Client,JobCandidateHistories,Assessment,InterviewType
from .serializers import JourneySerializer, JourneyEventsSerializer, JobDashboardSerializer, CandidateSerializer,AddToJobsSerializer,JobDetailsSerializer,CandidateJourneySerializer,CampaignEventsSerializer,CampaignTriggersSerializer
from rest_framework import generics
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
import logging, re
from django.views import View
import json
from django.db import connection
from rest_framework import  status
from rest_framework.response import Response

class JobDataView(APIView):
    def get(self, request, candidate_id, job_id):
        try:
            # Querying add_to_jobs table based on candidate_id and job_id
            add_to_jobs_data = AddToJobs.objects.filter(candidate_id=candidate_id, job_id=job_id, is_deleted=False)

            if not add_to_jobs_data.exists():
                return Response({'error': 'Data not found for given candidate_id and job_id'}, status=status.HTTP_200_OK)

            job_data = []
 
            for add_to_job in add_to_jobs_data:
                # Querying job_details table based on job_id from add_to_jobs_data
                job_details_data = JobDetails.objects.filter(id=add_to_job.job_id, is_deleted=False).first()

                if not job_details_data:
                    return Response({'error': 'Job details not found for the given job_id'}, status=status.HTTP_200_OK)

                # Serialize data using respective serializers
                add_to_jobs_serializer = AddToJobsSerializer(add_to_job)
                job_details_serializer = JobDetailsSerializer(job_details_data)

                # Combine serialized data
                combined_data = {
                    'add_to_jobs_data': add_to_jobs_serializer.data,
                    'job_details_data': job_details_serializer.data,
                }
               
                job_data.append(combined_data)

            return Response(job_data,status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                  
            
class JourneyDetailsView(APIView):
    def get(self, request, candidate_id, job_id):
        try:
            # Querying add_to_jobs table based on candidate_id and job_id
            add_to_jobs_data = AddToJobs.objects.filter(candidate_id=candidate_id, job_id=job_id, is_deleted=False).first()

            if not add_to_jobs_data:
                return Response({'error': 'Data not found for given candidate_id and job_id'}, status=status.HTTP_200_OK)

            # Fetching journey_id from add_to_jobs_data
            journey_id = add_to_jobs_data.journey_id

            # Querying journey table based on journey_id
            journey_data = Journey.objects.filter(id=journey_id, is_deleted=False).first()

            if not journey_data:
                return Response({'error': 'Journey details not found for the given journey_id'}, status=status.HTTP_200_OK)

            # Counting distinct journey_events based on journey_id
            events_count = JourneyEvents.objects.filter(journey_id=journey_id).count()

            # Serialize data using respective serializers
            journey_serializer = JourneySerializer(journey_data)

            # Create response data including events_count
            journey_details = {
                **journey_serializer.data,  # Add journey details
                'events_count': events_count  # Add events count
            }

            return Response({'journey_details': journey_details},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CandidateJourneyDetailsView(APIView):
    def get(self, request, candidate_id, job_id):
        try:
            # Querying candidate_journey table based on candidate_id, job_id, and is_deleted
            candidate_journey_queryset = CandidateJourney.objects.filter(candidate_id=candidate_id, job_id=job_id)

            if not candidate_journey_queryset.exists():
                return Response({'error': 'Data not found for given candidate_id and job_id'}, status=status.HTTP_200_OK)

            # Serialize candidate journey data
            candidate_journey_serializer = CandidateJourneySerializer(candidate_journey_queryset, many=True)
            candidate_journey_data = candidate_journey_serializer.data

            # Initialize counters
            completed_events = {}
            in_process_events = {}
            event_reschedule_counts = {}
            processed_events = set()

            # Iterate through candidate journey data to get journey_event details and calculate counts
            for candidate_journey in candidate_journey_data:
                journey_id = candidate_journey['journey']
                journey_event_id = candidate_journey['journey_event']
                campaign_status = candidate_journey['campaign_status']

                # Count the reschedules
                if journey_event_id in event_reschedule_counts:
                    event_reschedule_counts[journey_event_id] += 1
                else:
                    event_reschedule_counts[journey_event_id] = 1

                # Query journey_events table based on journey_id and journey_event_id
                journey_events_queryset = JourneyEvents.objects.filter(journey_id=journey_id, id=journey_event_id, is_deleted=False)
                journey_events_serializer = JourneyEventsSerializer(journey_events_queryset, many=True)
                journey_events_data = journey_events_serializer.data

                # Add journey_events details to candidate_journey data
                candidate_journey['journey_events_details'] = journey_events_data

                # Update completed and in-process counts
                if (journey_event_id, campaign_status) not in processed_events:
                    processed_events.add((journey_event_id, campaign_status))
                    if campaign_status == 'completed':
                        if journey_event_id in completed_events:
                            completed_events[journey_event_id] += 1
                        else:
                            completed_events[journey_event_id] = 1
                    elif campaign_status == 'inprocess':
                        if journey_event_id in in_process_events:
                            in_process_events[journey_event_id] += 1
                        else:
                            in_process_events[journey_event_id] = 1

            # Calculate final reschedule counts
            for candidate_journey in candidate_journey_data:
                journey_event_id = candidate_journey['journey_event']
                candidate_journey['reschedule_count'] = event_reschedule_counts[journey_event_id] - 1

            # Prepare response data
            response_data = {
                'candidate_journey_details': candidate_journey_data,
                'completed_events': [{'count': count, 'id': event_id} for event_id, count in completed_events.items()],
                'in_process_events': [{'count': count, 'id': event_id} for event_id, count in in_process_events.items()]
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CampaignDataView(APIView):
    def get(self, request, candidate_journey_id):
        try:
            # Querying CampaignTriggers table based on candidate_journey_id
            campaign_triggers = CampaignTriggers.objects.filter(candidate_journey_id=candidate_journey_id)

            if not campaign_triggers.exists():
                return Response({'error': 'Data not found for given candidate_journey_id'}, status=status.HTTP_200_OK)

            campaign_data = []
            for trigger in campaign_triggers:
                # Serializing the CampaignTriggers data
                trigger_serializer = CampaignTriggersSerializer(trigger)

                # Querying CampaignEvents table based on event_id from CampaignTriggers
                campaign_event = CampaignEvent.objects.filter(id=trigger.event_id).first()

                if campaign_event:
                    # Serializing the CampaignEvents data
                    event_serializer = CampaignEventsSerializer(campaign_event)

                    # Combining serialized data
                    combined_data = {
                        'campaign_trigger_data': trigger_serializer.data,
                        'campaign_event_data': event_serializer.data
                    }
                else:
                    combined_data = trigger_serializer.data

                campaign_data.append(combined_data)

            return Response(campaign_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class JourneyEventDetails(APIView):
    def get(self, request, candidate_id, job_id):
        # Filter candidate_journey based on candidate_id and job_id
        candidate_journeys = CandidateJourney.objects.filter(candidate_id=candidate_id, job_id=job_id)

        if not candidate_journeys:
            return Response(f"message: No journey is started for this candidate with candidate_id:{candidate_id} and job_id:{job_id}")

        # Initialize response data
        response_data = []
        completed_events = 0
        in_process_events = 0

        # Iterate through each matching row of candidate_journey
        for candidate_journey in candidate_journeys:
            journey_event = JourneyEvents.objects.get(id=candidate_journey.journey_event_id)
            
            # Prepare event details
            event_details = {
                'step_started_time': candidate_journey.created_at,
                'step_ended': candidate_journey.updated_at if candidate_journey.campaign_status == 'completed' else None,
                'status': 'completed' if candidate_journey.campaign_status == 'completed' else 'in process' if candidate_journey.campaign_status == 'in process' else 'pending',
                'result': 'pass' if candidate_journey.qualifying_criteria >= journey_event.qualifying_criteria else 'fail',
                'rating': (candidate_journey.qualifying_criteria / 5) * 100,
            }

            # Increment counters based on campaign_status
            if candidate_journey.campaign_status == 'completed':
                completed_events += 1
            elif candidate_journey.campaign_status == 'in process':
                in_process_events += 1

            # Serialize journey_event data
            serialized_event = JourneyEventsSerializer(journey_event).data
            event_details.update(serialized_event)

            # Calculate reschedule count
            reschedule_count = CandidateJourney.objects.filter(journey_id=journey_event.journey_id, journey_event_id=journey_event.id).count()
            event_details['reschedule_count'] = reschedule_count-1

            response_data.append(event_details)

        # Determine current step
        first_journey_id = candidate_journeys.first().journey_id
        total_steps = JourneyEvents.objects.filter(journey_id=first_journey_id).count()

        current_step = completed_events + 1 if completed_events < total_steps else total_steps

        # Add global event information
        global_info = {
            'completed_events': completed_events,
            'in_process_events': in_process_events,
            'current_step': current_step,
            'total_steps': total_steps
        }

        # Include JourneyEvents not associated with any CandidateJourney
        journey_events_not_in_candidate_journey = JourneyEvents.objects.filter(journey_id=first_journey_id).exclude(id__in=candidate_journeys.values_list('journey_event_id', flat=True))

        for journey_event in journey_events_not_in_candidate_journey:
            event_details = {
                'step_started_time': None,
                'step_ended': None,
                'status': 'pending',
                'result': None,
                'rating': None,
                'reschedule_count': None
            }

            serialized_event = JourneyEventsSerializer(journey_event).data
            event_details.update(serialized_event)
            response_data.append(event_details)

        return Response({'events': response_data, 'global_info': global_info}, status=status.HTTP_200_OK)



class CandidateCallsEmailsSms(View):
    def get(self, request, candidate_id, job_id, *args, **kwargs):
        response_data = []

        with connection.cursor() as cursor:
            # Call the stored procedure
            cursor.callproc('smsemailcallfrequency', [candidate_id, job_id])
            results = cursor.fetchall()

            # Fetch the interview_type for each journey_event_id
            journey_event_ids = [row[0] for row in results]
            if journey_event_ids:
                cursor.execute(
                    "SELECT id, interview_type FROM journey_events WHERE id IN %s",
                    [tuple(journey_event_ids)]
                )
                interview_types = {row[0]: row[1] for row in cursor.fetchall()}

            for row in results:
                journey_event_id, calls_count, sms_count, emails_count, reschedule_count = row
                response_data.append({
                    'id': journey_event_id,
                    'calls': calls_count,
                    'sms': sms_count,
                    'emails': emails_count,
                    'reschedule': reschedule_count,
                    'step_type': interview_types.get(journey_event_id)
                })

        return JsonResponse(response_data, safe=False)


class AddToJobsJobDetails(View):
    def get(self, request, *args, **kwargs):
        try:
            candidate_id = request.GET.get('candidate_id')
            if not candidate_id:
                return JsonResponse({'error': 'candidate_id is required'}, status=status.HTTP_200_OK)

            response_data = []

            with connection.cursor() as cursor:
                # Call the stored procedure
                cursor.callproc('fetch_add_to_jobs_and_job_details', [candidate_id])
                results = cursor.fetchall()

                # Get column names
                columns = [desc[0] for desc in cursor.description]

                # Process the results
                for row in results:
                    # Create dictionary for each row
                    row_dict = dict(zip(columns, row))
                    # Adjust the response to separate add_to_jobs_id
                    response_data.append({
                        'add_to_jobs_id': row_dict['add_to_jobs_id'],
                        **{key: row_dict[key] for key in columns if key != 'add_to_jobs_id'}
                    })

            return JsonResponse(response_data, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

class CampaignTriggersView(View):
    def get(self, request, *args, **kwargs):
        try:
            
            campaign_id = request.GET.get('campaign_id')

            if not campaign_id:
                return JsonResponse({'error': 'campaign_id is required'}, status=status.HTTP_200_OK)

            response_data = []

            with connection.cursor() as cursor:
                # Call the stored procedure
                cursor.callproc('fetch_campaign_triggers_and_status', [campaign_id])
                results = cursor.fetchall()  

                # Get the column names from the cursor
                columns = [col[0] for col in cursor.description]

                # Process the results
                for row in results:
                    row_dict = dict(zip(columns, row))
                    response_data.append(row_dict)

            return JsonResponse(response_data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CallsByCampaignTriggerView(View):
    def get(self, request, *args, **kwargs):
        campaign_trigger_id = request.GET.get('campaign_trigger_id')
        if not campaign_trigger_id:
            return JsonResponse({'error': 'campaign_trigger_id is required'}, status=status.HTTP_200_OK)

        try:
            response_data = []

            with connection.cursor() as cursor:
                # Query to fetch calls based on campaign_trigger_id
                query = """
                    SELECT *
                    FROM calls
                    WHERE campaign_trigger_id = %s
                """
                cursor.execute(query, [campaign_trigger_id])
                results = cursor.fetchall()

                # Get the column names from the cursor
                columns = [col[0] for col in cursor.description]

                # Process the results
                for row in results:
                    row_dict = dict(zip(columns, row))
                    response_data.append(row_dict)

            return JsonResponse(response_data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class EmailLogsByCampaignTriggerView(View):
    def get(self, request, *args, **kwargs):
        try:
            campaign_trigger_id = request.GET.get('campaign_trigger_id')
            if not campaign_trigger_id:
                return JsonResponse({'error': 'campaign_trigger_id is required'}, status=status.HTTP_200_OK)

            response_data = []

            with connection.cursor() as cursor:
                # Query to fetch email logs based on campaign_trigger_id
                query = """
                    SELECT *
                    FROM email_logs
                    WHERE campaign_trigger_id = %s
                """
                cursor.execute(query, [campaign_trigger_id])
                results = cursor.fetchall()

                # Get the column names from the cursor
                columns = [col[0] for col in cursor.description]

                # Process the results
                for row in results:
                    row_dict = dict(zip(columns, row))
                    response_data.append(row_dict)

            return JsonResponse(response_data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

