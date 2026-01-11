import re

def evaluate(contents, lastname=None):
    CERTIFICATION_ASSISTANCE = "I CERTIFY THAT I HAVE COMPLETELY DOCUMENTED ALL SOURCES THAT I USED TO COMPLETE THIS ASSIGNMENT"
    CERTIFICATION_NO_ASSISTANCE = "I CERTIFY THAT I DID NOT USE ANY SOURCES OR RECEIVE ANY ASSISTANCE REQUIRING DOCUMENTATION WHILE COMPLETING THIS ASSIGNMENT"

    callouts = []

    lines = contents.splitlines()

    certification_line = None
    for line_num, line in enumerate(lines, start=1):
        if "I CERTIFY THAT" in line:
            certification_line = line
            break

    if not certification_line:
        callouts.append(('important', "Missing certification statement."))
        return callouts

    if CERTIFICATION_ASSISTANCE in contents and CERTIFICATION_NO_ASSISTANCE in contents:
        callouts.append(('important', "Found both certification statements."))

    elif CERTIFICATION_ASSISTANCE not in contents and CERTIFICATION_NO_ASSISTANCE not in contents:
        callouts.append(('important', "Certification statement has been modified."))

    before_certification = certification_line.split("I CERTIFY THAT")[
        0].strip()

    # initialsFromDaaw = re.findall(r'[A-Za-z]', before_certification)
    # initialsFromStudentName = [x[0].upper() for x in studentName.split('-')[:-1]]
    # for i in initialsFromStudentName:
    #     if i not in initialsFromDaaw:
    #         expected = ''.join(initialsFromStudentName)
    #         found = ''.join(initialsFromDaaw)
    #         callouts.append(('warning', f"Initials not found in statement. Expected: `{expected}`, Found: `{found}`"))
    #         break

    # ensure that last line contains the last name
    lastline = contents.splitlines()[-1]
    lastline = re.sub(r'[^a-zA-Z]', '', lastline).lower()
    if lastname and lastname.lower() not in lastline:
        callouts.append(('important', f"Last name not found in signature. Expected: `{lastname}`, Found: `{lastline}`"))

    return callouts