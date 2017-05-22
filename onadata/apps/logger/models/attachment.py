import os
import mimetypes

from hashlib import md5
from django.db import models

from instance import Instance
from datetime import datetime

def get_first_value(d,value,default=None):
    if isinstance(d,list):
        if value in d:
            return d[value]
        for k in d:
            if isinstance(d[k], list):
                for i in d[k]:
                    return get_first_value(i,value)
    return default

def upload_to(attachment, filename):
    instance = attachment.instance
    xform = instance.xform
    today = datetime.now().strftime("%Y-%m-%d")
    instance_date = get_first_value(instance.json, 'today',today)
    instance_date_path = os.path.join(instance_date[:7],instance_date) if len(instance_date)==10 else 'no_date'
    return os.path.join(
	get_first_value(instance.json,'swca_office','no_office'),
	get_first_value(instance.json,'project_number','no_project'),
        instance_date_path,
        xform.user.username,
        #'attachments',
        # xform.uuid or 'form',
        #instance.uuid or 'instance',
        os.path.split(filename)[1])


class Attachment(models.Model):
    instance = models.ForeignKey(Instance, related_name="attachments")
    media_file = models.FileField(upload_to=upload_to, max_length=380)
    mimetype = models.CharField(
        max_length=50, null=False, blank=True, default='')

    class Meta:
        app_label = 'logger'

    def save(self, *args, **kwargs):
        if self.media_file and self.mimetype == '':
            # guess mimetype
            mimetype, encoding = mimetypes.guess_type(self.media_file.name)
            if mimetype:
                self.mimetype = mimetype
        super(Attachment, self).save(*args, **kwargs)

    @property
    def file_hash(self):
        if self.media_file.storage.exists(self.media_file.name):
            return u'%s' % md5(self.media_file.read()).hexdigest()
        return u''

    @property
    def filename(self):
        return os.path.basename(self.media_file.name)
