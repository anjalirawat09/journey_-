# urls.py
from django.urls import path
from . import views
from .views import JourneyEventsListAPIView, JourneyAPIView,  AddJobAPIView, CandidateNextEventAdditionAPIView, JourneyShowAPIView, ShowjourneyeventsListAPIView, GetSegmentCategoriesView,GetBotsBySegmentCategoryView,GetCampaignsBySegmentCategoryView,CheckCampaignInterview,GetUsersByApplicationId,GetSegmentsByApplicationIdView,SegmentCategoryByInterviewTypeView
from .inprocess import JobDashboardView,CandidateView

# ,CandidateJourneyFlowView
from .candidate_details import JobDataView,JourneyDetailsView,CandidateJourneyDetailsView,CampaignDataView,JourneyEventDetails,CandidateCallsEmailsSms,AddToJobsJobDetails,CampaignTriggersView,CallsByCampaignTriggerView,EmailLogsByCampaignTriggerView

# ,CandidateJourneyFlowView
from .views import GetAssessmentsByApplicationIdView,ClientAPIView,InterviewTypeListView


urlpatterns = [
    path('journey/', JourneyAPIView.as_view(), name='journey-list'),
    path('journey/<int:journey_id>/', JourneyAPIView.as_view(), name='journey-update'),
    path('journey/<int:journey_id>/', JourneyAPIView.as_view(), name='journey-list-delete'),
    path('journey/show/<int:journey_id>/', JourneyShowAPIView.as_view(), name='journey-list-show'),
    path('journey/show/', JourneyShowAPIView.as_view(), name='journey-list-show'),
    path('journey-event/', JourneyEventsListAPIView.as_view()),
    path('journey-event/<int:journey_id>/', JourneyEventsListAPIView.as_view()),
    path('event/<int:id>/', JourneyEventsListAPIView.as_view()),
    path('event/', JourneyEventsListAPIView.as_view()),
    path('event/show/<int:event_id>/', ShowjourneyeventsListAPIView.as_view(), name='interview-details-edit'),
    path('event/show/', ShowjourneyeventsListAPIView.as_view(), name='interview-details-edit'),
    path('addtojob-journey-update/', AddJobAPIView.as_view(), name='add-job'),
    path('addnextevent-by-camapignstatus/', CandidateNextEventAdditionAPIView.as_view(), name ='next-event-addition'),
    path('job-candidatestatus-counts/<int:job_id>/', JobDashboardView.as_view(), name='job-dashboard'),
    path('candidate_details-for-statuscounts/', CandidateView.as_view(), name='candidate_details'),

    path('get-segment-categories/<int:journey_id>/', GetSegmentCategoriesView.as_view(), name='get-segment-categories'),
    path('get-bots-by-segment-category/<int:segment_category_id>/', GetBotsBySegmentCategoryView.as_view(), name='get-bots-by-segment-category'),
    path('get-campaigns-by-segment-category/<int:segment_category_id>/', GetCampaignsBySegmentCategoryView.as_view(), name='get-camapigns-by-segment-category'),
    path('check-interview-type/<int:campaign_id>/',CheckCampaignInterview.as_view(), name='get-campaign-event-details'),

    path('managers/by-application/', GetUsersByApplicationId.as_view(), name='get_users_by_application_id'),

    path('segments/by-application/', GetSegmentsByApplicationIdView.as_view(), name='get_segments_by_application_id'),
    path('client/', ClientAPIView.as_view(), name='client_api'),
    # path('candidate-journey-flow/<int:candidate_id>/', CandidateJourneyFlowView.as_view(), name='candidate_journey_flow'),

    path('job_data/<int:candidate_id>/<int:job_id>/', JobDataView.as_view(), name='combined-data'),
    path('journey-details/<int:candidate_id>/<int:job_id>/', JourneyDetailsView.as_view(), name='journey-details'),
    path('candidate-journey-details/<int:candidate_id>/<int:job_id>/', CandidateJourneyDetailsView.as_view(), name='candidate-journey-details'),
    path('campaign-data/<int:candidate_journey_id>/', CampaignDataView.as_view(), name='campaign-data'),
    path('journey-event-details/<int:candidate_id>/<int:job_id>/', JourneyEventDetails.as_view(), name='journey-event-details'),  
    path('candidate-job-details/<int:candidate_id>/<int:job_id>/', CandidateCallsEmailsSms.as_view(), name='candidate-job-details'),

    path('add-to-jobs-job-details/', AddToJobsJobDetails.as_view(), name='add_to_jobs_job_details'),
    path('campaign_details/', CampaignTriggersView.as_view(), name='campaign_triggers'),
    path('calls/by-campaign-trigger/', CallsByCampaignTriggerView.as_view(), name='calls_by_campaign_trigger'),
    path('email-logs/by-campaign-trigger/', EmailLogsByCampaignTriggerView.as_view(), name='email_logs_by_campaign_trigger'),
    path('assessments/by-applicationid/', GetAssessmentsByApplicationIdView.as_view(), name='assessment-names'),

    path('segment-categories-by-interview_type/', views.SegmentCategoryByInterviewTypeView.as_view(), name='segment_categories_by_interview_type'),
    path('interview-types/', views.InterviewTypeListView.as_view(), name='interview_type_list'),


]

