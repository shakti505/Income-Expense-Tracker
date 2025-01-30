# from rest_framework.response import Response
# from rest_framework import status


# def success_response(data=None, status_code=status.HTTP_200_OK):
#     """
#     Returns a standard success response for multiple items or lists.
#     """
#     response_data = {
#         "items": data if data is not None else {},
#     }
#     return Response(response_data, status=status_code)


# def success_single_response(data=None, status_code=status.HTTP_200_OK):
#     """
#     Returns a success response for a single item or object.
#     """
#     response_data = {
#         "item": data if data is not None else {},
#     }
#     return Response(response_data, status=status_code)


# def validation_error_response(serializer, status_code=status.HTTP_400_BAD_REQUEST):
#     """
#     Returns a standardized error response for serializer validation errors.
#     Transforms serializer.errors into a key-value pair format.
#     """
#     errors = {}
#     for field, error in serializer.errors.items():
#         errors[field] = " ".join(errors) if isinstance(error, list) else str(error)

#     return Response(
#         {"error": error},
#         status=status_code,
#     )


# def not_found_error_response(detail="Not found", status_code=status.HTTP_404_NOT_FOUND):
#     """
#     Returns a standardized 'not found' error response.
#     """

#     return Response(
#         {"error": detail},
#         status=status_code,
#     )


# def permission_error_response(
#     detail="You do not have permission to perform this action.",
#     status_code=status.HTTP_404_NOT_FOUND,
# ):
#     """
#     Returns a response when the user does not have permission to perform an action.
#     """
#     return Response(
#         {"error": detail},
#         status=status_code,
#     )


# def internal_server_error_response(
#     detail="Internal server error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
# ):
#     """
#     Returns a response for any internal server error that occurs.
#     """
#     return Response(
#         {"error": detail},
#         status=status_code,
#     )


# def success_no_content_response(status_code=status.HTTP_204_NO_CONTENT):
#     """
#     Returns a success response with no content (typically used after a delete operation).
#     """
#     return Response(status=status_code)

from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, status_code=status.HTTP_200_OK):
    """
    Returns a standard success response for multiple items or lists.
    """
    response_data = {

        "data": data if data is not None else {}
    }
    return Response(response_data, status=status_code)


def success_single_response(data=None, status_code=status.HTTP_200_OK):
    """
    Returns a success response for a single item or object.
    """
    response_data = {

        "data": data if data is not None else {}
    }
    return Response(response_data, status=status_code)


def validation_error_response(errors, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Returns a standardized error response for validation errors.
    Converts error messages to simple strings instead of arrays.
    """
    if hasattr(errors, 'get_full_details'):
        # If it's a serializer errors object
        error_dict = {}
        for field, error_list in errors.items():
            # Take the first error message for each field
            if isinstance(error_list, list):
                error_dict[field] = error_list[0] if error_list else ''
            elif isinstance(error_list, dict):
                # Handle nested serializer errors
                nested_errors = error_list.get('message', error_list)
                if isinstance(nested_errors, list):
                    error_dict[field] = nested_errors[0]
                else:
                    error_dict[field] = str(nested_errors)
            else:
                error_dict[field] = str(error_list)
    else:
        # If it's already a dictionary
        error_dict = {
            field: error[0] if isinstance(error, list) else str(error)
            for field, error in errors.items()
        }

    response_data = {

        "errors": error_dict
    }
    
    return Response(response_data, status=status_code)


def not_found_error_response(detail="Not found", status_code=status.HTTP_404_NOT_FOUND):
    """
    Returns a standardized 'not found' error response.
    """
    response_data = {

        "errors": {
            "detail": detail
        }
    }
    return Response(response_data, status=status_code)


def permission_error_response(
    detail="You do not have permission to perform this action.",
    status_code=status.HTTP_403_FORBIDDEN
):
    """
    Returns a response when the user does not have permission to perform an action.
    """
    response_data = {

        "errors": {
            "detail": detail
        }
    }
    return Response(response_data, status=status_code)


def internal_server_error_response(
    detail="Internal server error", 
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
):
    """
    Returns a response for any internal server error that occurs.
    """
    response_data = {

        "errors": {
            "detail": detail
        }
    }
    return Response(response_data, status=status_code)


def success_no_content_response(status_code=status.HTTP_204_NO_CONTENT):
    """
    Returns a success response with no content (typically used after a delete operation).
    """
    return Response(status=status_code)