from django.db import models
from django.utils import timezone
from .mendate_model import User, Application
from django.core.exceptions import ValidationError 
import uuid


class Segments(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255,null=True,blank=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'segments'

class InterviewType(models.Model):
    root_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'interview_type'

class SegmentCategories(models.Model):
    id = models.BigAutoField(primary_key=True)
    segment = models.ForeignKey(Segments, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    category_name= models.CharField(max_length=255,null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    interview_type = models.ForeignKey(InterviewType, on_delete=models.CASCADE)


    class Meta:
        managed = False
        db_table = 'segment_categories'

class BotDetails(models.Model):
    bot_name = models.CharField(max_length=45)
    bot_description = models.TextField()
    category = models.CharField(max_length=150)
    is_published = models.BooleanField()
    custom_data = models.JSONField()
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField()
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, db_column='created_by')
    file_name = models.CharField(max_length=45)
    segment = models.ForeignKey(Segments, on_delete=models.CASCADE, null=True, blank=True)  
    segment_category = models.ForeignKey(SegmentCategories, on_delete=models.CASCADE, null=True, blank=True)  

    class Meta:
        managed = False
        db_table = 'bot_details'



class Campaigns(models.Model):
    campaign_name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)
    allow_restart = models.BooleanField()
    is_published = models.BooleanField()
    publish_at = models.DateTimeField(null=True, blank=True)
    unpublish_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField()
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    segment = models.ForeignKey(Segments, on_delete=models.CASCADE, null=True, blank=True)  
    segment_category = models.ForeignKey(SegmentCategories, on_delete=models.CASCADE, null=True, blank=True)  

    class Meta:
        managed = False
        db_table = 'campaigns'



class Journey(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True,max_length = 255)

    # category = models.CharField(max_length=30)
    segment = models.ForeignKey(Segments, on_delete=models.CASCADE, null=True, blank=True)
    allow_contacts_to_restart = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        managed = False
        db_table = 'journey'

class StepType(models.Model):
    step_name = models.CharField(max_length=255)
    step_display_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'step_type'

class Client(models.Model):
    client_name = models.CharField(max_length=255)
    client_location = models.CharField(max_length=255, null=True, blank=True)
    client_about = models.TextField(null=True, blank=True)
    consensus_person_name = models.CharField(max_length=255)
    consensus_person_email = models.EmailField(max_length=254)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'client'


class Assessment(models.Model):
    assessment_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    # prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    department = models.ForeignKey('ApplicationDepartments', on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    # instructions = models.TextField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'assessment'


class JourneyEvents(models.Model):
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    interview_type = models.CharField(max_length=50)
    bot_language =  models.CharField(max_length=50, blank= True)


    # bot_type = models.CharField(max_length=100, blank=True, null=True)
    # bot_variant = models.CharField(max_length=100, blank=True, null=True)
    # bot_segment = models.CharField(max_length=100, blank=True, null=True)
    # campaign_segment = models.CharField(max_length=100, blank=True, null=True)
    # hiring_manager = models.CharField(max_length=100, blank=True, null=True)
    # hiring_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journey_events_as_manager', null=True, blank=True)

    integration_type = models.CharField(max_length=100, blank=True, null=True)
    test_type = models.CharField(max_length=100, blank=True, null=True)
    qualifying_criteria = models.IntegerField(default=0)
    campaign = models.ForeignKey(Campaigns, on_delete=models.CASCADE,blank=True,null=True)


    # campaign_type = models.CharField(max_length=100, blank=True, null=True)
    # campaign_variant = models.CharField(max_length=100, blank=True, null=True)

    close_link_within_interval = models.IntegerField(blank=True, null=True)
    close_link_within_unit = models.CharField(max_length=10, blank=True, null=True)
    immediately = models.BooleanField(default=False)
    relative_time_period_interval = models.IntegerField(blank=True, null=True)
    relative_time_period_unit = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='journey_events_as_user')
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    addr1 = models.CharField(max_length=255, blank=True, null=True)
    addr2 = models.CharField(max_length=255, blank=True, null=True)
    skills = models.CharField(max_length=255,blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    parent_id = models.BigIntegerField(default=0, null=True)
    Mark_as_Online = models.BooleanField(default=False)
    bot = models.ForeignKey(BotDetails, on_delete=models.CASCADE, null=True, blank=True)
    segment_category = models.ForeignKey('SegmentCategories', on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, null=True, blank=True)
    step_type = models.ForeignKey('StepType', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, null=True, blank=True)
    meeting_title = models.CharField(max_length=255, null=True, blank=True)
    meeting_duration = models.IntegerField(null=True, blank=True)
    step = models.ForeignKey(InterviewType, on_delete=models.CASCADE, null=True, blank=True)


    class Meta:
        managed = False
        db_table = 'journey_events'

class JourneyEventHiringManager(models.Model):
    id = models.BigAutoField(primary_key=True)
    journey_event = models.ForeignKey('JourneyEvents', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='hiring_manager_user')
    hiring_manager = models.ForeignKey('User', on_delete=models.CASCADE, related_name='hiring_manager')
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    

    class Meta:
        managed = False
        db_table = 'journey_event_hiring_manager'


class CandidateDetails(models.Model):
    first_name = models.CharField(max_length=45, null=True)
    middle_name = models.CharField(max_length=45, null=True)
    last_name = models.CharField(max_length=45, null=True)
    candidate_name = models.CharField(max_length=191, null=True)
    mobile_no = models.CharField(max_length=11)
    email = models.CharField(max_length=254)
    pan_no = models.CharField(max_length=6, null=True)
    aadharcard_number = models.BigIntegerField(null=True)
    skill_set = models.CharField(max_length=445, null=True)
    gender = models.IntegerField(null=True)
    current_organization = models.CharField(max_length=90, null=True)
    current_designation = models.CharField(max_length=90, null=True)
    overall_experience = models.CharField(max_length=90, null=True)
    relevant_experience = models.CharField(max_length=90, null=True)
    qualification = models.CharField(max_length=100, null=True)
    location = models.CharField(max_length=100, null=True)
    preferred_location = models.CharField(max_length=190, null=True)
    address = models.CharField(max_length=100, null=True)
    current_salary = models.CharField(max_length=100, null=True)
    expected_salary = models.CharField(max_length=100, null=True)
    notice_period = models.IntegerField(null=True)
    remark = models.CharField(max_length=100, null=True)
    industry_type = models.CharField(max_length=100, null=True)
    functional_area = models.CharField(max_length=100, null=True)
    dob = models.DateField(null=True)
    resume = models.CharField(max_length=100, null=True)
    cvhtml = models.TextField(null=True)
    ip_address = models.CharField(max_length=100, null=True)
    jobboard_url = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    pincode = models.IntegerField(null=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    country_code = models.CharField(max_length=4)
    is_deleted = models.BooleanField()
    documents = models.CharField(max_length=1000, default='{}')
    # journey = models.ForeignKey(Journey, null=True, on_delete=models.CASCADE)
    # job = models.ForeignKey('JobDetails', null=True, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'candidate_details'

class FunctionalAreas(models.Model):
    functional_areas_name = models.CharField(max_length=100, null=False, blank=False)
    code = models.CharField(max_length=8, null=False, blank=False)
    ip_address = models.CharField(blank=False, null=False, max_length=150, default='0.0.0.0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'functional_areas'


class Industries(models.Model):
    industry_name = models.CharField(max_length=100, null=False, blank=False)
    ip_address = models.CharField(blank=False, null=False, max_length=150, default='0.0.0.0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'industries'

class Trackers(models.Model):
    id = models.BigAutoField(primary_key=True)
    tracker_name = models.CharField(max_length=45)
    tracker_data = models.JSONField()
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_deleted = models.BooleanField()

    class Meta:
        managed=True
        db_table = 'trackers'

class ApplicationDepartments(models.Model):
    client_or_department = models.CharField(max_length=20)
    department_name = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE)
    head_of_department = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='head_of_department')
    department_location = models.CharField(max_length=255, null=True)
    is_deleted = models.BooleanField()
    client_about = models.TextField(null=True)

    class Meta:
        managed = False
        db_table = 'application_departments'


class JobDetails(models.Model):
    creater = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='created_jobs')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='managed_jobs')
    application = models.ForeignKey(Application, on_delete=models.CASCADE, default=1)
    department = models.ForeignKey(ApplicationDepartments, on_delete=models.CASCADE, default=1)
    slug = models.CharField(max_length=100, default='')
    job_title = models.CharField(max_length=100)
    job_status = models.CharField(max_length=100, default='Active')
    job_description = models.TextField()
    minimum_experience = models.IntegerField()
    maximum_experience = models.IntegerField()
    minimum_salary = models.IntegerField()
    maximum_salary = models.IntegerField()
    number_of_opening = models.IntegerField()
    is_referral = models.BooleanField(default=False)
    referral_bonus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)
    is_visible_on_app = models.BooleanField(default=False)
    visible_start_date = models.DateTimeField(null=True, blank=True)
    visible_end_date = models.DateTimeField(null=True, blank=True)
    keyskills = models.CharField(max_length=255,null=True,blank=True)
    first_skill = models.CharField(max_length=150,null=True,blank=True)
    second_skill = models.CharField(max_length=150,null=True,blank=True)
    third_skill = models.CharField(max_length=150,null=True,blank=True)
    ip_address = models.CharField(max_length=150, default='0.0.0.0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    hiring_manager_id = models.BigIntegerField(default=1)  
    event_name = models.TextField(blank=True, null=True)
    min_rating = models.IntegerField(default=0)
    interview_round = models.IntegerField(default=0)
    tracker = models.ForeignKey(Trackers, on_delete=models.CASCADE, null=True, blank=True)
    signing_authority = models.CharField(max_length=100, blank=True, null=True)
    salary_slab = models.CharField(max_length=100, blank=True, null=True)
    job_type = models.CharField(max_length=100, blank=True, null=True)
    industry = models.ForeignKey(Industries, on_delete=models.SET_NULL, blank=True, null=True)
    functional_area = models.ForeignKey(FunctionalAreas, on_delete=models.SET_NULL, blank=True, null=True)
    job_role = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    job_about = models.CharField(max_length=255, blank=True, null=True)
    internship_duration_interval = models.IntegerField(blank=True, null=True)
    internship_duration_unit = models.CharField(max_length=10, blank=True, null=True)
    contract_duration_interval = models.IntegerField(blank=True, null=True)
    contract_duration_unit = models.CharField(max_length=10, blank=True, null=True)
    contract_renewable = models.BooleanField(default=False)
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, null=True, blank=True)
    uid = models.CharField(max_length=200, unique=True, default=uuid.uuid4, db_column='uid')


    class Meta:
        managed = False
        db_table = 'job_details'

