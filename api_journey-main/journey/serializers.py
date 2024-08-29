from rest_framework import serializers
import re,bleach 
from .models import Journey, JourneyEvents, BotDetails,CampaignEvent, CampaignChannel,JourneyEventHiringManager,Campaigns,CandidateStatuses, StepType
from .mendate_model import User, Application

class JourneySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    application_name = serializers.CharField(source='application.application_name', read_only=True)
    segment_name = serializers.CharField(source='segment.name', read_only=True)

    class Meta:
        model = Journey
        fields = '__all__'

    def validate_name(self, value):
        cleaned_value = bleach.clean(value, tags=[], attributes={}, strip=True)
        cleaned_value = cleaned_value.strip() 
        if not re.match(r'^[a-zA-Z\s-]+$', cleaned_value):
            raise serializers.ValidationError("Name should only contain alphabetic characters, spaces, and hyphens.")
        return cleaned_value
    

    def validate_description(self, value):
        cleaned_value = bleach.clean(value, tags=[], attributes={}, strip=True)
        cleaned_value = cleaned_value.strip()  
        if not re.match(r'^[a-zA-Z0-9\s!"#$%&\'()*+,\-./:;=?@\[\\\]^_`{|}~]*$', cleaned_value):
            raise serializers.ValidationError("Description should only contain alphanumeric characters, spaces, and allowed special characters.")
        return cleaned_value
     
    def validate_allow_contacts_to_restart(self, value):
        if isinstance(value, str):
            value = value.strip().lower()  
            if value == 'true':
                return True
            elif value == 'false':
                return False
            else:
                raise serializers.ValidationError("allow_contacts_to_restart must be either true or false.")
        elif isinstance(value, bool):
            return value
        else:
            raise serializers.ValidationError("allow_contacts_to_restart must be either true or false.")
    
    def validate_published(self, value):
        if isinstance(value, str):
            value = value.strip().lower()  
            if value == 'true':
                return True
            elif value == 'false':
                return False
            else:
                raise serializers.ValidationError("published must be either true or false.")
        elif isinstance(value, bool):
            return value
        else:
            raise serializers.ValidationError("published must be either true or false.")




# class JourneyEventsSerializer(serializers.ModelSerializer):
    
    
#     class Meta:
#         model = JourneyEvents
#         fields = '__all__'

#     def validate(self, data):
#         interview_type = data.get('interview_type')

#         if not interview_type:
#             raise serializers.ValidationError({"interview_type": "This field is required."})

#         interview_type_normalized = interview_type.strip().lower()

#         if interview_type_normalized == 'bot call':
#             self.validate_bot_call(data)
#         elif interview_type_normalized == 'one on one':
#             self.validate_one_on_one(data)
#         elif interview_type_normalized == 'third party integration':
#             self.validate_third_party_integration(data)

        
#         if not data.get('immediately') and not data.get('relative_time_period_interval'):
#             raise serializers.ValidationError("Either 'immediately' or 'relative_time_period_interval' must be provided.")
#         if data.get('immediately') and data.get('relative_time_period_interval'):
#             raise serializers.ValidationError("Both 'immediately' and 'relative_time_period' cannot be provided together.")
        
#         if data.get('relative_time_period_interval') is not None and not data.get('relative_time_period_unit'):
#             raise serializers.ValidationError("relative_time_period_unit cannot be null if relative_time_period_interval is provided.")   
#         return data

    
    
#     def validate_bot_call(self, data):
#         required_fields = [
#             'bot_type', 'bot_variant', 'bot_segment', 'skills',
#             'campaign_type', 'campaign_variant', 'campaign_segment', 'bot_language','bot','campaign'
#         ]
#         self.check_required_fields(data, required_fields, 'Bot Call')
        
#     def validate_one_on_one(self, data):
#         required_fields = [
#         'campaign_segment', 'hiring_manager', 'campaign_type', 'campaign_variant','campaign'
#         ]

#         mark_as_online = data.get('Mark_as_Online', False)
        
#         if not mark_as_online:
            
#             required_fields.extend(['state', 'city', 'addr1', 'addr2'])
#             self.check_required_fields(data, required_fields, 'One on one')

        

#         else:
            
