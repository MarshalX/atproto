def get_or_create_model(data, model):
    # TODO(MarshalX): uncomment when models will be ready
    return data

    if isinstance(data, dict):
        # TODO(MarshalX): use dacite
        return model(**data)
    return data
