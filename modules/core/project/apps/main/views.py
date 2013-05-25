from django.template import loader
import sys
from django import http
from django.template.context import Context
def nondefault_500_error(request, template_name='500nondefault.html'):
    """
    500 error handler for debug.

    Templates: `500.html`
    Context: sys.exc_info() results
     """
    t = loader.get_template(template_name) # You need to create a 500.html template.
    ltype,lvalue,ltraceback = sys.exc_info()
    sys.exc_clear() #for fun, and to point out I only -think- this hasn't happened at 
                    #this point in the process already
    return http.HttpResponseServerError(t.render(Context({'type':ltype,'value':lvalue,'traceback':ltraceback})))