#             for field in ['state', 'city', 'addr1', 'addr2']:
#                 if field in data and data[field] is not None:
#                     raise serializers.ValidationError({
#                     field: f"This field should be null when 'Mark_as_Online' is True for 'One on one' interview type."
#                 })



        

#     def validate_third_party_integration(self, data):
#         required_fields = [
#             'test_type', 'qualifying_criteria', 'campaign_type', 'campaign_variant', 'integration_type',
#             'campaign_segment', 'close_link_within_interval','close_link_within_unit','campaign'
#         ]
#         self.check_required_fields(data, required_fields, 'Third Party integration')

    
   

#     def check_required_fields(self, data, required_fields, interview_type):
#         missing_fields = [field for field in required_fields if not data.get(field)]
#         if missing_fields:
#             raise serializers.ValidationError({
#                 field: f"This field is required for '{interview_type}' interview type." for field in missing_fields
#             })
       

#     def validate_immediately(self, value):
#         if isinstance(value, str):
#             value = value.strip().lower()
#             if value == 'true':
#                 return True
#             elif value == 'false':
#                 return False
#             else:
#                 raise serializers.ValidationError("immediately must be either 'true' or 'false'.")

#         elif isinstance(value, bool):
#             return value

#         else:
#             raise serializers.ValidationError("immediately must be either 'true' or 'false'.")

    

#     def validate_interview_type(self, value):
#         cleaned_value = bleach.clean(value, tags=[], attributes={}, strip=True)
#         if not re.match(r'^[a-zA-Z\s-]+$', cleaned_value):
#             raise serializers.ValidationError("Interview type should only contain alphabetic characters, spaces, and hyphens.")
#         return cleaned_value
    

#     def validate_string_field(self, value, field_name):
#         if value is None or value.strip() == '':
#             return None
#         if not isinstance(value, str):
#             raise serializers.ValidationError(f"{field_name} must be a string.")
        
#         cleaned_value = bleach.clean(value, tags=[], attributes={}, strip=True)
        
        
#         if not re.match(r'^[a-zA-Z0-9\s]+$', cleaned_value):
#             raise serializers.ValidationError(f"{field_name} should only contain alphanumeric characters and spaces.")
        
#         return cleaned_value

   
#     def validate_bot_type(self, value):
      
#         return self.validate_string_field(value, "bot_type")

#     def validate_bot_variant(self, value):
       
#         return self.validate_string_field(value, "bot_variant")

#     def validate_bot_segment(self, value):
      
#         return self.validate_string_field(value, "bot_segment")

#     def validate_campaign_segment(self, value):
       
#         return self.validate_string_field(value, "campaign_segment")

#     def validate_hiring_manager(self, value):
       
#         return self.validate_string_field(value, "hiring_manager")

#     def validate_integration_type(self, value):
       
#         return self.validate_string_field(value, "integration_type")

#     def validate_test_type(self, value):
       
#         return self.validate_string_field(value, "test_type")

    
#     def validate_campaign_type(self, value):
       
#         return self.validate_string_field(value, "campaign_type")

#     def validate_campaign_variant(self, value):
       
#         return self.validate_string_field(value, "campaign_variant")

#     def validate_state(self, value):
       
#         return self.validate_string_field(value, "state")

#     def validate_city(self, value):
        
#         return self.validate_string_field(value, "city")

#     def validate_addr1(self, value):
       
#         return self.validate_string_field(value, "addr1")

#     def validate_addr2(self, value):
       
#         return self.validate_string_field(value, "addr2")

#     def validate_skills(self, value):
       
#         return self.validate_string_field(value, "skills")
    
#     def validate_relative_time_period(self,value):
       
#         return self.validate_string_field(value, "relative_time_period")

#     def validate_Mark_as_Online(self, value):
        
#         if isinstance(value, str):
#             value = value.strip().lower()
#             if value == 'true':
#                 return True
#             elif value == 'false':
#                 return False
#             else:
#                 raise serializers.ValidationError("Mark_as_Online must be either 'true' or 'false'.")

#         elif isinstance(value, bool):
#             return value

#         else:
#             raise serializers.ValidationError("Mark_as_Online must be either 'true' or 'false'.")
        
#     def validate_qualifying_criteria(self, value):
#         if value is None:
#             return 0
      
#         try:
#             value = int(value)
#             return value
#         except ValueError:
#             raise serializers.ValidationError("Qualifying criteria must be an integer value.")

