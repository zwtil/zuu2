import typing as _typing


def _traverse(obj: _typing.Union[dict, list, set, tuple], keys, create_missing=False):
    """
    Traverse a nested object using a sequence of keys.

    Args:
        obj (typing.Union[dict, list, set, tuple]): The nested object to traverse.
        keys (list): The sequence of keys to access the desired value.
        create_missing (bool): Whether to create missing intermediate keys.

    Returns:
        The nested object at the end of the traversal.
    """
    curr = obj
    for key in keys:
        if isinstance(curr, dict):
            if create_missing and key not in curr:
                curr[key] = {}
            curr = curr.get(key)
            if curr is None:
                raise KeyError(f"Key {key} not found in dictionary")
        elif isinstance(curr, list):
            key = int(key)
            if create_missing and key >= len(curr):
                curr.extend([{}] * (key - len(curr) + 1))
            try:
                curr = curr[key]
            except IndexError:
                raise KeyError(f"Index {key} out of range for list")
        elif isinstance(curr, (set, tuple)):
            try:
                curr = list(curr)[int(key)]
            except IndexError:
                raise KeyError(f"Index {key} out of range for set/tuple")
        else:
            try:
                curr = getattr(curr, key)
            except AttributeError:
                raise KeyError(f"Attribute {key} not found")
    return curr


def get_deep(obj: _typing.Union[dict, list, set, tuple], *keys):
    """
    Get a value from a nested object using a sequence of keys.

    Args:
        obj (typing.Union[dict, list, set, tuple]): The nested object to retrieve the value from.
        *keys: The sequence of keys to access the desired value.

    Returns:
        typing.Any: The value retrieved from the nested object.
    """
    return _traverse(obj, keys)


def set_deep(obj: _typing.Union[dict, list, set, tuple], *keys, value):
    """
    Set a value in a nested object using a sequence of keys.

    Args:
        obj (typing.Union[dict, list, set, tuple]): The nested object to set the value in.
        *keys: The sequence of keys to access the desired location for setting the value.
        value: The value to be set in the nested object.

    Returns:
        None
    """
    *initial_keys, final_key = keys
    curr = _traverse(obj, initial_keys, create_missing=True)
    if isinstance(curr, dict):
        curr[final_key] = value
    elif isinstance(curr, list):
        final_key = int(final_key)
        if final_key >= len(curr):
            curr.extend([None] * (final_key - len(curr) + 1))
        curr[final_key] = value
    else:
        setattr(curr, final_key, value)


def del_deep(obj: _typing.Union[dict, list, set, tuple], *keys):
    """
    Delete a value in a nested object using a sequence of keys.

    Args:
        obj (typing.Union[dict, list, set, tuple]): The nested object to delete the value from.
        *keys: The sequence of keys to access the desired location for deleting the value.

    Returns:
        None
    """
    *initial_keys, final_key = keys
    curr = _traverse(obj, initial_keys)
    if isinstance(curr, dict):
        del curr[final_key]
    elif isinstance(curr, list):
        del curr[int(final_key)]
    else:
        delattr(curr, final_key)


def set_default_deep(
    obj: _typing.Union[dict, list, set, tuple], *keys, value, fillpadding=False
):
    """
    Set a value in a nested object using a sequence of keys. If the keys do not exist, they are created.

    Args:
        obj (typing.Union[dict, list, set, tuple]): The nested object to set the value in.
        *keys: The sequence of keys to access the desired location for setting the value.
        value: The value to be set in the nested object.
        fillpadding (bool, optional): If True, and the last key is an index that is beyond the length of the current list,
            the list is padded with None values to make space for the new value. Defaults to False.

    Returns:
        None
    """
    *initial_keys, final_key = keys
    curr = _traverse(obj, initial_keys, create_missing=True)

    if isinstance(curr, set):
        raise IndexError("set does not support default value")

    if isinstance(curr, dict):
        if final_key not in curr:
            curr[final_key] = value
    elif isinstance(curr, list):
        final_key = int(final_key)
        if final_key >= len(curr):
            if fillpadding:
                curr.extend([None] * (final_key - len(curr) + 1))
            else:
                raise IndexError(f"Index {final_key} out of range for list")
        curr[final_key] = value
    else:
        if not hasattr(curr, final_key):
            setattr(curr, final_key, value)
