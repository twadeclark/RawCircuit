import requests


class HuggingfaceModelSearch:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.model_list = {}

    def fetch_next_model_name_from_huggingface(self):
        # we check db first and grab a model if we can
        models_with_none_success = self.db_manager.get_models_with_none_success()
        if models_with_none_success:
            ret_val = models_with_none_success[0][0]
            return ret_val

        # if none in the db, we get the first page of the huggingface api results
        response = requests.get(
                                "https://huggingface.co/api/models",
                                params={"filter"    : "text-generation",
                                        "sort"      : "likes",
                                        "direction" : "-1",
                                        "limit"     : "10",
                                        "full"      : "False",
                                        "config"    : "False"},
                                headers={},
                                timeout=120
                                )
        next_url_link = self._insert_models_into_database_then_return_next_url_link(response)

        # check the db again for a model
        models_with_none_success = self.db_manager.get_models_with_none_success()
        if models_with_none_success:
            ret_val = models_with_none_success[0][0]
            return ret_val

        while next_url_link:
            response = requests.get(
                                    next_url_link,
                                    headers={},
                                    timeout=120
                                    )
            next_url_link = self._insert_models_into_database_then_return_next_url_link(response)

            # check the db again for a model
            models_with_none_success = self.db_manager.get_models_with_none_success()
            if models_with_none_success:
                ret_val = models_with_none_success[0][0]
                return ret_val

        return None # no new models found!

    def only_insert_model_into_database_if_not_already_there(self, model_name):
        rows = self.db_manager.get_model_name_list_by_list_of_model_names([model_name])
        if len(rows) == 0:
            self.db_manager.insert_model_record(model_name)

    def update_model_record(self, model_name, success, disposition):
        self.db_manager.update_model_record(model_name, success, disposition)

    def _insert_models_into_database_then_return_next_url_link(self, response):
        list_of_id_from_response = [model["id"] for model in response.json()] # id is the model_name from huggingface
        rows = self.db_manager.get_model_name_list_by_list_of_model_names(list_of_id_from_response)
        for model in response.json():
            if model["id"] not in [item for sublist in rows for item in sublist]:
                self.db_manager.insert_model_record(model["id"])
        next_url_link = response.links['next']['url'] or ""
        return next_url_link
