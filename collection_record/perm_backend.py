OAC = False
try:
    from oac.models import Institution
    from oac.models import get_institutions_for_user
    OAC = True
except ImportError:
    from collection_record.models import PublishingInstitution
    pass

if not OAC:
    class CollectionRecordPermissionBackend(object):
        '''Reject all requests if not in OAC.
        3rd Party user will need to implement an appropriate backend object
        '''
        supports_object_permissions = True
        supports_anonymous_user = True
        supports_inactive_user = False

        def authenticate(self, username, password):
            return None

        def has_perm(self, user_obj, perm, obj=None):
            if user_obj.is_superuser:
                return True
            if obj is None:
                return False
            if user_obj.is_authenticated():
                return True
            return True #allow all users to edit all

    def get_publishing_institutions_for_user(user):
        '''Return the publishing institutions for the given user
        '''
        #TODO: Do we want user_profile with linked insts?
        return PublishingInstitution.objects.all()

else:
    class CollectionRecordPermissionBackend(object):
        '''If user is in a group that is associated with the publishing
        institution, allow edits and creation of ColllectionRecords for that 
        institution.
        '''
        supports_object_permissions = True
        supports_anonymous_user = True
        supports_inactive_user = False

        def authenticate(self, username, password):
            return None

        def has_perm(self, user_obj, perm, obj=None):
            if not user_obj.is_authenticated():
                return False
            if obj is None:
                return False
            if user_obj.is_superuser:
                return True
            publisher = getattr(obj, 'publisher', None)
            if publisher and isinstance(publisher, Institution):
                groups = [prof.group for prof in publisher.groupprofile_set.all()]
                for grp in groups:
                    if user_obj in grp.user_set.all():
                        return True
            return False


    def get_publishing_institutions_for_user(user):
        '''Return the publishing institutions for the given user
        '''
        insts = get_institutions_for_user(user) 
        return [i for i in insts if not i.isa_campus]
