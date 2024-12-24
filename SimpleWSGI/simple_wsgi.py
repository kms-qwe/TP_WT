def simple_app(environ, start_response):
    method = environ['REQUEST_METHOD']
    
    if method == 'GET':
        query_string = environ.get('QUERY_STRING', '')
        params = query_string.split('&')
        params = {p.split('=')[0]: p.split('=')[1] for p in params if '=' in p}
    elif method == 'POST':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
        params = {p.split('=')[0]: p.split('=')[1] for p in request_body.split('&') if '=' in p}
    else:
        params = {}

    body = f"Method: {method}\nParams: {params}".encode('utf-8')
    start_response('200 OK', [('Content-Type', 'text/plain'), ('Content-Length', str(len(body)))])
    return [body]
