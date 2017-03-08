import os
import mimetypes

from hashlib import md5
from django.db import models

from instance import Instance

def get_first_value(d,value,default):
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
    instance_date = get_first_value(instance.json, 'today', None)
    if not instance_date:
        instance_time = get_first_value(instance.json, 'submission_time', None)
        instance_date = instance_time[:10] if (instance_time and len(instance_time)>10) else None
    instance_month = instance_date[:7] if len(instance_date)==10 else None
    #if instance_date and instance_month:
    #    final_date = os.path.join(instance_month,instance_date)
    #else:
    #    final_date = 'no_date'
    return os.path.join(
	get_first_value(instance.json,'swca_office','no_office'),
	get_first_value(instance.json,'project_number','no_project'),
        instance_month,
        instance_date,
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
