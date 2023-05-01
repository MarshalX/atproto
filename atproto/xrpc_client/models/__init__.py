from dacite import from_dict
from xrpc_client.models.data import *
from xrpc_client.models.params import *


def get_or_create_model(model_data, model):
    if isinstance(model_data, dict):
        return from_dict(model, model_data)
    return model_data