# class AddNewJob(models.Model):
#     creater = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='created_jobs')
#     manager = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='managed_jobs')
#     application = models.ForeignKey(Application, on_delete=models.CASCADE, default=1)
#     department = models.ForeignKey(ApplicationDepartments, on_delete=models.CASCADE, default=1)
#     slug = models.CharField(max_length=100, default='')
#     job_title = models.CharField(max_length=100)
#     job_status = models.CharField(max_length=100, default='Active')
#     job_description = models.TextField()
#     minimum_experience = models.IntegerField()
#     maximum_experience = models.IntegerField()
#     minimum_salary = models.IntegerField()
#     maximum_salary = models.IntegerField()
#     number_of_opening = models.IntegerField()
#     is_referral = models.BooleanField(default=False)
#     referral_bonus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     location = models.CharField(max_length=255)
#     is_approved = models.BooleanField(default=False)
#     is_visible_on_app = models.BooleanField(default=False)
#     visible_start_date = models.DateTimeField(null=True, blank=True)
#     visible_end_date = models.DateTimeField(null=True, blank=True)
#     keyskills = models.CharField(max_length=255,null=True,blank=True)
#     first_skill = models.CharField(max_length=150,null=True,blank=True)
#     second_skill = models.CharField(max_length=150,null=True,blank=True)
#     third_skill = models.CharField(max_length=150,null=True,blank=True)
#     ip_address = models.CharField(max_length=150, default='0.0.0.0')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_deleted = models.BooleanField(default=False)
#     hiring_manager_id = models.BigIntegerField(default=1)  
#     event_name = models.TextField(blank=True, null=True)
#     min_rating = models.IntegerField(default=0)
#     interview_round = models.IntegerField(default=0)
#     tracker = models.ForeignKey(Trackers, on_delete=models.CASCADE, null=True, blank=True)
#     signing_authority = models.CharField(max_length=100, blank=True, null=True)
#     salary_slab = models.CharField(max_length=100, blank=True, null=True)
#     job_type = models.CharField(max_length=100, blank=True, null=True)
#     industry = models.ForeignKey(Industries, on_delete=models.SET_NULL, blank=True, null=True)
#     functional_area = models.ForeignKey(FunctionalAreas, on_delete=models.SET_NULL, blank=True, null=True)
#     job_role = models.CharField(max_length=100, blank=True, null=True)
#     notes = models.TextField(blank=True, null=True)
#     job_about = models.CharField(max_length=255, blank=True, null=True)
#     internship_duration_interval = models.IntegerField(blank=True, null=True)
#     internship_duration_unit = models.CharField(max_length=10, blank=True, null=True)
#     contract_duration_interval = models.IntegerField(blank=True, null=True)
#     contract_duration_unit = models.CharField(max_length=10, blank=True, null=True)
#     contract_renewable = models.BooleanField(default=False)
#     journey = models.ForeignKey(Journey, on_delete=models.CASCADE, null=True, blank=True)
#     uid = models.CharField(max_length=200, unique=True, default=uuid.uuid4, db_column='uid')

