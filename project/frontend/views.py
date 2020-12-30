import json
import os

from data.models import Data
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from frontend.IR.tf_idf import (get_data_train, get_data_train_from_database,
                                get_relevant_ranking_for_query,
                                get_text_from_file)

# Create your views here.


class Index(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.INPUT_ROOT = os.path.abspath(os.path.dirname(__file__))

    def get(self, request):
        return render(request, "frontend/index.html")

    def post(self, request, *args, **kwargs):
        if request.method == "POST" and request.is_ajax():
            query = request.POST['query']
            use = request.POST['use']
            if use == "search":
                tf_idf_index, docs_length, arr_file = get_data_train()
                answers = get_relevant_ranking_for_query(
                    query,
                    tf_idf_index,
                    docs_length,
                    arr_file
                )

                convertAnswer = dict()
                input_path = os.path.join(
                    self.INPUT_ROOT, "IR", "input", "Cranfield")
                for i in answers:
                    # name = arr_file[int(i)]
                    filename = os.path.join(input_path, i + ".txt")
                    text = get_text_from_file(filename)
                    convertAnswer[i] = text
                answerJson = json.dumps(convertAnswer)
                return JsonResponse({'content': answerJson}, status=200)
            elif use == "reTrain":
                # delete datatrain
                file_path = os.path.join(self.INPUT_ROOT, "IR", 'input',
                                         'data', 'inverted.pickle')
                if os.path.exists(file_path):
                    os.remove(file_path)

                file_path = os.path.join(self.INPUT_ROOT, "IR", 'input',
                                         'data', 'index.pickle')
                if os.path.exists(file_path):
                    os.remove(file_path)

                _, _, _ = get_data_train_from_database()
                return JsonResponse({'content': {}}, status=200)
            elif use == "search_in_database":
                tf_idf_index, docs_length, arr_file = get_data_train_from_database()
                answers = get_relevant_ranking_for_query(
                    query,
                    tf_idf_index,
                    docs_length,
                    arr_file
                )
                convertAnswer = dict()
                for i in answers:
                    text = Data.objects.get(id=int(arr_file[i-1])).text
                    convertAnswer[i] = text
                answerJson = json.dumps(convertAnswer)
                return JsonResponse({'content': answerJson}, status=200)
