def at_least_one_field_required_validator(instance):
    if all(getattr(instance, field) is None for field in instance.model_fields):
        raise ValueError("At least one field_required.")
    return instance
