from rest_framework.response import Response
from rest_framework import status


def success_response(
    data=None,
    status_code=status.HTTP_200_OK,
):
    """
    Returns a standard success response, formatted like Razorpay's success structure.
    """
    response_data = {
        "items": data if data is not None else {},
    }
    return Response(response_data, status=status_code)


def error_response(

    errors=None,
    status_code=status.HTTP_400_BAD_REQUEST,

):
    """
    Returns a standard error response, formatted like Razorpay's error structure.
    """
    error_details = {
        "code": "BAD_REQUEST_ERROR",
        "description": message,
        "field": None,  # You can specify which field the error relates to, if applicable
        "source": "customer",  # Default source, you can adjust based on context
        "step": "user_creation",  # Default step, adjust based on the operation
        "reason": "invalid_input",  # Customize reason as per error type
        "metadata": additional_metadata or {},  # Add extra metadata if needed
    }
    if errors:
        error_details["errors"] = errors
    return Response({"error": error_details}, status=status_code)