#     def validate_bot_id(self, value):
#         if value is None:
#             return None
       
#         try:
#             value = int(value)
#             return value
#         except ValueError:
#             raise serializers.ValidationError("Bot id must be an integer value.")
    
# class JourneyEventsSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source='user.username', read_only=True)
#     application_name = serializers.CharField(source='application.application_name', read_only=True)

#     hiring_manager_ids = serializers.ListField(
#         child=serializers.IntegerField(), required=False, allow_null=True
#     )

#     hiring_manager_names = serializers.SerializerMethodField()

#     class Meta:
#         model = JourneyEvents
#         fields = '__all__'

#     def create(self, validated_data):
#         hiring_manager_ids = validated_data.pop('hiring_manager_ids', [])
#         journey_event = super().create(validated_data)
#         for manager_id in hiring_manager_ids:
#             JourneyEventHiringManager.objects.create(
#                 journey_event=journey_event,
#                 user_id=journey_event.user.id,
#                 hiring_manager_id=manager_id,
#                 application_id=journey_event.application.id
#             )
#         return journey_event

#     def get_hiring_manager_names(self, instance):
#         hiring_manager_ids = instance.journeyeventhiringmanager_set.values_list('hiring_manager_id', flat=True)
#         if hiring_manager_ids:
#             hiring_managers = User.objects.filter(id__in=hiring_manager_ids)
#             return list(hiring_managers.values('id', 'username'))
#         else:
#             return []


#     def to_representation(self, instance):
#         ret = super().to_representation(instance)
#         hiring_manager_ids = JourneyEventHiringManager.objects.filter(journey_event=instance).values_list('hiring_manager_id', flat=True)
#         ret['hiring_manager_ids'] = list(hiring_manager_ids)
#         ret['hiring_manager_names'] = self.get_hiring_manager_names(instance)
#         return ret


#     def validate(self, data):
#         interview_type = data.get('interview_type')

#         if not interview_type:
#             raise serializers.ValidationError({"interview_type": "This field is required."})

#         interview_type_normalized = interview_type.strip().lower()

#         if interview_type_normalized == 'bot call':
#             self.validate_bot_call(data)
#         elif interview_type_normalized == 'one on one':
#             self.validate_one_on_one(data)
#         elif interview_type_normalized == 'third party integration':
#             self.validate_third_party_integration(data)

#         if not data.get('immediately') and not data.get('relative_time_period_interval'):
#             raise serializers.ValidationError("Either 'immediately' or 'relative_time_period_interval' must be provided.")
#         if data.get('immediately') and data.get('relative_time_period_interval'):
#             raise serializers.ValidationError("Both 'immediately' and 'relative_time_period' cannot be provided together.")
        
#         if data.get('relative_time_period_interval') is not None and not data.get('relative_time_period_unit'):
#             raise serializers.ValidationError("relative_time_period_unit cannot be null if relative_time_period_interval is provided.")
        
#         return data



#     def validate_bot_call(self, data):
#         campaign_id = data.get('campaign').id
#         # Check if interview channel exists for this camapign when interview type is bot call
#         if self.one_on_one_exists_for_campaign(campaign_id):
#             raise serializers.ValidationError("Interview channel exists for this campaign.")
#         # Chec if call channel exists for the bot call
#         if not self.bot_call_exists_for_campaign(campaign_id):
#             raise serializers.ValidationError("call channel does not exist for this campaign.")
        
#         required_fields = ['bot_language', 'bot', 'campaign','segment_category']
#         self.check_required_fields(data, required_fields, 'Bot Call')

#     def validate_one_on_one(self, data):

#         campaign_id = data.get('campaign').id
#         hiring_manager_ids = data.get('hiring_manager_ids')


#         # Check if interview channel exists
#         interview_exists = self.one_on_one_exists_for_campaign(campaign_id)
#         if hiring_manager_ids and not interview_exists:
#             raise serializers.ValidationError("No interview channel exists for this campaign.")
#         # Check if interview channel exists but hiring_manager_ds are not provided
#         if interview_exists and not hiring_manager_ids: 
#             raise serializers.ValidationError({"hiring_manager_ids": "This field is required for 'One on one' interview type."})


