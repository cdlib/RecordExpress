#Utility function to determine if we are running on OAC or not

def is_OAC():
    OAC = False
    try:
        from oac.models import Institution
        OAC = True
    except ImportError:
        pass
    return OAC
