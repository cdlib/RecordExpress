import re

class ARKInvalid(ValueError):
    '''An ARK specific exception'''
    pass

def extract(string):
    '''Attempts to extract an ark from a string. Uses one regex then sends
    it to validate.
    '''
    try:
        ark = string[string.index('ark:/'):]
    except ValueError:
        raise ARKInvalid('Not an ark:/ string')
    return validate(ark)
    
def validate(string):
    '''Validates that a string is an ark. Throws an exception if not.
    Returns extracted ark with qualifire stripped, NAAN, NAME and Qualifier
    Raises ARKInvalid if not an ark

    >>> validate('x')
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid('No ARK label')
    ARKInvalid: No ARK label
    >>> validate('ark:/') 
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("A NAAN must be a 5 or 9 digit sequence.")
    ARKInvalid: A NAAN must be a 5 or 9 digit sequence.
    >>> validate('ark:/123456') 
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("A NAAN must be a 5 or 9 digit sequence.")
    ARKInvalid: A NAAN must be a 5 or 9 digit sequence.
    >>> validate('ark:/123456/') 
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("A NAAN must be 5 or 9 digits long")
    ARKInvalid: A NAAN must be 5 or 9 digits long
    >>> validate('ark:/12345/') 
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("No Name provided")
    ARKInvalid: No Name provided
    >>> validate('ark:/123456789/') 
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("No Name provided")
    ARKInvalid: No Name provided
    >>> validate('ark:/123456789/!') 
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("Illegal characters in ARK")
    ARKInvalid: Illegal characters in ARK
    >>> validate('ark:/123456789/swer kt101') 
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("Illegal characters in ARK")
    ARKInvalid: Illegal characters in ARK
    >>> validate('ark:/123456789/swerkt101/not valid') 
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("Illegal characters in ARK")
    ARKInvalid: Illegal characters in ARK
    >>> validate('ark:/123456789/----1---') 
    ('ark:/123456789/1', '123456789', '1', '')
    >>> validate('ark:/123456789/=') 
    ('ark:/123456789/=', '123456789', '=', '')
    >>> validate('ark:/123456789/#') 
    ('ark:/123456789/#', '123456789', '#', '')
    >>> validate('ark:/123456789/*') 
    ('ark:/123456789/*', '123456789', '*', '')
    >>> validate('ark:/123456789/+') 
    ('ark:/123456789/+', '123456789', '+', '')
    >>> validate('ark:/123456789/@') 
    ('ark:/123456789/@', '123456789', '@', '')
    >>> validate('ark:/123456789/_') 
    ('ark:/123456789/_', '123456789', '_', '')
    >>> validate('ark:/123456789/$') 
    ('ark:/123456789/$', '123456789', '$', '')
    >>> validate('ark:/123456789//') 
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("No Name provided")
    ARKInvalid: No Name provided
    >>> validate('ark:/123456789/.') 
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("No Name provided")
    ARKInvalid: No Name provided
    >>> validate('ark:/123456789/-------------') 
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("No Name provided")
    ARKInvalid: No Name provided
    >>> validate('ark:/123456789/-------------/qual')
    Traceback (most recent call last):
      File "ARK_validator.py", line 12, in validate
        raise ARKInvalid("No Name provided")
    ARKInvalid: No Name provided
    >>> validate('ark:/123456789/%') # should fail 
    ('ark:/123456789/%', '123456789', '%', '')
    >>> validate('ark:/123456789/%2') # should fail
    ('ark:/123456789/%2', '123456789', '%2', '')
    >>> validate('ark:/123456789/%25')  # not fail?, becomes just %
    ('ark:/123456789/%25', '123456789', '%25', '')
    >>> validate('ark:/123456789/1') 
    ('ark:/123456789/1', '123456789', '1', '')
    >>> validate('ark:/123456789/1/') 
    ('ark:/123456789/1', '123456789', '1', '')
    >>> validate('ark:/123456789/1.') 
    ('ark:/123456789/1.', '123456789', '1', '')
    >>> validate('ark:/123456789/--1--2/somequal') 
    ('ark:/123456789/12', '123456789', '12', 'somequal')
    '''
    if not string.find('ark:/') == 0:
        raise ARKInvalid('No ARK label')
    match = re.compile("ark:/(?P<NAAN>\d{5}|\d{9})/").match(string)
    if not match:
        num = re.compile("ark:/\d+/").match(string)
        if num:
            raise ARKInvalid("A NAAN must be 5 or 9 digits long")
        raise ARKInvalid("A NAAN must be a 5 or 9 digit sequence.")
    match = re.compile("ark:/(?P<NAAN>\d{5}|\d{9})/.+").match(string)
    if not match:
        raise ARKInvalid("No Name provided")
    match = re.compile("ark:/(?P<NAAN>\d{5}|\d{9})/([a-zA-Z0-9=#\*\+@_\$/%-\.]+)$").match(string)
    if not match:
        raise ARKInvalid("Illegal characters in ARK")
    grps = match.groups()
    NAAN = match.group('NAAN')
    if not NAAN:
        raise Exception
    name_and_qual = match.group(2)
    name = ''
    qualifier = ''
    # remove - from Name/Qualifier -- is insignificant for ARKS
    name_and_qual = name_and_qual.replace('-','')
    # split at first /
    # this will work for OAC ARKs, not sure in general
    parts = name_and_qual.split('/', 1)
    name = parts[0].rstrip('./')
    if len(name) == 0:
        raise ARKInvalid("No Name provided")
    if len(parts)==2:
        qualifier = parts[1].rstrip('./')
    #match = re.compile("([a-zA-Z0-9=#\*\+@_\$%-\.])").match(name_and_qual)
    return ''.join(('ark:/', NAAN, '/', name)), NAAN, name, qualifier

if __name__=="__main__":
    print "SELF TEST?"
    import doctest
    doctest.testmod()