#         # Check for call channel and bot_id requirement
#         if 'bot' in data and not self.bot_call_exists_for_campaign(campaign_id):
#             raise serializers.ValidationError("No call channel exists for this campaign.")

#         required_fields = ['campaign','segment_category']
#         mark_as_online = data.get('Mark_as_Online', False)

#         if not mark_as_online:
#             required_fields.extend(['state', 'city', 'addr1', 'addr2'])
#             self.check_required_fields(data, required_fields, 'One on one')
#         else:
#             for field in ['state', 'city', 'addr1', 'addr2']:
#                 if field in data and data[field] is not None:
#                     raise serializers.ValidationError({
#                         field: f"This field should be null when 'Mark_as_Online' is True for 'One on one' interview type."
#                     })

#     def validate_third_party_integration(self, data):
#         required_fields = ['test_type', 'qualifying_criteria', 'integration_type', 'close_link_within_interval', 'close_link_within_unit', 'campaign','segment_category']
#         self.check_required_fields(data, required_fields, 'Third Party integration')

#     def check_required_fields(self, data, required_fields, interview_type):
#         missing_fields = [field for field in required_fields if not data.get(field)]
#         if missing_fields:
#             raise serializers.ValidationError({
#                 field: f"This field is required for '{interview_type}' interview type." for field in missing_fields
#             })

#     def bot_call_exists_for_campaign(self, campaign_id):
#         campaign_events = CampaignEvent.objects.filter(campaign_id=campaign_id)
#         channel_ids = campaign_events.values_list('channel_id', flat=True)
#         campaign_channels = CampaignChannel.objects.filter(id__in=channel_ids)
#         return campaign_channels.filter(channel_root_name='call').exists()

#     def one_on_one_exists_for_campaign(self, campaign_id):
#         campaign_events = CampaignEvent.objects.filter(campaign_id=campaign_id)
#         channel_ids = campaign_events.values_list('channel_id', flat=True)
#         campaign_channels = CampaignChannel.objects.filter(id__in=channel_ids)
#         exists = campaign_channels.filter(channel_root_name='interview').exists()
#         return exists

    
#     def validate_immediately(self, value):
#         if isinstance(value, str):
#             value = value.strip().lower()
#             if value == 'true':
#                 return True
#             elif value == 'false':
#                 return False
#             else:
#                 raise serializers.ValidationError("immediately must be either 'true' or 'false'.")

#         elif isinstance(value, bool):
#             return value

#         else:
#             raise serializers.ValidationError("immediately must be either 'true' or 'false'.")

#     def validate_interview_type(self, value):
#         cleaned_value = bleach.clean(value, tags=[], attributes={}, strip=True)
#         if not re.match(r'^[a-zA-Z\s-]+$', cleaned_value):
#             raise serializers.ValidationError("Interview type should only contain alphabetic characters, spaces, and hyphens.")
#         return cleaned_value

#     def validate_string_field(self, value, field_name):
#         if value is None or value.strip() == '':
#             return None
#         if not isinstance(value, str):
#             raise serializers.ValidationError(f"{field_name} must be a string.")
        
#         cleaned_value = bleach.clean(value, tags=[], attributes={}, strip=True)
        
#         if not re.match(r'^[a-zA-Z0-9\s]+$', cleaned_value):
#             raise serializers.ValidationError(f"{field_name} should only contain alphanumeric characters and spaces.")
        
#         return cleaned_value

#     def validate_hiring_manager(self, value):
#         return self.validate_string_field(value, "hiring_manager")

#     def validate_integration_type(self, value):
#         return self.validate_string_field(value, "integration_type")

#     def validate_test_type(self, value):
#         return self.validate_string_field(value, "test_type")

#     def validate_state(self, value):
#         return self.validate_string_field(value, "state")

#     def validate_city(self, value):
#         return self.validate_string_field(value, "city")

#     def validate_addr1(self, value):
#         return self.validate_string_field(value, "addr1")

#     def validate_addr2(self, value):
#         return self.validate_string_field(value, "addr2")

#     def validate_skills(self, value):
#         return self.validate_string_field(value, "skills")

#     def validate_relative_time_period(self, value):
#         return self.validate_string_field(value, "relative_time_period")

#     def validate_Mark_as_Online(self, value):
#         if isinstance(value, str):
#             value = value.strip().lower()
#             if value == 'true':
#                 return True
#             elif value == 'false':
#                 return False
#             else:
#                 raise serializers.ValidationError("Mark_as_Online must be either 'true' or 'false'.")

