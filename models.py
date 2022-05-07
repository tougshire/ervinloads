from django.db import models
from django.conf import settings
from datetime import datetime

class Location(models.Model):
    name = models.CharField(
        max_length=80,
        help_text = 'The status of the load'
    )
    is_default = models.BooleanField(
        'is default',
        default = False,
        help_text = 'If this is the default location for new loads (Only one will used even if more than one is selected)'
    )
    class Meta:
        ordering=('-is_default', 'name',)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(
        max_length=150,
        help_text = 'The supplier\'s name'
    )
    details = models.TextField(
        'details',
        blank=True,
        help_text='Any details such as contact info'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

class Completion(models.Model):
    name = models.CharField(
        max_length=50,
        help_text = 'The status of the load'
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank = True,
        help_text = 'The recipients of notices for when a load changes to this status'
    )
    rank = models.IntegerField(
        'rank',
        default=1000,
        help_text='The order that this status should display in a list of statuses'
    )
    is_active = models.BooleanField(
        'is active',
        default = False,
        help_text = 'If this status is for an active load (one that is not yet complete or canceled and should be displayed in the default list)'
    )
    is_default = models.BooleanField(
        'is default',
        default = False,
        help_text = 'If this is the default status for new loads (Only one will used even if more than one is selected)'
    )

    class Meta:
        ordering=('-is_default', 'rank', 'name',)

    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(
        max_length=50,
        help_text = 'The status of the load'
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank = True,
        help_text = 'The recipients of notices for when a load changes to this status'
    )
    rank = models.IntegerField(
        'rank',
        default=1000,
        help_text='The order that this status should display in a list of statuses'
    )
    is_active = models.BooleanField(
        'is active',
        default = False,
        help_text = 'If this status is for an active load (one that is not yet complete or canceled and should be displayed in the default list)'
    )
    is_default = models.BooleanField(
        'is default',
        default = False,
        help_text = 'If this is the default status for new loads (Only one will used even if more than one is selected)'
    )

    class Meta:
        ordering=('-is_default', 'rank', 'name',)

    def __str__(self):
        return self.name

class NotificationGroup(models.Model):
    name = models.CharField(
        'name',
        max_length=80,
        help_text = 'The name of this notification group'
    )
    email_addresses = models.TextField(
        'email addresses',
        blank=True,
        help_text = 'Send to the following email addresses(comma or semicolon separated)'
    )
    is_default = models.BooleanField(
        'is_default',
        default = False,
        help_text = 'If this is a default notification group for new loads'
    )

    class Meta:
        ordering=('-is_default', 'name')

    def __str__(self):
        return self.name

class LoadsNotDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_when__isnull=True)

class Load(models.Model):
    INSTALLATION_NA = 0
    INSTALLATION_DELIVER = 1
    INSTALLATION_INSTALL = 2
    INSTALLATION_CHOICES = [
        (INSTALLATION_NA, "NA/Unkown"),
        (INSTALLATION_DELIVER, "Deliver"),
        (INSTALLATION_INSTALL, "Install")
    ]

    job_name = models.CharField(
        'job name',
        max_length = 255,
        help_text = 'The name of the job'
    )
    po_number = models.CharField(
        'PO Number',
        max_length = 255,
        help_text = 'The PO Number for this jon'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete = models.SET_NULL,
        null=True,
        blank=True,
        help_text = 'The supplier of this load'
    )
    spo_number = models.CharField(
        'Supplier PO Number',
        max_length = 255,
        blank=True,
        help_text = 'The Suppier\'s PO Number for this jon'
    )
    description = models.TextField(
        'description',
        null=True,
        help_text = 'A description of the load'
    )
    notes = models.TextField(
          'notes',
        blank=True,
        help_text='Any notes about this load'
    )
    location = models.ForeignKey(
        Location,
        on_delete = models.SET_NULL,
        null=True,
        help_text = 'The location of this load'
    )
    status = models.ForeignKey(
        Status,
        on_delete = models.SET_NULL,
        null=True,
        help_text = 'The status of the load'
    )
    created_when = models.DateTimeField(
        'created',
        default = datetime.now,
        help_text = 'The date this historical entry was created'
    )
    updated_when = models.DateTimeField(
        'when updated',
        default = datetime.now,
        help_text = 'When the load was updated'
    )
    do_install = models.IntegerField(
        'Do Install',
        default = 1,
        choices = INSTALLATION_CHOICES,
        help_text = 'If Ervin will be doing the installation'
    )
    photo = models.ImageField(
        'photo',
        blank=True,
        null=True,
        help_text = 'A photo of the load'
    )
    notification_groups = models.ManyToManyField(
        NotificationGroup,
        blank = True,
        help_text = 'Notification groups that should be notified about changes to this load'
    )
    completion = models.ForeignKey(
        Completion,
        on_delete = models.SET_NULL,
        null=True,
        help_text = 'The completion status of this load'
    )
    deleted_when = models.DateTimeField(
        'deleted when',
        null = True,
        blank = True,
        help_text = 'If this item is deleted, when'
    )

    class Meta:
        ordering = ('updated_when',)

    def __str__(self):
        return f'{ self.po_number } - { self.job_name }'

    objects = LoadsNotDeletedManager()
    all_objects = models.Manager()


class LoadHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete = models.SET_NULL
    )
    load = models.ForeignKey(
        Load,
        null=True,
        on_delete = models.SET_NULL
    )
    changed_when = models.DateTimeField(
        auto_now_add = True
    )
    data = models.JSONField(
        'data',
        blank=True,
        help_text = 'The data that was submitted for this change'
    )
    class Meta:
        ordering=('-changed_when',)

class Notification(models.Model):
    load = models.ForeignKey(
        Load,
        on_delete = models.CASCADE,
        help_text = 'The load about which to notify'
    )
    action = models.CharField(
        'action',
        max_length=30,
        blank=True,
        help_text = 'The action (Created, Updated) to be reported'
    )
    created_when = models.DateField(
        'created when',
        blank=True,
        null=True,
        help_text = 'The date this notification was created'
    )

#eof
