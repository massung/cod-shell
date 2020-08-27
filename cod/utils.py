import os.path
import re


def cap_case_str(s):
    """
    Translate a string like "foo_Bar-baz  whee" and return "FooBarBazWhee".
    """
    return re.sub(r'(?:[_\-\s]+|^)(.)', lambda m: m.group(1).upper(), s)


def cap_case_filename(f):
    """
    Translate a filename into a CapCaseString.
    """
    return cap_case_str(os.path.basename(f))