#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.job_title)
#         super().save(*args, **kwargs)

#     def clean(self):
#         if self.is_referral and self.referral_bonus is None:
#             raise ValueError("Referral bonus is required when isReferral is set to 'Yes'.")
#         if self.is_visible_on_app and (self.visible_start_date is None or self.visible_end_date is None):
#             raise models.ValidationError("Both startdate and enddate are required when is_visible_on_app is set to 'Yes'.")
#         if self.maximum_experience is not None and self.minimum_experience is not None:
#             if float(self.maximum_experience) <= float(self.minimum_experience):
#                 raise ValidationError("Maximum experience must be greater than minimum experience.")

#     class Meta:
#         managed = True
#         db_table = 'job_details'




class HiringManagers(models.Model):
    available_end_time = models.TimeField(null=True)
    available_start_time = models.TimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    department_id = models.ForeignKey('ApplicationDepartments', on_delete=models.CASCADE)
    email = models.EmailField()
    is_deleted = models.BooleanField()
    mobile = models.CharField(max_length=455, null=True)
    msg_send = models.CharField(max_length=500)
    name = models.CharField(max_length=105, null=True)
    platform = models.CharField(max_length=100, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    calendar = models.CharField(max_length=100, null=True)
    off_days = models.CharField(max_length=100, null=True)

    class Meta:
        managed = False
        db_table = 'hiring_managers'






class EmailTemplate(models.Model):
  
    template_name = models.CharField(max_length=100)
    template_area = models.CharField(max_length=45)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sended_by = models.CharField(max_length=50)
    sender_name = models.CharField(max_length=50)
    ip_address = models.CharField(max_length=150, default='0.0.0.0')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_deleted = models.BooleanField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    application_id = models.ForeignKey(Application, on_delete=models.CASCADE)
    design = models.TextField(blank=True, null=True)

    class Meta:
        managed=False
        db_table = 'email_templates'


class CampaignChannel(models.Model):
    
    channel_name = models.CharField(max_length=45)
    channel_root_name = models.CharField(max_length=45)

    class Meta:
        managed=False
        db_table = 'campaign_channels'
    
class RefererPaymentStatus(models.Model):
   
    status_name = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_deleted = models.BooleanField()

    class Meta:
        managed=False
        db_table = 'referer_payment_statuses'

    

class SmsTemplate(models.Model):
    
    template_name = models.CharField(max_length=100)
    template_area = models.CharField(max_length=45)
    message = models.TextField()
    sended_by = models.CharField(max_length=50)
    sender_name = models.CharField(max_length=50)
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_deleted = models.BooleanField()
    added_by = models.ForeignKey('User', on_delete=models.CASCADE)
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    dlt_te_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed=False
        db_table = 'sms_templates'

class CampaignActionBasedStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    status_name = models.CharField(max_length=45)
    create_at = models.DateTimeField()
    update_at = models.DateTimeField()

    class Meta:
        managed=False
        db_table='campaign_action_based_status'

class CandidateStatuses(models.Model):
    
    display_name = models.CharField(max_length=255)
    root_name = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_deleted = models.BooleanField()
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    is_interview = models.BooleanField()
    referer_status = models.ForeignKey('RefererPaymentStatus', on_delete=models.CASCADE)
    candidate_email_template = models.ForeignKey('EmailTemplate', on_delete=models.SET_NULL, null=True, blank=True, related_name='candidate_email_templates')
    candidate_sms_template = models.ForeignKey('SmsTemplate', on_delete=models.SET_NULL, null=True, blank=True, related_name='candidate_sms_templates')
    referer_email_template = models.ForeignKey('EmailTemplate', on_delete=models.SET_NULL, null=True, blank=True, related_name='referer_email_templates')
    referer_sms_template = models.ForeignKey('SmsTemplate', on_delete=models.SET_NULL, null=True, blank=True, related_name='referer_sms_templates')
    campaign_action_based_status = models.ForeignKey(CampaignActionBasedStatus, on_delete=models.CASCADE)

    class Meta:
        managed=False
        db_table = 'candidate_statuses'

class Referrer(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    uid = models.CharField(max_length=200, unique=True)
    is_email_confirmed = models.BooleanField()
    is_mobile_confirmed = models.BooleanField()
    is_internal_referrer = models.BooleanField()
    email = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=12, null=True)
    date_joined = models.DateTimeField()
    last_login = models.DateTimeField()
    is_active = models.BooleanField()
    name = models.CharField(max_length=100)
    gender = models.IntegerField(null=True)
    profile_pic = models.CharField(max_length=150, null=True)
    mobile_no = models.CharField(max_length=150, unique=True)
    dob = models.DateField()
    short_name = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    
    class Meta:
        managed = False
        db_table= 'referrers'


class AddToJobs(models.Model):
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    application = models.ForeignKey('Application', on_delete=models.CASCADE, related_name='add_to_jobs')
    candidate = models.ForeignKey('CandidateDetails', on_delete=models.CASCADE, related_name='add_to_jobs')
    job = models.ForeignKey('JobDetails', on_delete=models.CASCADE, related_name='add_to_jobs')
    status = models.ForeignKey('CandidateStatuses', on_delete=models.CASCADE, related_name='add_to_jobs')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='add_to_jobs')
    is_referred = models.BooleanField(default=False)
    referer_status = models.ForeignKey('RefererPaymentStatus', on_delete=models.CASCADE, related_name='add_to_jobs')
    referrer_id =  models.IntegerField(null=True, blank=True)
    campaign_id =  models.IntegerField(null=True, blank=True)
    campaign_event_id =  models.IntegerField(null=True, blank=True)
    campaign_status = models.IntegerField(null=True, blank=True)
    campaign_run_time = models.DateTimeField()
    attachment = models.CharField(max_length=1000, null=True, blank=True)
    journey_status = models.CharField(max_length=255, null=True, blank=True)
    journey_update = models.BooleanField(default=False)
    journey = models.ForeignKey('Journey', null=True, blank=True, on_delete=models.CASCADE, related_name='add_to_jobs')
    error_occurred = models.BooleanField(default=False) 

    class Meta:
        managed = False
        db_table='add_to_jobs'


