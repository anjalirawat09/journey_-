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
from datetime import datetime, timedelta
from django.conf import settings
from django.http import QueryDict
from django.db.models import Count
import json
from .mendate_model import User
from django.core.paginator import Paginator
from django.db.models import Max
from .mendate_model import User, Application
from django.db import connection
from rest_framework import serializers, status
from rest_framework.response import Response
from .utils import convert_unit, validate_interview_type_sequence, handle_hiring_managers,create_job_candidate_histories,get_first_event, calculate_start_time, handle_interview_type,process_completed_campaign, process_cancelled_campaign


logger = logging.getLogger('journey')



class JourneyAPIView(APIView):

    def get(self, request, **kwargs):
        journey_id = kwargs.get('journey_id')
        if journey_id is not None:
            return Response({"message": "journey_id should not be provided for GET request."}, status=status.HTTP_400_BAD_REQUEST)
        
        start_index = int(request.query_params.get('start_index', 0))
        end_index = int(request.query_params.get('end_index', 10))

        try:
            # Get the total count of journeys where is_deleted=False
            total_count = Journey.objects.filter(is_deleted=False).count()
   
            # Query for journeys where is_deleted=False, in reverse order by id
            max_id = Journey.objects.filter(is_deleted=False).aggregate(max_id=Max('id'))['max_id']
            if max_id is not None:
                reverse_journeys = Journey.objects.filter(is_deleted=False, id__lte=max_id).order_by('-id')[start_index:end_index + 1]
            else:
                reverse_journeys = []

            paginator = Paginator(reverse_journeys, end_index - start_index)

            page_number = (start_index // (end_index - start_index)) + 1
            page_obj = paginator.get_page(page_number)

            serializer = JourneySerializer(page_obj, many=True)

            logger.info("Journeys retrieved successfully.")
            return Response({"total_count": total_count, "journeys": serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request, **kwargs):
        
        journey_id = kwargs.get('journey_id')
        if journey_id is not None:
            return Response({"message": "journey_id should not be provided for POST request."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer = JourneySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info("Journeys created successfully.")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.warning("Invalid data provided for journey creation.")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:  
            logger.error(f"An error occurred: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def put(self, request, **kwargs):
        if 'journey_id' not in kwargs:
            return Response({"message": "journey_id should be provided for PUT request."}, status=status.HTTP_400_BAD_REQUEST)

        journey_id = kwargs['journey_id']
        try:
            journey = Journey.objects.get(id=journey_id)
        except Journey.DoesNotExist:
            logger.warning(f"Journey with id {journey_id} not found.")
            return Response({'error': 'Journey not found'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred while retrieving the journey: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            
            serializer = JourneySerializer(journey, data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Journey with id {journey_id} updated successfully.")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                logger.warning("Invalid data provided for journey update.")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An error occurred while updating the journey: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, **kwargs):
        if 'journey_id' not in kwargs:
            return Response({"message": "journey_id should be provided for DELETE request."}, status=status.HTTP_400_BAD_REQUEST)

        journey_id = kwargs['journey_id']
        try:
            journey = Journey.objects.get(id=journey_id, is_deleted=False)
            journey.is_deleted = True
            journey.save()
            logger.info(f"Journey with id {journey_id} deleted successfully.")
            return Response('Data soft deleted',status=status.HTTP_200_OK)
        except Journey.DoesNotExist:
            logger.warning(f"Journey with id {journey_id} not found or already deleted.")
            return Response({'error': 'Journey not found or already deleted'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class JourneyShowAPIView(APIView):    

    def get(self, request, **kwargs):
        if 'journey_id' not in kwargs:
            return Response({"message": "journey_id should be provided for GET request."}, status=status.HTTP_400_BAD_REQUEST)

        journey_id = kwargs['journey_id']
        try:
            journey = Journey.objects.get(pk=journey_id, is_deleted=False)
            serializer = JourneySerializer(journey)
            
            response_data = {
                'name': serializer.data['name'],
                'description': serializer.data['description'],
                'segment': serializer.data['segment'],
                'allow_contacts_to_restart': serializer.data['allow_contacts_to_restart'],
                'published': serializer.data['published'],
                'user':serializer.data['user'],
                'application':serializer.data['application'],
                'is_deleted':serializer.data['is_deleted']
            }
            logger.info(f"Journey with id {journey_id} showed successfully.")
            return Response(response_data, status=status.HTTP_200_OK)
        except Journey.DoesNotExist:
            logger.warning(f"Journey with id {journey_id} not found or deleted.")
            return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class JourneyEventsListAPIView(APIView):

    def get(self, request, **kwargs):

        if 'journey_id' not in kwargs:
            return Response({"message": "journey_id should be provided for getting event details for particular journeyid."}, status=status.HTTP_200_OK)

        journey_id = kwargs['journey_id']

        try:
            # data = JourneyEvents.objects.filter(journey_id=journey_id)
            data = JourneyEvents.objects.filter(journey_id=journey_id).order_by('id')
            if not data.exists():
                logger.warning(f"No journey events found for journey_id {journey_id}.")
                return Response([], status=status.HTTP_200_OK)


            serializer = JourneyEventsSerializer(data, many=True)
            logger.info(f"Journey events with  journey id {journey_id} retrieved successfully.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self, request, **kwargs):
        journey_id = kwargs.get('id')
        if journey_id is not None:
            return Response({"message": "journey_id should not be provided for POST request."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = request.data.copy()
            application_id = request.UserData.application_id
            user_id = request.UserData.id
            data['application'] = application_id
            data['user'] = user_id

            valid_units = {'h': 'hours', 'm': 'minutes', 's': 'seconds', 'ms': 'milliseconds', 'us': 'microseconds', 'd': 'days', 'w': 'weeks'}
            data['relative_time_period_unit'] = convert_unit(data.get('relative_time_period_interval'), data.get('relative_time_period_unit'), valid_units)
            data['close_link_within_unit'] = convert_unit(data.get('close_link_within_interval'), data.get('close_link_within_unit'), valid_units)

            # Retrieve interview type name using interview_type_id
            step_id = data.get('step')
            if step_id:
                interview_type = InterviewType.objects.filter(id=step_id).first()
                if interview_type:
                    data['interview_type'] = interview_type.root_name
                else:
                    return Response({"message": "Invalid interview_type_id provided."}, status=status.HTTP_400_BAD_REQUEST)
            # Validating interview_type sequence
            journey_id=data.get('journey')
            last_event = JourneyEvents.objects.filter(journey_id=journey_id,is_deleted=False).order_by('-id').first()
            sequence_error = validate_interview_type_sequence(last_event, data.get('interview_type'))
            if sequence_error:
                return Response(sequence_error, status=status.HTTP_400_BAD_REQUEST)
            
             
            # Setting parent_id based on existing events
            existing_events = JourneyEvents.objects.filter(journey_id=data.get('journey'))
            data['parent_id'] = (existing_events.order_by('-parent_id').first().parent_id + 1) if existing_events.exists() else 0

            event_data = JourneyEventsSerializer(data=data)
            if event_data.is_valid():
                event = event_data.save()
                logger.info("Journey event is posted successfully with managers.")
                return Response(event_data.data, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Invalid data provided: {event_data.errors}")
                return Response(event_data.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):  
        if 'id' not in kwargs:
            return Response({"message": "event_id should be provided for PUT request."}, status=status.HTTP_400_BAD_REQUEST)

        event_id = kwargs['id']
        try:
            event = JourneyEvents.objects.get(id=event_id)
        except JourneyEvents.DoesNotExist:
            logger.warning(f"Journey event with ID {event_id} not found.")
            return Response({'error': f'Journey event with ID {event_id} not found'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred while retrieving the journey event: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            data = request.data.copy()
            valid_units = {'h': 'hours', 'm': 'minutes', 's': 'seconds', 'ms': 'milliseconds', 'us': 'microseconds', 'd': 'days', 'w': 'weeks'}

            data['relative_time_period_unit'] = convert_unit(data.get('relative_time_period_interval'), data.get('relative_time_period_unit'), valid_units)
            data['close_link_within_unit'] = convert_unit(data.get('close_link_within_interval'), data.get('close_link_within_unit'), valid_units)

            # Retrieve interview type name using interview_type_id
            step_id = data.get('step')
            if step_id:
                interview_type = InterviewType.objects.filter(id=step_id).first()
                if interview_type:
                    data['interview_type'] = interview_type.root_name
                else:
                    return Response({"message": "Invalid interview_type_id provided."}, status=status.HTTP_400_BAD_REQUEST)

            current_interview_type = data.get('interview_type')
            if current_interview_type and current_interview_type != event.interview_type:
                last_event = JourneyEvents.objects.filter(journey_id=event.journey_id, is_deleted=False).order_by('-id').first()
                sequence_error = validate_interview_type_sequence(last_event, current_interview_type)
                if sequence_error:
                    return Response(sequence_error, status=status.HTTP_400_BAD_REQUEST)
                
            # Ensure 'application' and 'user' keys are present
            if 'application' not in data:
                data['application'] = event.application_id
            if 'user' not in data:
                data['user'] = event.user_id

            handle_hiring_managers(event, data.get('hiring_manager_ids', []), data['user'], data['application'])

            serializer = JourneyEventsSerializer(event, data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Journey event with id {event_id} updated successfully.")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Invalid data provided for journey event update: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An error occurred while updating the journey event: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def delete(self, request, **kwargs):
        if 'id' not in kwargs:
            return Response({"message": "event_id should be provided for DELETE request."}, status=status.HTTP_400_BAD_REQUEST)

        event_id = kwargs['id']
        try:
            event = JourneyEvents.objects.get(id=event_id)
        except JourneyEvents.DoesNotExist:
            logger.warning(f"Journey event with ID {event_id} not found.")
            return Response({'error': f'Journey event with ID {event_id} not found'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred while retrieving the journey event: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            event.is_deleted = True
            event.save()

            related_hiring_managers = JourneyEventHiringManager.objects.filter(journey_event=event_id, is_deleted=False)
            for record in related_hiring_managers:
                record.is_deleted = True
                record.save()

            

            logger.info("Journey event is deleted successfully.")
            return Response({"message": "Journey event deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShowjourneyeventsListAPIView(APIView):  
    
    def get(self, request, **kwargs):
        if 'event_id' not in kwargs:
            return Response({"message": "event_id should be provided for getting event details for particular event."}, status=status.HTTP_200_OK)

        event_id = kwargs['event_id']
        
        try:
            data = JourneyEvents.objects.filter(id=event_id, is_deleted=False)
            if not data.exists():
                logger.warning(f"No journey events found for the given event_id {event_id}.")
                return Response([], status=status.HTTP_200_OK)

            serializer = JourneyEventsSerializer(data, many=True)
            logger.info(f"Journey events with id {event_id} showed successfully.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddJobAPIView(APIView):
    def get(self, request):
        try:
            successful_ids = []
            error_ids = {}

            # Retrieve jobs that need to be added and whose journey is not updated and no errors occurred
            jobs_to_add = AddToJobs.objects.filter(journey_update=False, error_occurred=False)

            if not jobs_to_add.exists():
                # Log an info and return a response if no jobs are found
                logger.info("No jobs to add whose journey is not updated in AddToJobs.")
                return Response({"message": "No jobs to add whose journey is not updated in AddToJobs."})

            # Iterate through each job to process
            for job in jobs_to_add:
                try:
                    first_event = get_first_event(job.journey_id, job.id)

                    if 'error' in first_event:
                        logger.error(first_event['error'])
                        error_ids[job.id] = first_event['error']
                        job.error_occurred = True
                        job.journey_update = True
                        job.save()
                        continue
                    
                    start_time = calculate_start_time(first_event)
            
                    # Add the first event in Candidate Journey if their journey is not updated
                    candidate_journey = CandidateJourney.objects.create(
                        job_id=job.job_id,
                        candidate_id=job.candidate_id,
                        application_id=job.application_id,
                        user_id=job.user_id,
                        journey_id=job.journey_id,
                        start_time=start_time,
                        journey_event_id=first_event.id,
                        bot_id=first_event.bot_id,
                        status_id=job.status_id,
                        add_to_job_id=job.id,
                        campaign_id=first_event.campaign_id,
                        campaign_status=0
                    )

                    handle_interview_type(first_event, candidate_journey, job)

                    # Update the job to indicate the journey has been updated
                    job.journey_update = True
                    job.journey_status= 'candidate in journey'
                    job.save()  

                    
                    # Log successful processing
                    logger.info(f"Job successfully added to CandidateJourney: job_id={job.job_id}, candidate_id={job.candidate_id}, journey_id={job.journey_id}")
                    successful_ids.append({"id": job.id, "message": "Successfully added to CandidateJourney"})

                except Exception as e:
                    error_message = f"Error processing job with job_id={job.id}, journey_id={job.journey_id}: {str(e)}"
                    logger.error(error_message)
                    error_ids[job.id] = error_message
                    job.error_occurred = True # Mark the job as having an error
                    job.journey_update=True  
                    job.save()
                    continue

            # Prepare response with successful and error job IDs
            response_data = {
                "successful_ids": successful_ids,
                "error_ids": error_ids
            }

            logger.info("Jobs added to CandidateJourney successfully.")
            return Response(response_data)


        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CandidateNextEventAdditionAPIView(APIView):

    def get(self, request):
        try:
            events_processed = False  

            completed_campaigns_event = CandidateJourney.objects.filter(campaign_status__iexact='completed')
            if completed_campaigns_event.exists():
                for event in completed_campaigns_event:
                    if process_completed_campaign(event):
                        events_processed = True

            cancelled_campaigns_event = CandidateJourney.objects.filter(campaign_status__iexact='cancelled')
            if cancelled_campaigns_event.exists():
                for event in cancelled_campaigns_event:
                    if process_cancelled_campaign(event):
                        events_processed = True

            if events_processed:
                return JsonResponse({"message": "Next events added to CandidateJourney Successfully and journey status updated in AddToJobs."}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"message": "No events processed."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({"message": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetSegmentCategoriesView(View):
    def get(self, request, journey_id):
        try:
            # Filter the journey by journey_id and get the segment_id  
            journey = Journey.objects.get(id=journey_id)
            segment_id = journey.segment_id

            # Filter SegmentCategories by segment_id
            categories = SegmentCategories.objects.filter(segment_id=segment_id)
            
            # Prepare the response data
            data = []
            for category in categories:
                data.append({
                    'id': category.id,
                    'category_name': category.category_name,
                })
            
            logger.info(f"Retrieved {len(data)} segment categories for journey_id {journey_id}.")
            return JsonResponse(data, safe=False, status=200)
        except Journey.DoesNotExist:
            logger.warning(f"Journey with id {journey_id} not found.")
            return JsonResponse([], status=200)
        except Exception as e:
            logger.error(f"An error occurred while retrieving segment categories for journey_id {journey_id}: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
        
        
        
class GetBotsBySegmentCategoryView(View):
    def get(self, request, segment_category_id):
        try:
            # Get segment_id from SegmentCategories
            segment_category = SegmentCategories.objects.get(id=segment_category_id)
            segment_id = segment_category.segment_id

            # Filter BotDetails by segment_id and segment_category_id
            bots = BotDetails.objects.filter(segment_id=segment_id, segment_category_id=segment_category_id)

            bot_data = [{'id': bot.id, 'bot_name': bot.bot_name} for bot in bots]

            bot_data = [{'bot_id': bot.id, 'bot_name': bot.bot_name} for bot in bots]


            logger.info(f"Retrieved {len(bot_data)} bots for segment_category_id {segment_category_id}.")
            return JsonResponse(bot_data, safe= False, status=200)
        except SegmentCategories.DoesNotExist:
            logger.warning(f"Segment category with id {segment_category_id} not found.")
            return JsonResponse({'error': 'Segment category not found'}, status=404)
        except Exception as e:
            logger.error(f"An error occurred while retrieving bots for segment_category_id {segment_category_id}: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

        
class GetCampaignsBySegmentCategoryView(View):
    def get(self, request, segment_category_id):
        try:
            # Get segment_id from SegmentCategories
            segment_category = SegmentCategories.objects.get(id=segment_category_id)
            segment_id = segment_category.segment_id

            # Filter Campaigns by segment_id and segment_category_id
            campaigns = Campaigns.objects.filter(segment_id=segment_id, segment_category_id=segment_category_id)
            campaign_data = [{'id': campaign.id, 'campaign_name': campaign.campaign_name} for campaign in campaigns]
            
            logger.info(f"Retrieved {len(campaign_data)} campaigns for segment_category_id {segment_category_id}.")
            return JsonResponse(campaign_data, safe=False, status=200)
        except SegmentCategories.DoesNotExist:
            logger.warning(f"Segment category with id {segment_category_id} not found.")
            return JsonResponse({'error': 'Segment category not found'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred while retrieving campaigns for segment_category_id {segment_category_id}: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

class CheckCampaignInterview(View):
    def get(self, request, campaign_id):
        try:
            interview_type = request.GET.get('interview_type')

            if not campaign_id or not interview_type:
                logger.error("Missing campaign_id or interview_type parameters")
                return JsonResponse({'error': 'campaign_id and interview_type are required parameters.'}, status=status.HTTP_200_OK)

            # Fetching channel_ids from CampaignEvents table
            campaign_events = CampaignEvent.objects.filter(campaign_id=campaign_id)
            channel_ids = campaign_events.values_list('channel_id', flat=True)

            # Fetching channels from CampaignChannels table
            campaign_channels = CampaignChannel.objects.filter(id__in=channel_ids)

            found_interview = False
            found_call = False

            # Iterating over the channels to find matching conditions
            for channel in campaign_channels:
                if interview_type.lower() in ['bot call', 'interview reminder', 'one on one', 'book calendar']:
                    if channel.channel_root_name == 'interview':
                        found_interview = True
                    if channel.channel_root_name == 'call':
                        found_call = True

            # Constructing the response based on the flags
            response = {
                'interview': found_interview,
                'bot': found_call
            }

            logger.info(f"Processed CheckCampaignInterview request successfully for campaign_id: {campaign_id}, interview_type: {interview_type}")
            return JsonResponse(response)

        except CampaignEvent.DoesNotExist:
            logger.warning(f"No campaign events found for campaign_id: {campaign_id}")
            return JsonResponse({'error': 'No campaign events found'}, status=status.HTTP_200_OK)
        except CampaignChannel.DoesNotExist:
            logger.warning(f"No campaign channels found for campaign_id: {campaign_id}")
            return JsonResponse({'error': 'No campaign channels found'}, status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

class GetUsersByApplicationId(View):
    def get(self, request):
        try:
            application_id = request.UserData.application_id
            
            if not application_id:
                logger.error("Missing application_id in token")
                return JsonResponse({'error': 'application_id is a required parameter.'}, status=status.HTTP_200_OK)

            # Filter users by application_id
            users = User.objects.filter(application_id=application_id)
            
            # Prepare the response data

            user_data = [{'id': user.id, 'name': user.name} for user in users]

            user_data = [{'id': user.id, 'username': user.username} for user in users]

            
            logger.info(f"Fetched {len(user_data)} users for application_id: {application_id}")
            return JsonResponse(user_data, safe=False, status=200)

        except User.DoesNotExist:
            logger.warning(f"No users found for application_id: {application_id}")
            return JsonResponse({'error': 'No users found for the given application_id'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)



class GetSegmentsByApplicationIdView(View):
    def get(self, request):
        try:
            application_id = request.UserData.application_id
            
            if not application_id:
                logger.error("Missing application_id in token")
                return JsonResponse({'error': 'application_id is a required parameter.'}, status=status.HTTP_200_OK)

            # Filter segments by application_id
            segments = Segments.objects.filter(application_id=application_id)
            
            # Prepare the response data
            segment_data = [{'id': segment.id, 'segment_name': segment.name} for segment in segments]
            
            logger.info(f"Fetched {len(segment_data)} segments for application_id: {application_id}")
            return JsonResponse(segment_data, safe=False, status=200)

        except Segments.DoesNotExist:
            logger.warning(f"No segments found for application_id: {application_id}")
            return JsonResponse({'error': 'No segments found for the given application_id'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)   


class ClientAPIView(View):
    def get(self, request, *args, **kwargs):
        try:
            clients = Client.objects.all().values()
            if clients:
                return JsonResponse(list(clients), safe=False, status=200)
            else:
                return JsonResponse({'message': 'No records found'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

class GetAssessmentsByApplicationIdView(View):
    def get(self, request):
        try:
            application_id = request.UserData.application_id

            if not application_id:
                logger.error("Missing application_id in request")
                return JsonResponse({'error': 'application_id is a required parameter.'}, status=status.HTTP_200_OK)

            # Filter assessments by application_id
            assessments = Assessment.objects.filter(application_id=application_id)

            # Prepare the response data
            assessment_data = [{'id': assessment.id, 'assessment_name': assessment.assessment_name} for assessment in assessments]

            logger.info(f"Fetched {len(assessment_data)} assessments for application_id: {application_id}")
            return JsonResponse(assessment_data, safe=False, status=200)

        except Assessment.DoesNotExist:
            logger.warning(f"No assessments found for application_id: {application_id}")
            return JsonResponse({'error': 'No assessments found for the given application_id'}, status=404)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


class SegmentCategoryByInterviewTypeView(APIView):
    def get(self, request, *args, **kwargs):
        # Get interview_type_id from the query parameters
        interview_type_id = request.query_params.get('interview_type_id')

        if not interview_type_id:
            return JsonResponse({"message": "interview_type_id is required."}, status=400)

        try:
            # Filter segment categories based on interview_type_id
            segment_categories = SegmentCategories.objects.filter(interview_type_id=interview_type_id).values('id', 'category_name')

            # Logging the successful retrieval
            logger.info(f"Segment categories retrieved successfully for interview_type_id: {interview_type_id}.")

            # Return the filtered data
            return JsonResponse({"segment_categories": list(segment_categories)}, status=200)

        except Exception as e:
            logger.error(f"An error occurred while fetching segment categories for interview_type_id {interview_type_id}: {str(e)}")
            return JsonResponse({"message": "An error occurred while processing the request."}, status=500)

class InterviewTypeListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Retrieve all interview types
            interview_types = InterviewType.objects.all().values('id', 'name')

            # Logging the successful retrieval
            logger.info("Interview types retrieved successfully.")

            # Return the data
            return JsonResponse({"interview_types": list(interview_types)}, status=200)

        except Exception as e:
            logger.error(f"An error occurred while fetching interview types: {str(e)}")
            return JsonResponse({"message": "An error occurred while processing the request."}, status=500)