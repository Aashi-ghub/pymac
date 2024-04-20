#    Copyright (c) 2024 Rafal Wytrykus
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
Utility module for converting Python objects to JSON-serializable formats.
"""

from functools import singledispatch

_cant_serialize = object()


@singledispatch
def json_serializable(o, skip_underscore=False):
    """
    Recursively convert a Python object to a JSON-serializable format.

    Args:
        o (Any): The object to be converted.
        skip_underscore (bool, optional): If True, dictionary keys starting with an underscore ('_') are skipped.
            Defaults to False.

    Returns:
        Any: A JSON-serializable representation of the input object.

    Notes:
        - The function uses `singledispatch` to handle different types.
        - By default, types that are not explicitly handled will be ignored in the output.

    Examples:
        >>> json_serializable({'a': 1, '_b': 2}, skip_underscore=True)
        {'a': 1}
    """
    # Default handler for types without a specific registration.
    return _cant_serialize


@json_serializable.register(dict)
def _handle_dict(d, skip_underscore=False):
    """
    Handle conversion of dictionaries to JSON-serializable formats.

    Args:
        d (dict): The dictionary to be converted.
        skip_underscore (bool, optional): If True, keys starting with an underscore are skipped.
            Defaults to False.

    Returns:
        dict: A JSON-serializable dictionary with keys converted to strings and values processed recursively.
    """
    converted = ((str(k), json_serializable(v, skip_underscore)) for k, v in d.items())
    if skip_underscore:
        converted = ((k, v) for k, v in converted if k[:1] != "_")
    return {k: v for k, v in converted if v is not _cant_serialize}


@json_serializable.register(list)
@json_serializable.register(tuple)
def _handle_sequence(seq, skip_underscore=False):
    """
    Handle conversion of lists and tuples to JSON-serializable formats.

    Args:
        seq (list or tuple): The sequence to be converted.
        skip_underscore (bool, optional): Ignored for sequences.
            Defaults to False.

    Returns:
        list: A JSON-serializable list with elements processed recursively.

    Notes:
        - Elements that cannot be serialized are omitted from the result.
    """
    converted = (json_serializable(v, skip_underscore) for v in seq)
    return [v for v in converted if v is not _cant_serialize]


@json_serializable.register(int)
@json_serializable.register(float)
@json_serializable.register(str)
@json_serializable.register(bool)
@json_serializable.register(type(None))
def _handle_default_scalar_types(value, skip_underscore=False):
    """
    Handle scalar types that are inherently JSON serializable.

    Args:
        value (int, float, str, bool, or None): The scalar value to be returned.
        skip_underscore (bool, optional): Ignored for scalar types.
            Defaults to False.

    Returns:
        int, float, str, bool, or None: The input value unchanged.
    """
    return value
