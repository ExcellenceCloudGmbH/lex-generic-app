from django.apps import apps
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from django.http import JsonResponse
from lex_app.settings import repo_name

class CleanCalculations(APIView):
    http_method_names = ['post']
    permission_classes = [HasAPIKey | IsAuthenticated]
    def post(self, request, *args, **kwargs):
        will_be_cleaned = []

        for entry in request.data["records"]:
            # Parse JSON and extract the model name and record ID
            model_class = apps.get_model(repo_name, entry['model'])

            try:
                obj = model_class.objects.get(pk=entry['record_id'])

                if hasattr(obj, 'calculate') and not obj.calculate:
                    will_be_cleaned.append(f"{entry['model']}_{entry['record_id']}")

            except Exception as e:
                will_be_cleaned.append(f"{entry['model']}_{entry['record_id']}")

        return JsonResponse({"records": will_be_cleaned})
