def get_user_name(request):
    if "JIRA" in request.headers:
        return "Created by Jira"
    elif "api-key" in [header.lower() for header in list(request.headers)]:
        return "Created by Technical User"
    return f"{request.auth['name']} ({request.auth['sub']})"


def get_user_email(request):
    if "JIRA" in request.headers:
        return "jira@mail.com"
    return request.auth['email']
