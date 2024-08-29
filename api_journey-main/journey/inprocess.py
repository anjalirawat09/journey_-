from django.db.models import Count, F
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count, Q, F
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Journey, JourneyEvents, AddToJobs, CandidateJourney, CandidateDetails, CandidateStatuses, CampaignTriggers,JobDetails,SegmentCategories,BotDetails, Campaigns,CampaignEvent,CampaignChannel,JourneyEventHiringManager,Segments,StepType,SubmitPanel,JourneyEventHiringManager,SubmitClient,Client,JobCandidateHistories,Assessment,InterviewType
from .serializers import JourneySerializer, JourneyEventsSerializer, JobDashboardSerializer, CandidateSerializer,AddToJobsSerializer,JobDetailsSerializer,CandidateJourneySerializer,CampaignEventsSerializer,CampaignTriggersSerializer
from rest_framework import generics
from django.http import JsonResponse
from django.views import View
import logging
from django.http import QueryDict
from django.db.models import Count
from .models import Journey, JourneyEvents, AddToJobs, CandidateJourney, CandidateDetails, CandidateStatuses, CampaignTriggers,JobDetails,SegmentCategories,BotDetails, Campaigns,CampaignEvent,CampaignChannel,JourneyEventHiringManager,Segments,StepType,SubmitPanel,JourneyEventHiringManager,SubmitClient,Client,JobCandidateHistories,Assessment,InterviewType
from .serializers import JourneySerializer, JourneyEventsSerializer, JobDashboardSerializer, CandidateSerializer,AddToJobsSerializer,JobDetailsSerializer,CandidateJourneySerializer,CampaignEventsSerializer,CampaignTriggersSerializer
logger = logging.getLogger('journey')

class JobDashboardView(View):
    def get(self, request, job_id):
        response_data = {}
        
        serializer = JobDashboardSerializer(data={'job_id': job_id, 'status': request.GET.get('status')})
        if not serializer.is_valid():
            logger.warning(f"Validation error: {serializer.errors}")
            return JsonResponse({'error': serializer.errors}, status=400)
        
        job_id = serializer.validated_data['job_id']
        status = serializer.validated_data['status']

        try:
            logger.info(f"Fetching details for job ID: {job_id}")
            journey = JobDetails.objects.get(id=job_id)
            journey_id = journey.journey_id

            logger.info(f"Fetching candidate statuses for status: {status}")
            status_objs = CandidateStatuses.objects.filter(root_name=status)
            status_id_to_display_name = {obj.id: obj.display_name for obj in status_objs}
            status_ids = list(status_id_to_display_name.keys())

            logger.info(f"Fetching journey events for journey ID: {journey_id}")
            
            # Fetch all journey events for the journey
            journey_events = JourneyEvents.objects.filter(journey_id=journey_id, is_deleted=False)

            for journey_event in journey_events:
                journey_event_id = journey_event.id
                interview_type = journey_event.interview_type

                logger.info(f"Fetching status counts for journey event ID: {journey_event_id}")

                # Check if there are any CampaignTriggers for this journey event
                campaign_triggers = CampaignTriggers.objects.filter(
                    journey_event_id=journey_event_id,
                    journey_id=journey_id,
                    job_id=job_id,
                    status_id__in=status_ids
                ).exclude(id=F('parent_id'))  

                event_name = f"{interview_type}"
                response_data[event_name] = {}

                if campaign_triggers.exists():
                    status_counts = campaign_triggers.values('status_id').annotate(count=Count('status_id'))

                    for status_count in status_counts:
                        status_id = status_count['status_id']
                        count = status_count['count']
                        display_name = status_id_to_display_name[status_id]
                        
                        if self.candidate_journey_has_completed(campaign_triggers, status_id):
                            count = 0

                        response_data[event_name][display_name] = {
                            'count': count,
                            'status_id': status_id,
                            'journey_id': journey_id,
                            'journey_event_id': journey_event_id,
                            'job_id': job_id
                        }
                else:
                    response_data[event_name] = {'message': 'Campaign has not started for this journey event'}

            logger.info(f"Successfully fetched data for job ID: {job_id}")
            return JsonResponse(response_data)

        except JobDetails.DoesNotExist:
            logger.warning(f"Job with ID {job_id} not found")
            return JsonResponse({'error': f'Job with ID "{job_id}" not found'}, status=400)
        except JourneyEvents.DoesNotExist:
            logger.warning(f"No journey events found for job ID {job_id}")
            return JsonResponse({'error': f'No journey events found for job ID "{job_id}"'}, status=200)
        except CandidateStatuses.DoesNotExist:
            logger.error("No status IDs found")
            return JsonResponse({'error': 'No status IDs found'}, status=200)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    def candidate_journey_has_completed(self, campaign_triggers, status_id):
        # Helper function to check if any associated CandidateJourney has campaign_status as 'completed' for a given status_id
        triggers = campaign_triggers.filter(status_id=status_id)
        for trigger in triggers:
            candidate_journey = CandidateJourney.objects.get(id=trigger.candidate_journey_id)
            if candidate_journey.campaign_status == 'completed':
                return True
        return False

  
@method_decorator(csrf_exempt, name='dispatch')
class CandidateView(View):
    def post(self, request):
        try:
            data = request.POST 
            
            # If the data is not in POST, convert QueryDict to dict
            if isinstance(data, QueryDict):
                data = data.dict()
                
            serializer = CandidateSerializer(data=data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)

            validated_data = serializer.validated_data
            status_id = validated_data.get('status_id')
            journey_id = validated_data.get('journey_id')
            journey_event_id = validated_data.get('journey_event_id')
            job_id = validated_data.get('job_id')
            
            # Set default values for start_index and end_index
            start_index = validated_data.get('start_index', 0)
            end_index = validated_data.get('end_index', 10)
            
            # Logging and further processing
            logger.info(f"Fetching candidate IDs for status_id: {status_id}, journey_id: {journey_id}, journey_event_id: {journey_event_id}, job_id: {job_id}")
            
            # Fetching candidate IDs and corresponding add_to_job_id matching criteria
            candidate_triggers = CampaignTriggers.objects.filter(
                status_id=status_id,
                journey_id=journey_id,
                journey_event_id=journey_event_id,
                job_id=job_id
            ).values('candidate_id', 'add_to_job_id')

            # Extract candidate_ids and create a dictionary for add_to_job_id
            candidate_ids = [ct['candidate_id'] for ct in candidate_triggers]
            candidate_add_to_job_ids = {ct['candidate_id']: ct['add_to_job_id'] for ct in candidate_triggers}

            # Total count of candidates 
            total_candidates = len(candidate_ids)
            
            # Fetching limited candidate details
            candidates_queryset = CandidateDetails.objects.filter(id__in=candidate_ids).values()[start_index:end_index]
            
            # Prepare response data
            response_data = []
            for candidate in candidates_queryset:
                candidate_id = candidate['id']
                candidate['totalcandidate'] = total_candidates
                candidate['status_id'] = status_id
                candidate['job_id'] = job_id
                candidate['display_name'] = 'Sourced'
                candidate['add_to_job_id'] = candidate_add_to_job_ids.get(candidate_id)
                response_data.append(candidate)

            logger.info(f"Successfully fetched candidate data")
            
            return JsonResponse(response_data, safe=False)
            
        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
            return JsonResponse({'error': ve.detail}, status=400)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