class CandidateJourney(models.Model):
    job = models.ForeignKey('JobDetails', on_delete=models.CASCADE)
    journey = models.ForeignKey('Journey', on_delete=models.CASCADE)
    candidate = models.ForeignKey('CandidateDetails', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    add_to_job = models.ForeignKey('AddToJobs', on_delete=models.CASCADE, null=True, blank=True)
    bot = models.ForeignKey(BotDetails, on_delete=models.CASCADE, null=True, blank=True)
    campaign = models.ForeignKey('Campaigns', on_delete=models.CASCADE, null=True, blank=True)
    hiring_managers = models.ForeignKey('HiringManagers', on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    campaign_status = models.CharField(max_length=255, null=True, blank=True)
    is_update = models.BooleanField(default=False, null=True)
    journey_event = models.ForeignKey('JourneyEvents', on_delete=models.CASCADE)
    is_next_event_added = models.BooleanField(default=False)
    qualifying_criteria = models.IntegerField(default=0, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    status = models.ForeignKey(CandidateStatuses, on_delete=models.CASCADE, null=True, blank=True)
    candidate = models.ForeignKey('CandidateDetails', on_delete=models.CASCADE, db_column='candidate_id')

    class Meta:
        managed = False
        db_table = 'candidate_journey'



class CampaignEvent(models.Model):
    
    event_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=25)
    event_order = models.IntegerField()
    trigger_date = models.DateTimeField(blank=True, null=True)
    trigger_interval = models.IntegerField(blank=True, null=True)
    trigger_interval_unit = models.CharField(max_length=25, blank=True, null=True)
    trigger_mode = models.CharField(max_length=45, blank=True, null=True)
    channel = models.ForeignKey('CampaignChannel', on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    campaign = models.ForeignKey('Campaigns', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    candidate_status = models.ForeignKey('CandidateStatuses', on_delete=models.SET_NULL, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    color = models.CharField(max_length=25)
    temp_id = models.IntegerField(blank=True, null=True)
    # bot_id = models.IntegerField(blank=True, null=True)
    # email_template_id = models.IntegerField(blank=True, null=True)
    # flow_type = models.CharField(max_length=45, blank=True, null=True)
    # sms_template_id = models.IntegerField(blank=True, null=True)
    # flow_up_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'campaign_events'

# class CampaignTriggers(models.Model):
    
#     ip_address = models.CharField(max_length=150)
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(default=timezone.now)
#     add_to_job = models.ForeignKey('AddToJobs', on_delete=models.CASCADE)
#     application = models.ForeignKey('Application', on_delete=models.CASCADE)
#     campaign = models.ForeignKey('Campaigns', on_delete=models.CASCADE)
#     candidate = models.ForeignKey('CandidateDetails', on_delete=models.CASCADE)
#     client_department = models.ForeignKey('ApplicationDepartments', on_delete=models.CASCADE)
#     job = models.ForeignKey('JobDetails', on_delete=models.CASCADE)
#     status = models.ForeignKey('CandidateStatuses', on_delete=models.SET_NULL, null=True, blank=True)
#     user = models.ForeignKey('User', on_delete=models.CASCADE)
#     # later_time = models.DateTimeField(blank=True, null=True)
#     journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
#     journey_event=models.ForeignKey(JourneyEvents, on_delete=models.CASCADE)
#     candidate_journey=models.ForeignKey(CandidateJourney, on_delete=models.CASCADE)
#     action_root_name=models.CharField(max_length=4,blank=True,null=True)
#     parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_triggers')

#     class Meta:
#         managed=False
#         db_table = 'campaign_triggers'

class CampaignTriggers(models.Model):
    action_name = models.CharField(max_length=45)
    action_root_name = models.CharField(max_length=45)
    action_temp_id = models.IntegerField(blank=True, null=True)
    channel_id = models.IntegerField(blank=True, null=True)
    action_run_time = models.DateTimeField()
    next_action_time = models.DateTimeField(blank=True, null=True)
    candidate_id = models.IntegerField(blank=True, null=True)
    add_to_job = models.ForeignKey('AddToJobs', on_delete=models.CASCADE, db_column='add_to_job_id')
    event_id = models.IntegerField(blank=True, null=True)
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_action = models.BooleanField()
    is_next_action = models.BooleanField()
    job = models.ForeignKey('JobDetails', on_delete=models.CASCADE, db_column='job_id', blank=True, null=True)
    client_department = models.ForeignKey('ApplicationDepartments', on_delete=models.CASCADE, db_column='client_department_id', blank=True, null=True)
    is_ready_to_next_event = models.BooleanField()
    call_type = models.CharField(max_length=45, blank=True, null=True)
    journey = models.ForeignKey('Journey', on_delete=models.CASCADE, db_column='journey_id', blank=True, null=True)
    journey_event = models.ForeignKey('JourneyEvents', on_delete=models.CASCADE, db_column='journey_event_id', blank=True, null=True)
    application = models.ForeignKey('Application', on_delete=models.CASCADE, db_column='application_id')
    campaign = models.ForeignKey('Campaigns', on_delete=models.CASCADE, db_column='campaign_id')
    candidate_journey = models.ForeignKey('CandidateJourney', on_delete=models.CASCADE, db_column='candidate_journey_id')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='parent_id', related_name='sub_triggers')
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_column='user_id')
    status = models.ForeignKey('CandidateStatuses', on_delete=models.SET_NULL, blank=True, null=True, db_column='status_id')

    class Meta:
        managed = False  
        db_table = 'campaign_triggers'

class EmailLog(models.Model):
    uid = models.CharField(max_length=200, unique=True)
    sended_by = models.CharField(max_length=50)
    sended_to = models.CharField(max_length=50)
    is_send = models.IntegerField()
    is_read = models.BooleanField()
    read_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField()
    subject = models.CharField(max_length=500, null=True, blank=True)
    attachment = models.CharField(max_length=500, null=True, blank=True)
    sended_cc = models.CharField(max_length=500, null=True, blank=True)
    sended_bcc = models.CharField(max_length=500, null=True, blank=True)
    sent_date = models.DateTimeField()
    to_be_sent_date = models.DateTimeField(null=True, blank=True)
    is_otp = models.IntegerField()
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_deleted = models.BooleanField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    candidate = models.ForeignKey(CandidateDetails, on_delete=models.CASCADE)
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    sender_name = models.CharField(max_length=50)
    is_update = models.IntegerField(null=True, blank=True)
    is_smtp = models.BooleanField()
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, null=True, blank=True)
    journey_event = models.ForeignKey(JourneyEvents, on_delete=models.CASCADE, null=True, blank=True)
    candidate_journey = models.ForeignKey(CandidateJourney, on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(JobDetails, on_delete=models.CASCADE, null=True, blank=True)
    campaign_trigger = models.ForeignKey(CampaignTriggers, on_delete=models.CASCADE, null=True, blank=True, related_name='email_logs')

    class Meta:
        managed = False
        db_table = 'email_logs'

class CampaignTriggerHistory(models.Model):
    
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    action_name = models.CharField(max_length=45)
    action_root_name = models.CharField(max_length=45)
    action_temp_id = models.IntegerField(null=True, blank=True)
    next_action_time = models.DateTimeField(null=True, blank=True)
    status_id = models.ForeignKey('CandidateStatuses', on_delete=models.SET_NULL, null=True, blank=True)
    add_to_job = models.ForeignKey('AddToJobs', on_delete=models.CASCADE)
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    campaign = models.ForeignKey('Campaigns', on_delete=models.CASCADE)
    candidate = models.ForeignKey('CandidateDetails', on_delete=models.CASCADE)
    event_id = models.ForeignKey('CampaignEvent', on_delete=models.CASCADE)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    is_action = models.BooleanField(default=True)
    is_next_action = models.BooleanField(default=True)
    parent_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    channel_id = models.ForeignKey('CampaignChannel', on_delete=models.CASCADE)
    action_run_time = models.DateTimeField()
    client_department = models.ForeignKey('ApplicationDepartments', on_delete=models.CASCADE)
    job_id = models.ForeignKey('JobDetails', on_delete=models.CASCADE)
    is_ready_to_next_event = models.BooleanField(default=True)
    trigger_id = models.ForeignKey('self', on_delete=models.CASCADE, related_name='trigger_history')
    call_type = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        managed=False
        db_table = 'campaign_triggers_history'

class SmsLog(models.Model):
    
    uid = models.CharField(max_length=200, unique=True)
    sended_by = models.CharField(max_length=50)
    sended_to = models.CharField(max_length=50)
    is_send = models.IntegerField()
    is_read = models.BooleanField()
    read_at = models.DateTimeField(blank=True, null=True)
    message = models.TextField()
    sent_date = models.DateTimeField()
    to_be_sent_date = models.DateTimeField(blank=True, null=True)
    is_otp = models.IntegerField()
    dtl_te_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField()
    added_by = models.ForeignKey('User', on_delete=models.CASCADE)
    application = models.ForeignKey('Application', on_delete=models.CASCADE)
    candidate = models.ForeignKey('CandidateDetails', on_delete=models.CASCADE)
    sms_template = models.ForeignKey('SmsTemplate', on_delete=models.CASCADE)
    is_update = models.IntegerField(blank=True, null=True)
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, null=True, blank=True)
    journey_event = models.ForeignKey(JourneyEvents, on_delete=models.CASCADE, null=True, blank=True)
    candidate_journey = models.ForeignKey(CandidateJourney, on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(JobDetails, on_delete=models.CASCADE, null=True, blank=True)

    
    class Meta:
        managed=False
        db_table = 'sms_logs'



class SubmitPanel(models.Model):
    candidate = models.ForeignKey('CandidateDetails', on_delete=models.CASCADE)
    journey = models.ForeignKey('Journey', on_delete=models.CASCADE)
    journey_event = models.ForeignKey('JourneyEvents', on_delete=models.CASCADE)
    candidate_journey = models.ForeignKey('CandidateJourney', on_delete=models.CASCADE)
    uid = models.CharField(max_length=200, unique=True, default=uuid.uuid4, db_column='uid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hiring_manager_ids = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        managed=False
        db_table = 'submit_panel'

class SubmitClient(models.Model):
    candidate = models.ForeignKey('CandidateDetails', on_delete=models.CASCADE)
    journey = models.ForeignKey('Journey', on_delete=models.CASCADE)
    journey_event = models.ForeignKey('JourneyEvents', on_delete=models.CASCADE)
    candidate_journey = models.ForeignKey('CandidateJourney', on_delete=models.CASCADE)
    client_id = models.BigIntegerField(null=True, blank=False)
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed=False
        db_table = 'submit_client'


class Calls(models.Model):
    country_code = models.CharField(max_length=4)
    mobile_no = models.CharField(max_length=11)
    call_status = models.CharField(max_length=50)
    disposition = models.CharField(max_length=50)
    call_language = models.CharField(max_length=50)
    custom_data = models.JSONField()
    conversation = models.TextField(blank=True, null=True)
    last_question = models.TextField(blank=True, null=True)
    call_start_time = models.DateTimeField(blank=True, null=True)
    call_end_time = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField()
    call_duration = models.FloatField(blank=True, null=True)
    to_send_jd = models.BooleanField()
    interview_time_start = models.DateTimeField(blank=True, null=True)
    interview_time_end = models.DateTimeField(blank=True, null=True)
    gram_check_text = models.TextField(blank=True, null=True)
    gram_check_text_2 = models.TextField(blank=True, null=True)
    gram_check_perc = models.FloatField(blank=True, null=True)
    gram_check_perc_2 = models.FloatField(blank=True, null=True)
    grammer_avg_rating = models.FloatField(blank=True, null=True)
    skill_1 = models.FloatField(blank=True, null=True)
    skill_2 = models.FloatField(blank=True, null=True)
    skill_3 = models.FloatField(blank=True, null=True)
    skill_avg_rating = models.BooleanField()
    grammer_interview_audio_link1 = models.CharField(max_length=500, blank=True, null=True)
    grammer_interview_audio_link2 = models.CharField(max_length=500, blank=True, null=True)
    is_validate_conversation = models.BooleanField()
    call_to = models.CharField(max_length=50)
    islater = models.BooleanField()
    inbound_lead = models.BooleanField()
    type_of_call = models.CharField(max_length=50)
    call_credit = models.CharField(max_length=50)
    call_initiate_id = models.CharField(max_length=50)
    is_data_update = models.BooleanField()
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(CandidateDetails, on_delete=models.CASCADE)
    job = models.ForeignKey(JobDetails, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    campaign_trigger_id = models.ForeignKey(CampaignTriggers, on_delete=models.CASCADE, blank=True, null=True)
    bot_status_id = models.ForeignKey(CandidateStatuses, on_delete=models.CASCADE)
    is_update = models.IntegerField(blank=True, null=True)
    latter = models.DateTimeField(blank=True, null=True)
    other_slots = models.TextField(blank=True, null=True)
    campaign_trigger_history_id = models.BigIntegerField(blank=True, null=True)
    campaign_event_id = models.BigIntegerField(blank=True, null=True)
    campaign_id = models.BigIntegerField(blank=True, null=True)
    call_history_id = models.IntegerField(blank=True, null=True)
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, blank=True, null=True)
    journey_event = models.ForeignKey(JourneyEvents, on_delete=models.CASCADE, blank=True, null=True)
    candidate_journey = models.ForeignKey(CandidateJourney, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        managed=False
        db_table = 'calls'

class JobCandidateHistories(models.Model):
    id = models.BigAutoField(primary_key=True)
    comment = models.TextField(blank=True, null=True)
    is_interview = models.BooleanField(default=False)
    reminder_date = models.DateField(blank=True, null=True)
    ip_address = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachment = models.CharField(max_length=1000, blank=True, null=True)
    application = models.ForeignKey('Application', on_delete=models.CASCADE, related_name='job_candidate_histories')
    atj = models.ForeignKey('AddToJobs', on_delete=models.CASCADE, related_name='job_candidate_histories')
    candidate = models.ForeignKey('CandidateDetails', on_delete=models.CASCADE, related_name='job_candidate_histories')
    status = models.ForeignKey('CandidateStatuses', on_delete=models.CASCADE, related_name='job_candidate_histories')
    job = models.ForeignKey('JobDetails', on_delete=models.CASCADE, related_name='job_candidate_histories')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='job_candidate_histories')

    class Meta:
        managed= False
        db_table = 'job_candidate_histories'