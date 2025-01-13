from django.shortcuts import render
from rest_framework.response import Response

# THE PURPOSE OF THIS FILE IS TO HELP ADD LOGGING TO YOUR BACKEND:

# 1. IMPORT THE LOGGING LIBRARY TO YOUR FILE
import logging

# 2. FETCH THE LOGGER FROM SETTINGS.PY FILE
logger = logging.getLogger('WarehousePilot_app')

# WHEN LOGGING, CHOOSE TO LOG BASED ON THE SEVERITY:
"""
    info: use for writing debugging messages that you want to print to the terminal (ie. instead of print statements to the terminal)
          OR
          use for writing actions that have occurred like successful states (ie. login successful)
    warning: use for if something may go wrong, but no error has occurred
    error: use for writing error messages
    critical: use for when a crtitical issue occurs (something that could take the product down)
"""
# 3. WRITE YOUR LOG MESSAGE AND CHOOSE THE CORRECT SEVERITY BASED ON THE COMMENT ABOVE
def logging_example_view(request):
    try:
        # view logic being done
        logger.info("An action has occurred successfully") # INFO LEVEL LOG
        return Response({"message": "Success"})
    except Exception as e:
        logger.error("An error occurred: %s", str(e), exc_info=True) # LOGGING AN ERROR
        return Response({"message": "Error"}, status=500)