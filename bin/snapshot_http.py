"""Read the selected local server; keep a failed request's address attached."""
import http.client
import urllib.error
import urllib.request


class SnapshotFailure(RuntimeError):
    pass


def read(port, path, body=None):
    url = 'http://127.0.0.1:' + str(port) + path
    method = 'GET' if body is None else 'POST'
    request = urllib.request.Request(url, data=body, method=method)
    # This socket belongs to our own child. An ambient HTTP proxy is not an
    # input to a snapshot, and must never turn it into an external request.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=120) as response:
            return response.read()
    except (OSError, http.client.HTTPException) as error:
        detail = str(error)
        if isinstance(error, urllib.error.HTTPError):
            try:
                detail += ': ' + error.read(1000).decode('utf-8', errors='replace')
            except (OSError, http.client.HTTPException) as body_error:
                detail += ': unreadable refusal body: ' + str(body_error)
        raise SnapshotFailure(method + ' ' + url + ': ' + type(error).__name__ + ': ' + detail) from None
