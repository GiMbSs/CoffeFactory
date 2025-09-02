# Core exceptions for coffee_factory project
"""
Custom exception handlers for standardized API error responses.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides standardized error responses.
    
    Returns standardized error format:
    {
        "error": {
            "code": "error_code",
            "message": "Human readable message",
            "details": {...}
        }
    }
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the exception
        logger.error(f"API Exception: {exc}", exc_info=True)
        
        # Determine error code based on status
        error_code = get_error_code(response.status_code)
        
        # Get original error data
        original_data = response.data
        
        # Create standardized error response
        custom_response_data = {
            'error': {
                'code': error_code,
                'message': get_error_message(response.status_code, original_data),
                'details': format_error_details(original_data)
            }
        }
        
        response.data = custom_response_data
    
    return response


def get_error_code(status_code):
    """Get standardized error code based on HTTP status."""
    error_codes = {
        400: 'validation_error',
        401: 'authentication_required',
        403: 'permission_denied',
        404: 'not_found',
        405: 'method_not_allowed',
        406: 'not_acceptable',
        409: 'conflict',
        422: 'unprocessable_entity',
        429: 'too_many_requests',
        500: 'internal_server_error',
        502: 'bad_gateway',
        503: 'service_unavailable',
    }
    return error_codes.get(status_code, 'unknown_error')


def get_error_message(status_code, original_data):
    """Get human-readable error message."""
    if status_code == 400:
        return "Dados inválidos fornecidos"
    elif status_code == 401:
        return "Autenticação necessária"
    elif status_code == 403:
        return "Permissão negada"
    elif status_code == 404:
        return "Recurso não encontrado"
    elif status_code == 405:
        return "Método não permitido"
    elif status_code == 409:
        return "Conflito de dados"
    elif status_code == 422:
        return "Entidade não processável"
    elif status_code == 429:
        return "Muitas requisições"
    elif status_code >= 500:
        return "Erro interno do servidor"
    else:
        # Try to extract message from original data
        if isinstance(original_data, dict):
            if 'detail' in original_data:
                return str(original_data['detail'])
            elif 'message' in original_data:
                return str(original_data['message'])
        
        return "Erro desconhecido"


def format_error_details(original_data):
    """Format error details from original data."""
    if isinstance(original_data, dict):
        # Remove 'detail' and 'message' as they're in main message
        details = original_data.copy()
        details.pop('detail', None)
        details.pop('message', None)
        return details if details else {}
    elif isinstance(original_data, list):
        return {'errors': original_data}
    else:
        return {'raw': str(original_data)}
