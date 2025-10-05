def image_base64_field_validator(value):
    extension_map = {"png": "png", "jpg": "jpg", "jpeg": "jpg", "gif": "gif"}
    if not value.startswith("data:image"):
        raise ValueError("The provided file is not recognized as an image.")

    try:
        header, base64_data = value.split(sep=";base64,", maxsplit=1)
    except ValueError:
        raise ValueError("Invalid image data format.")

    file_extension = extension_map.get(header.split("/")[-1])
    if not file_extension:
        raise ValueError("Only PNG, JPG, and GIF image formats are supported.")
    return value
