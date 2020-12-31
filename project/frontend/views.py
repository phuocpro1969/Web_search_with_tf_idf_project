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
        self.tf_idf_index, self.docs_length, self.arr_file = get_data_train_from_database()

    def get(self, request):
        return render(request, "frontend/index.html")

    def post(self, request, *args, **kwargs):
        if request.method == "POST" and request.is_ajax():
            query = request.POST['query']
            use = request.POST['use']
            if use == "reTrain":
                # delete datatrain
                file_path = os.path.join(self.INPUT_ROOT, "IR", 'input',
                                         'data', 'inverted.pickle')
                if os.path.exists(file_path):
                    os.remove(file_path)

                file_path = os.path.join(self.INPUT_ROOT, "IR", 'input',
                                         'data', 'index.pickle')
                if os.path.exists(file_path):
                    os.remove(file_path)

                self.tf_idf_index, self.docs_length, self.arr_file = get_data_train_from_database()
                return JsonResponse({'content': {}}, status=200)
            elif use == "search_in_database":
                x_retrieved = get_relevant_ranking_for_query(
                    query,
                    self.tf_idf_index,
                    self.docs_length,
                    self.arr_file
                )

                answer = {
                    keys: [
                        self.arr_file[int(values[0])],
                        Data.objects.get(
                            id=int(self.arr_file[int(values[0])])).text,
                        str(values[1])
                    ] for keys, values in enumerate(x_retrieved)
                }
                answerJson = json.dumps(answer)
                return JsonResponse({'content': answerJson}, status=200)
