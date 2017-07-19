import json

from boto.s3.connection import S3Connection

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from .utils import create_upload_data


def HttpResponseJsonError(error_message, status=400):
    return HttpResponse(
        json.dumps({'error': error_message}),
        content_type="application/json",
        status=status
    )


def _filename(key, filename):
    if hasattr(key, '__call__'):
        return key(filename)
    elif key == '/':
        return '${filename}'
    else:
        # The literal string '${filename}' is an S3 field variable for key.
        # https://aws.amazon.com/articles/1434#aws-table
        return '%s/${filename}' % key


@require_POST
def get_upload_params(request):
    content_type = request.POST['type']
    filename = request.POST['name']
    try:
        dest = settings.S3UPLOAD_DESTINATIONS[request.POST['dest']]
    except KeyError:
        return HttpResponseJsonError('File destination does not exist.')
    else:
        key = dest.get('key')
        auth = dest.get('auth')
        allowed = dest.get('allowed')
        acl = dest.get('acl', 'public-read')
        bucket = dest.get('bucket')
        cache_control = dest.get('cache_control')
        content_disposition = dest.get('content_disposition')
        content_length_range = dest.get('content_length_range')
        server_side_encryption = dest.get('server_side_encryption')

    if not key:
        return HttpResponseJsonError('Missing destination path.', status=403)

    if auth and not auth(request.user):
        return HttpResponseJsonError('Permission denied.', status=403)

    if (allowed and content_type not in allowed) and allowed != '*':
        return HttpResponseJsonError('Invalid file type (%s).' % content_type)

    key = _filename(key, filename)
    access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
    secret_access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
    token = None

    data = create_upload_data(
        content_type, key, acl, bucket, cache_control, content_disposition,
        content_length_range, server_side_encryption, access_key, secret_access_key, token
    )

    url = None

    # Generate signed URL for private document access
    if acl == "private":
        c = S3Connection(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY
        )
        url = c.generate_url(
            expires_in=int(5 * 60),  # 5 mins
            method='GET',
            bucket=bucket or settings.AWS_STORAGE_BUCKET_NAME,
            key=key.replace("${filename}", filename),
            query_auth=True,
            force_http=True
        )

    response = {
        "aws_payload": data,
        "private_access_url": url,
    }

    return HttpResponse(json.dumps(response), content_type="application/json")