#         elif isinstance(value, bool):
#             return value

#         else:
#             raise serializers.ValidationError("Mark_as_Online must be either 'true' or 'false'.")

#     def validate_qualifying_criteria(self, value):
#         if value is None:
#             return 0
      
#         try:
#             value = int(value)
#             return value
#         except ValueError:
#             raise serializers.ValidationError("Qualifying criteria must be an integer value.")

#     def validate_bot_id(self, value):
#         if value is None:
#             return None
       
#         try:
#             value = int(value)
#             return value
#         except ValueError:
#             raise serializers.ValidationError("Bot id must be an integer value.")



class JourneyEventsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    application_name = serializers.CharField(source='application.application_name', read_only=True)

    hiring_manager_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_null=True
    )

    hiring_manager_names = serializers.SerializerMethodField()

    class Meta:
        model = JourneyEvents
        fields = '__all__'

    def create(self, validated_data):
        hiring_manager_ids = validated_data.pop('hiring_manager_ids', [])
        journey_event = super().create(validated_data)
        for manager_id in hiring_manager_ids:
            JourneyEventHiringManager.objects.create(
                journey_event=journey_event,
                user_id=journey_event.user.id,
                hiring_manager_id=manager_id,
                application_id=journey_event.application.id,
            
            )
        return journey_event

    def get_hiring_manager_names(self, instance):
        hiring_manager_ids = instance.journeyeventhiringmanager_set.filter(is_deleted=False).values_list('hiring_manager_id', flat=True)
        # hiring_manager_ids = instance.journeyeventhiringmanager_set.values_list('hiring_manager_id' , flat=True)
        if hiring_manager_ids:
            hiring_managers = User.objects.filter(id__in=hiring_manager_ids)
            return list(hiring_managers.values('id', 'username'))
        else:
            return []

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        hiring_manager_ids = JourneyEventHiringManager.objects.filter(journey_event=instance,is_deleted=False).values_list('hiring_manager_id', flat=True)
        ret['hiring_manager_ids'] = list(hiring_manager_ids)
        ret['hiring_manager_names'] = self.get_hiring_manager_names(instance)
        return ret

    def validate(self, data):
        interview_type = data.get('interview_type')

        if not interview_type:
            raise serializers.ValidationError({"interview_type": "This field is required."})

        interview_type_normalized = interview_type.strip().lower()

        if interview_type_normalized == 'submit to panel':
            self.validate_submit_to_panel(data)
        elif interview_type_normalized == 'submit to client':
            self.validate_submit_to_client(data)
        elif interview_type_normalized == 'bot call':
            self.validate_bot_call(data)
        elif interview_type_normalized == 'one on one':
            self.validate_one_on_one(data)
        elif interview_type_normalized == 'book calendar':
            self.validate_book_calendar(data)
        elif interview_type_normalized == 'third party integration':
            self.validate_third_party_integration(data)
        elif interview_type_normalized == 'interview reminder':
            self.validate_interview_reminder(data)

        elif interview_type_normalized == 'assessment':
            self.validate_assessment(data)


        if not data.get('immediately') and not data.get('relative_time_period_interval'):
            raise serializers.ValidationError("Either 'immediately' or 'relative_time_period_interval' must be provided.")
        if data.get('immediately') and data.get('relative_time_period_interval'):
            raise serializers.ValidationError("Both 'immediately' and 'relative_time_period' cannot be provided together.")
        
        if data.get('relative_time_period_interval') is not None and not data.get('relative_time_period_unit'):
            raise serializers.ValidationError("relative_time_period_unit cannot be null if relative_time_period_interval is provided.")
        
        return data

    def validate_book_calendar(self, data):
        campaign_id = data.get('campaign').id
        hiring_manager_ids = data.get('hiring_manager_ids')
        bot=data.get('bot')
        
        Mark_as_Online = data.get('Mark_as_Online')
        # Check if interview channel exists
        interview_exists = self.one_on_one_exists_for_campaign(campaign_id)
        if hiring_manager_ids is not None and not interview_exists:
            raise serializers.ValidationError("No interview channel exists for this campaign.")
        
        # Check if interview channel exists but hiring_manager_ids are not provided
        if interview_exists and Mark_as_Online:
            if hiring_manager_ids is None:
                raise serializers.ValidationError({"hiring_manager_ids": "This field is required for 'Book Calendar'."})

        required_fields = ['campaign', 'segment_category']

        # Append meeting_title and meeting_duration if Mark_as_Online is True
        if Mark_as_Online:
            required_fields.extend(['meeting_title', 'meeting_duration'])

        # Check for call channel and bot_id requirement
        if bot is not None and not self.bot_call_exists_for_campaign(campaign_id):
            raise serializers.ValidationError("No call channel exists for this campaign.")
        
        
        self.check_required_fields(data, required_fields, 'Book Calendar')

    def validate_submit_to_panel(self, data):
        required_fields = ['qualifying_criteria', 'hiring_manager_ids']
        self.check_required_fields(data, required_fields, 'Submit to Panel')

    def validate_submit_to_client(self, data):
        required_fields = ['client']
        self.check_required_fields(data, required_fields, 'Submit to Client')
    
    def validate_interview_reminder(self, data):
        required_fields = ['segment_category']
        bot=data.get('bot')
        campaign_id = data.get('campaign').id


        if bot is not None and not self.bot_call_exists_for_campaign(campaign_id):
            raise serializers.ValidationError("No call channel exists for this campaign.")
        self.check_required_fields(data, required_fields, 'interview reminder')
    
    def validate_bot_call(self, data):
        campaign_id = data.get('campaign').id

        # Check if interview channel exists for this campaign when interview type is bot call
        if self.one_on_one_exists_for_campaign(campaign_id):
            raise serializers.ValidationError("Interview channel exists for this campaign.")
        
        # Check if call channel exists for the bot call
        if not self.bot_call_exists_for_campaign(campaign_id):
            raise serializers.ValidationError("Call channel does not exist for this campaign.")
        
        required_fields = ['bot_language', 'bot', 'campaign', 'segment_category']
        self.check_required_fields(data, required_fields, 'Bot Call')

    def validate_one_on_one(self, data):
        campaign_id = data.get('campaign').id
        hiring_manager_ids = data.get('hiring_manager_ids')
        bot=data.get('bot')
        # Check if interview channel exists
        interview_exists = self.one_on_one_exists_for_campaign(campaign_id)
        if hiring_manager_ids and not interview_exists:
            raise serializers.ValidationError("No interview channel exists for this campaign.")
        
        # Check if interview channel exists but hiring_manager_ids are not provided
        if interview_exists and not hiring_manager_ids: 
            raise serializers.ValidationError({"hiring_manager_ids": "This field is required for 'One on one' interview type."})

        # Check for call channel and bot_id requirement
        if bot is not None and not self.bot_call_exists_for_campaign(campaign_id):
            raise serializers.ValidationError("No call channel exists for this campaign.")
        
        required_fields = ['campaign', 'segment_category']
        self.check_required_fields(data, required_fields, 'One on one')

        mark_as_online = data.get('Mark_as_Online', False)
        if not mark_as_online:
            required_fields.extend(['state', 'city', 'addr1', 'addr2'])
            self.check_required_fields(data, required_fields, 'One on one')
        else:
            for field in ['state', 'city', 'addr1', 'addr2']:
                if field in data and data[field] is not None:
                    raise serializers.ValidationError({
                        field: f"This field should be null when 'Mark_as_Online' is True for 'One on one' interview type."
                    })

    def validate_third_party_integration(self, data):
        required_fields = ['test_type', 'qualifying_criteria', 'integration_type', 'close_link_within_interval', 'close_link_within_unit', 'campaign', 'segment_category']
        self.check_required_fields(data, required_fields, 'Third Party Integration')

    def validate_assessment(self, data):
        campaign_id = data.get('campaign').id
        bot = data.get('bot')
    
        # Check if assessment channel exists for this campaign
        if not self.assessment_channel_exists_for_campaign(campaign_id):
            raise serializers.ValidationError("No assessment channel exists for this campaign.")
    
        # Check for bot channel requirement
        if bot is not None and not self.bot_call_exists_for_campaign(campaign_id):
            raise serializers.ValidationError("No call channel exists for this campaign.")
    
        required_fields = ['segment_category', 'campaign', 'qualifying_criteria', 'assessment']
        self.check_required_fields(data, required_fields, 'Assessment')


    def check_required_fields(self, data, required_fields, interview_type):
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise serializers.ValidationError({
                field: f"This field is required for '{interview_type}' interview type." for field in missing_fields
            })

    def bot_call_exists_for_campaign(self, campaign_id):
        campaign_events = CampaignEvent.objects.filter(campaign_id=campaign_id)
        channel_ids = campaign_events.values_list('channel_id', flat=True)
        campaign_channels = CampaignChannel.objects.filter(id__in=channel_ids)
        return campaign_channels.filter(channel_root_name='call').exists()

    def one_on_one_exists_for_campaign(self, campaign_id):
        campaign_events = CampaignEvent.objects.filter(campaign_id=campaign_id)
        channel_ids = campaign_events.values_list('channel_id', flat=True)
        campaign_channels = CampaignChannel.objects.filter(id__in=channel_ids)
        exists = campaign_channels.filter(channel_root_name='interview').exists()
        return exists

    def assessment_channel_exists_for_campaign(self, campaign_id):
        campaign_events = CampaignEvent.objects.filter(campaign_id=campaign_id)
        channel_ids = campaign_events.values_list('channel_id', flat=True)
        campaign_channels = CampaignChannel.objects.filter(id__in=channel_ids)
        return campaign_channels.filter(channel_root_name='assessment').exists()


    def validate_immediately(self, value):
        if isinstance(value, str):
            value = value.strip().lower()
            if value == 'true':
                return True
            elif value == 'false':
                return False
            else:
                raise serializers.ValidationError("immediately must be either 'true' or 'false'.")

        elif isinstance(value, bool):
            return value

        else:
            raise serializers.ValidationError("immediately must be either 'true' or 'false'.")

    def validate_interview_type(self, value):
        cleaned_value = bleach.clean(value, tags=[], attributes={}, strip=True)
        if not re.match(r'^[a-zA-Z\s-]+$', cleaned_value):
            raise serializers.ValidationError("Interview type should only contain alphabetic characters, spaces, and hyphens.")
        return cleaned_value

    def validate_string_field(self, value, field_name):
        if value is None or value.strip() == '':
            return None
        if not isinstance(value, str):
            raise serializers.ValidationError(f"{field_name} must be a string.")
        
        cleaned_value = bleach.clean(value, tags=[], attributes={}, strip=True)
        
        if not re.match(r'^[a-zA-Z0-9\s]+$', cleaned_value):
            raise serializers.ValidationError(f"{field_name} should only contain alphanumeric characters and spaces.")
        
        return cleaned_value

    def validate_hiring_manager(self, value):
        return self.validate_string_field(value, "hiring_manager")

    def validate_integration_type(self, value):
        return self.validate_string_field(value, "integration_type")

    def validate_test_type(self, value):
        return self.validate_string_field(value, "test_type")

    def validate_state(self, value):
        return self.validate_string_field(value, "state")

    def validate_city(self, value):
        return self.validate_string_field(value, "city")

    def validate_addr1(self, value):
        return self.validate_string_field(value, "addr1")


class JobDashboardSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    status = serializers.CharField(max_length=45, required=False)

    def validate_status(self, value):
        if not value:
            return value
        if not CandidateStatuses.objects.filter(root_name=value).exists():
            raise serializers.ValidationError(f'Status "{value}" is not valid.')
        return value

class CandidateSerializer(serializers.Serializer):
    status_id = serializers.IntegerField()
    journey_id = serializers.IntegerField()
    journey_event_id = serializers.IntegerField()
    job_id = serializers.IntegerField()
    start_index = serializers.IntegerField(required=False, default=0)
    end_index = serializers.IntegerField(required=False, default=10)

    def validate_status_id(self, value):
        if not CandidateStatuses.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid status_id")
        return value

# serializers.py

from rest_framework import serializers
from .models import JobDetails, CandidateJourney, CampaignTriggers, AddToJobs, CampaignEvent, Calls

class JobDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDetails
        fields = '__all__'

class CandidateJourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateJourney
        fields = '__all__'

class CampaignTriggersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignTriggers
        fields = '__all__'

class AddToJobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddToJobs
        fields = '__all__'

class CampaignEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignEvent
        fields = '__all__'

class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calls 
        fields = '__all__'

        