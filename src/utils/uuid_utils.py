import uuid


def uuid_to_short_form(uuid_value: uuid):
    # todo remove this method when db tables are set to use uuid as keys
    """
    returns the last 12 characters of string format of a uuid
    """
    return str(uuid_value)[24:36]
