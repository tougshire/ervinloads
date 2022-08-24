import re
import sys
import urllib
from urllib.parse import urlencode
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.http import Http404, QueryDict
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django.views.generic.list import ListView
from tougshire_vistas.models import Vista
from tougshire_vistas.views import (default_vista, delete_vista,
                                    get_global_vista, get_latest_vista,
                                    make_vista, make_vista_fields,
                                    retrieve_vista, vista_context_data)
from django.core.mail import send_mail
from .forms import (LoadForm, LocationForm, LocationMergeForm, NotificationForm, NotificationSendForm, SupplierForm)
from .models import (CompletionStatus, Load, Location, Notification, NotificationGroup, DeliveryStatus, Supplier,)

from tougshire_history.views import update_history
from tougshire_history.models import History
from django.contrib.auth.decorators import permission_required

def send_notification(request, notification):
    emails = []
    load = notification.load
    notification_groups = load.notification_groups.all()
    for notification_group in notification_groups:
        emails_in_group = re.split( r",|;", notification_group.email_addresses)
        for email in emails_in_group:
            email = email.strip()
            if email > '' and not email in emails:
                emails.append(email)

    load_url = request.build_absolute_uri(
        reverse('ervinloads:load-detail', kwargs={'pk': load.pk}))

    mail_subject = f"Load { notification.action }: {load.po_number} - { load.job_name }"

    mail_from = settings.ERVINSUFFOLK_FROM_EMAIL if hasattr(
        settings, 'ERVINSUFFOLK_FROM_EMAIL') else settings.DEFAULT_FROM_EMAIL

    mail_message = "\n".join(
        [
            f"The following load was { notification.action }",
            "",
            f"Job Name: { load.job_name }",
            f"PO Numner: { load.po_number }" ,
            f"Supplier: {load.supplier }",
            f"Supplier PO Number: { load.spo_number }",
            f"Description: { load.description }",
            f"Location: { load.location.name }",
            f"Delivery Status: { load.delivery_status.name }",
            f"Completion Status: { load.completion_status.name }",
            f"Notes: { load.notes }",
            f"URL: { load_url }",
        ]
    )

    mail_html_message = "<br>\n".join(
        [
            f"The following load was { notification.action }",
            "",
            f"Job Name: { load.job_name }",
            f"PO Number: { load.po_number }",
            f"Supplier: {load.supplier }",
            f"Supplier PO Number: { load.spo_number }",
            f"Description: { load.description }",
            f"Location: { load.location.name }",
            f"Delivery Status: { load.delivery_status.name }",
            f"Completion Status: { load.completion_status.name }",
            f"Notes: { load.notes }",
            f"URL: <a href=\"{ load_url }\">{ load_url }</a>"
        ]
    )

    mail_recipients = emails

    try:
        send_mail(
            mail_subject,
            mail_message,
            mail_from,
            mail_recipients,
            html_message=mail_html_message,
            fail_silently=False,
        )
    except Exception as e:
        messages.add_message(request, messages.WARNING, 'There was an error sending emails.')
        messages.add_message(request, messages.WARNING, e)

        print(e, ' at ', sys.exc_info()[2].tb_lineno)

        return e


def send_notifications(request, notifications):
    email_addresses = []

    mail_from = settings.ERVINSUFFOLK_FROM_EMAIL if hasattr(
        settings, 'ERVINSUFFOLK_FROM_EMAIL') else settings.DEFAULT_FROM_EMAIL

    mail_subject = 'Notification'
    mail_message=''
    mail_html_message=''
    
    for notification in notifications:
        load = notification.load
        notification_groups = load.notification_groups.all()
        for notification_group in notification_groups:
            emails_in_group = re.split( r",|;", notification_group.email_addresses)
            for email_address in emails_in_group:
                email_address = email_address.strip()
                if email_address > '' and not email_address in email_addresses:
                    email_addresses.append(email_address)

        mail_subject = mail_subject + f":: Load { notification.action }: {load.po_number} - { load.job_name }" 

        load_url = request.build_absolute_uri(
            reverse('ervinloads:load-detail', kwargs={'pk': load.pk}))


        mail_message = mail_message + "\n".join(
            [
                f"The following load was { notification.action }",
                "",
                f"Job Name: { load.job_name }",
                f"PO Numner: { load.po_number }" ,
                f"Supplier: {load.supplier }",
                f"Supplier PO Number: { load.spo_number }",
                f"Description: { load.description }",
                f"Location: { load.location.name }",
                f"Delivery Status: { load.delivery_status.name }",
                f"Completion Status: { load.completion_status.name }",
                f"Notes: { load.notes }",
                f"URL: { load_url }",
                '------------------------------------',
                '',
            ]
        )

        mail_html_message = mail_html_message + "<br>\n".join(
            [
                f"The following load was { notification.action }",
                "",
                f"Job Name: { load.job_name }",
                f"PO Number: { load.po_number }",
                f"Supplier: {load.supplier }",
                f"Supplier PO Number: { load.spo_number }",
                f"Description: { load.description }",
                f"Location: { load.location.name }",
                f"Delivery Status: { load.delivery_status.name }",
                f"Completion Status: { load.completion_status.name }",
                f"Notes: { load.notes }",
                f"URL: <a href=\"{ load_url }\">{ load_url }</a>",
                '------------------------------------',
                ''
            ]
        )

    mail_recipients = email_addresses

    try:
        send_mail(
            mail_subject,
            mail_message,
            mail_from,
            mail_recipients,
            html_message=mail_html_message,
            fail_silently=False,
        )
    except Exception as e:
        messages.add_message(request, messages.WARNING, 'There was an error sending emails.')
        messages.add_message(request, messages.WARNING, e)

        print(e, ' at ', sys.exc_info()[2].tb_lineno)

        return e

class LoadCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'ervinloads.add_load'
    model = Load
    form_class = LoadForm

    def get_initial(self):

        initial = super().get_initial()
        initial['notification_groups'] = [group for group in NotificationGroup.objects.filter(is_default=True)]
        initial['delivery_status'] = DeliveryStatus.objects.filter(is_default=True).first()
        initial['completion_status'] = CompletionStatus.objects.filter(is_default=True).first()
        initial['location'] = Location.objects.filter(is_default=True).first()

        return initial

    def form_valid(self, form):

        response = super().form_valid(form)

        update_history(form, 'ervinloads', 'load', form.instance, self.request.user)

        self.object = form.save()

        notification = Notification.objects.create(
            load = self.object,
            action = 'Created'
        )

        if self.request.POST.get('send_now'):
            send_notification(self.request, notification)
            notification.delete()

        return response

    def get_success_url(self):
        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('ervinloads:load-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('ervinloads:load-detail', kwargs={'pk': self.object.pk})

class LoadUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'ervinloads.change_load'
    model = Load
    form_class = LoadForm

    def get_initial(self):

        initial = super().get_initial()
        initial['updated_when'] = datetime.now()
        return initial

    def form_valid(self, form):

        update_history(form, 'ervinloads','load', form.instance, self.request.user)

        response = super().form_valid(form)

        self.object = form.save()

        notification, created = Notification.objects.get_or_create(
            load = self.object
        )
        notification.save()
        if created:
            notification.action = "Updated"
        else:
            notification.action = "Created and Updated"
        notification.save()

        if self.request.POST.get('send_now'):
            send_notification(self.request, notification)
            notification.delete()

        return response

    def get_success_url(self):
        return reverse_lazy('ervinloads:load-detail', kwargs={ 'pk':self.object.pk })


class LoadDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'ervinloads.view_load'
    model = Load

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['load_labels'] = { field.name: field.verbose_name.title() for field in Load._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        context_data['load_histories'] = History.objects.filter(app_label='ervinloads', modelname='load', objectid=self.object.pk)

        return context_data

class LoadDelete(PermissionRequiredMixin, UpdateView):
    permission_required = 'ervinloads.delete_load'
    model = Load
    success_url = reverse_lazy('ervinloads:load-list')

class LoadSoftDelete(PermissionRequiredMixin, UpdateView):
    permission_required = 'ervinloads.delete_load'
    model = Load
    template_name = 'ervinloads/load_confirm_delete.html'
    success_url = reverse_lazy('ervinloads:load-list')
    fields = ['is_deleted']

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['load_labels'] = { field.name: field.verbose_name.title() for field in Load._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class LoadList(PermissionRequiredMixin, ListView):
    permission_required = 'ervinloads.view_load'
    model = Load
    paginate_by = 30

    def setup(self, request, *args, **kwargs):

        self.vista_settings={
            'max_search_keys':5,
            'fields':[],
        }

        self.vista_settings['fields'] = make_vista_fields(Load, field_names=[
            'job_name',
            'po_number',
            'supplier',
            'spo_number',
            'description',
            'notes',
            'location',
            'delivery_status',
            'delivery_status__is_active',
            'created_when',
            'updated_when',
            'do_install',
            'photo',
            'completion_status',
            'completion_status__is_active'
        ])
        self.vista_settings['fields']['description']['available_for'].append('columns')
        self.vista_settings['fields']['notes']['available_for'].append('columns')
        self.vista_settings['fields']['delivery_status__is_active']['label']='Delivery Is Pending'
        self.vista_settings['fields']['completion_status__is_active']['label']='Completion Is Pending'

        self.vista_defaults = QueryDict(urlencode([
            ('filter__fieldname__0', ['delivery_status__is_active']),
            ('filter__op__0', ['exact']),
            ('filter__value__0', [True]),
            ('order_by', ['-updated_when']),
            ('paginate_by',self.paginate_by),
        ],doseq=True) )

        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = super().get_queryset()

        self.vistaobj = {'querydict':QueryDict(), 'queryset':queryset}

        if 'delete_vista' in self.request.POST:
            delete_vista(self.request)

        if 'query' in self.request.session:
            print('tp 224bc49', 'query in self.request.session')
            querydict = QueryDict(self.request.session.get('query'))
            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                querydict,
                '',
                False,
                self.vista_settings
            )
            del self.request.session['query']

        elif 'vista_query_submitted' in self.request.POST:
            print('tp 224bc50', 'vista_query_submitted')

            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                self.request.POST,
                self.request.POST.get('vista_name') if 'vista_name' in self.request.POST else '',
                self.request.POST.get('make_default') if ('make_default') in self.request.POST else False,
                self.vista_settings
            )
        elif 'retrieve_vista' in self.request.POST:
            print('tp 224bc51', 'retrieve_vista')

            self.vistaobj = retrieve_vista(
                self.request.user,
                queryset,
                'ervinloads.load',
                self.request.POST.get('vista_name'),
                self.vista_settings

            )
        elif 'default_vista' in self.request.POST:
            print('tp 224bc52', 'default_vista')

            self.vistaobj = default_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )
        else:
            self.vistaobj = get_latest_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )

            print('tp 224bc53', 'else')

        return self.vistaobj['queryset']

    def get_paginate_by(self, queryset):

        if 'paginate_by' in self.vistaobj['querydict'] and self.vistaobj['querydict']['paginate_by']:
            return self.vistaobj['querydict']['paginate_by']

        return super().get_paginate_by(self)

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        vista_data = vista_context_data(self.vista_settings, self.vistaobj['querydict'])

        context_data = {**context_data, **vista_data}

        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='ervinloads.load').all() # for choosing saved vistas

        if self.request.POST.get('vista_name'):
            context_data['vista_name'] = self.request.POST.get('vista_name')

        context_data['count'] = self.object_list.count()

        return context_data


class LoadClose(PermissionRequiredMixin, DetailView):
    permission_required = 'ervinloads.view_load'
    model = Load
    template_name = 'ervinloads/load_closer.html'


class LocationCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'ervinloads.add_location'
    model = Location
    form_class = LocationForm

    def form_valid(self, form):

        response = super().form_valid(form)

        update_history(form, 'ervinloads', 'location', form.instance, self.request.user)

        self.object = form.save()

        return response

    def get_success_url(self):
        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('ervinloads:location-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('ervinloads:location-detail', kwargs={'pk': self.object.pk})

class LocationUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'ervinloads.change_location'
    model = Location
    form_class = LocationForm


    def form_valid(self, form):

        update_history(form, 'ervinloads','location', form.instance, self.request.user)

        response = super().form_valid(form)

        self.object = form.save()

        return response

    def get_success_url(self):
        return reverse_lazy('ervinloads:location-detail', kwargs={ 'pk':self.object.pk })


class LocationDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'ervinloads.view_location'
    model = Location

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['location_labels'] = { field.name: field.verbose_name.title() for field in Location._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class LocationDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'ervinloads.delete_location'
    model = Location
    success_url = reverse_lazy('ervinloads:location-list')


class LocationMerge(PermissionRequiredMixin, FormView):
    permission_required = 'ervinloads.delete_location'
    success_url = reverse_lazy('ervinloads:location-list')
    template_name = 'ervinloads/location_merge_form.html'
    form_class = LocationMergeForm

    def get_initial(self, **kwargs):
        initial_data = super().get_initial(**kwargs)
        print('tp 2253f05', self.kwargs.get('pk'))
        initial_data['merge_from'] = self.kwargs.get('pk')
        return initial_data

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['merge_to'] = Location.objects.get(pk=self.kwargs.get('pk'))
        return context_data

    def form_valid(self, form):
        try:
            Load.objects.filter(location=form.cleaned_data['merge_from']).update(location=form.cleaned_data['merge_to'])
            form.cleaned_data['merge_from'].delete()
        except Exception as e:
            messages.add_message(self.request, messages.WARNING, 'This merge could not be completed' )
            messages.add_message(self.request, messages.WARNING, str(e) )
            return super().form_invalid(form)

        return super().form_valid(form)

class LocationList(PermissionRequiredMixin, ListView):
    permission_required = 'ervinloads.view_location'
    model = Location
    paginate_by = 30

    def setup(self, request, *args, **kwargs):

        self.vista_settings={
            'max_search_keys':5,
            'fields':[],
        }

        self.vista_settings['fields'] = make_vista_fields(Location, field_names=[
            'name',
        ])

        self.vista_defaults = QueryDict(urlencode([
            ('order_by', ['name']),
            ('paginate_by',self.paginate_by),
        ],doseq=True) )

        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = super().get_queryset()

        self.vistaobj = {'querydict':QueryDict(), 'queryset':queryset}

        if 'delete_vista' in self.request.POST:
            delete_vista(self.request)

        if 'query' in self.request.session:
            querydict = QueryDict(self.request.session.get('query'))
            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                querydict,
                '',
                False,
                self.vista_settings
            )
            del self.request.session['query']

        elif 'vista_query_submitted' in self.request.POST:
            print('tp 224bc50', 'vista_query_submitted')

            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                self.request.POST,
                self.request.POST.get('vista_name') if 'vista_name' in self.request.POST else '',
                self.request.POST.get('make_default') if ('make_default') in self.request.POST else False,
                self.vista_settings
            )
        elif 'retrieve_vista' in self.request.POST:
            print('tp 224bc51', 'retrieve_vista')

            self.vistaobj = retrieve_vista(
                self.request.user,
                queryset,
                'ervinloads.location',
                self.request.POST.get('vista_name'),
                self.vista_settings

            )
        elif 'default_vista' in self.request.POST:
            print('tp 224bc52', 'default_vista')

            self.vistaobj = default_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )
        else:
            self.vistaobj = get_latest_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )

            print('tp 224bc53', 'else')

        return self.vistaobj['queryset']

    def get_paginate_by(self, queryset):

        if 'paginate_by' in self.vistaobj['querydict'] and self.vistaobj['querydict']['paginate_by']:
            return self.vistaobj['querydict']['paginate_by']

        return super().get_paginate_by(self)

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        vista_data = vista_context_data(self.vista_settings, self.vistaobj['querydict'])

        context_data = {**context_data, **vista_data}

        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='ervinloads.location').all() # for choosing saved vistas

        if self.request.POST.get('vista_name'):
            context_data['vista_name'] = self.request.POST.get('vista_name')

        context_data['count'] = self.object_list.count()

        return context_data


class LocationClose(PermissionRequiredMixin, DetailView):
    permission_required = 'ervinloads.view_location'
    model = Location
    template_name = 'ervinloads/location_closer.html'


class SupplierCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'ervinloads.add_supplier'
    model = Supplier
    form_class = SupplierForm

    def form_valid(self, form):

        response = super().form_valid(form)

        update_history(form, 'ervinloads', 'supplier', form.instance, self.request.user)

        self.object = form.save()

        return response

    def get_success_url(self):
        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('ervinloads:supplier-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('ervinloads:supplier-detail', kwargs={'pk': self.object.pk})

class SupplierUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'ervinloads.change_supplier'
    model = Supplier
    form_class = SupplierForm


    def form_valid(self, form):

        update_history(form, 'ervinloads','supplier', form.instance, self.request.user)

        response = super().form_valid(form)

        self.object = form.save()

        return response

    def get_success_url(self):
        return reverse_lazy('ervinloads:supplier-detail', kwargs={ 'pk':self.object.pk })


class SupplierDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'ervinloads.view_supplier'
    model = Supplier

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['supplier_labels'] = { field.name: field.verbose_name.title() for field in Supplier._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class SupplierDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'ervinloads.delete_supplier'
    model = Supplier
    success_url = reverse_lazy('ervinloads:supplier-list')

class SupplierList(PermissionRequiredMixin, ListView):
    permission_required = 'ervinloads.view_supplier'
    model = Supplier
    paginate_by = 30

    def setup(self, request, *args, **kwargs):

        self.vista_settings={
            'max_search_keys':5,
            'fields':[],
        }

        self.vista_settings['fields'] = make_vista_fields(Supplier, field_names=[
            'name',
        ])

        self.vista_defaults = QueryDict(urlencode([
            ('order_by', ['updated_when']),
            ('paginate_by',self.paginate_by),
        ],doseq=True) )

        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = super().get_queryset()

        self.vistaobj = {'querydict':QueryDict(), 'queryset':queryset}

        if 'delete_vista' in self.request.POST:
            delete_vista(self.request)

        if 'query' in self.request.session:
            querydict = QueryDict(self.request.session.get('query'))
            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                querydict,
                '',
                False,
                self.vista_settings
            )
            del self.request.session['query']

        elif 'vista_query_submitted' in self.request.POST:
            print('tp 224bc50', 'vista_query_submitted')

            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                self.request.POST,
                self.request.POST.get('vista_name') if 'vista_name' in self.request.POST else '',
                self.request.POST.get('make_default') if ('make_default') in self.request.POST else False,
                self.vista_settings
            )
        elif 'retrieve_vista' in self.request.POST:
            print('tp 224bc51', 'retrieve_vista')

            self.vistaobj = retrieve_vista(
                self.request.user,
                queryset,
                'ervinloads.supplier',
                self.request.POST.get('vista_name'),
                self.vista_settings

            )
        elif 'default_vista' in self.request.POST:
            print('tp 224bc52', 'default_vista')

            self.vistaobj = default_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )
        else:
            self.vistaobj = get_latest_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )

            print('tp 224bc53', 'else')

        return self.vistaobj['queryset']

    def get_paginate_by(self, queryset):

        if 'paginate_by' in self.vistaobj['querydict'] and self.vistaobj['querydict']['paginate_by']:
            return self.vistaobj['querydict']['paginate_by']

        return super().get_paginate_by(self)

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        vista_data = vista_context_data(self.vista_settings, self.vistaobj['querydict'])

        context_data = {**context_data, **vista_data}

        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='ervinloads.supplier').all() # for choosing saved vistas

        if self.request.POST.get('vista_name'):
            context_data['vista_name'] = self.request.POST.get('vista_name')

        context_data['count'] = self.object_list.count()

        return context_data


class SupplierClose(PermissionRequiredMixin, DetailView):
    permission_required = 'ervinloads.view_supplier'
    model = Supplier
    template_name = 'ervinloads/supplier_closer.html'


class NotificationQueue(PermissionRequiredMixin, FormView):
    permission_required = 'ervinloads.change_load'

    form_class = NotificationSendForm
    template_name = 'ervinloads/notification_queue.html'

    def get_success_url(self):
        return reverse('ervinloads:notification-queue')

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['notifications'] = Notification.objects.all()
        return context_data

    def form_valid(self, form):

        response = super().form_valid(form)

        notifications = form.cleaned_data['notifications']
        if( form.cleaned_data['operation'] == 'ss'):

            try:
                send_notifications(self.request, notifications )
                for notification in notifications:
                    notification.delete()
            except Exception as e:
                print(e)
            
        elif(form.cleaned_data['operation']) == 'sa':

            try:
                send_notification(self.request, notifications )

            except Exception as e:
                print(e)

            for notification in Notification.objects.all():
                notification.delete()

        elif(form.cleaned_data['operation']) == 'ns':
            for notification in notifications:
                try:
                    notification.delete()
                except Exception as e:
                    print(e)




        # if( form.cleaned_data['operation'] == 'ss'):
        #     for notification in form.cleaned_data['notifications']:
        #         try:
        #             send_notification(self.request, notification )
        #             notification.delete()
        #         except Exception as e:
        #             print(e)

        # elif(form.cleaned_data['operation']) == 'sa':
        #     for notification in form.cleaned_data['notifications']:
        #         try:
        #             send_notification(self.request, notification )
        #             notification.delete()
        #         except Exception as e:
        #             print(e)

        #     for notification in Notification.objects.all():
        #         if not notification in form.cleaned_data['notifications']:
        #             notification.delete()

        # elif(form.cleaned_data['operation']) == 'ns':
        #     for notification in form.cleaned_data['notifications']:
        #         try:
        #             notification.delete()
        #         except Exception as e:
        #             print(e)

        return response

def notification_count(request):
    return HttpResponse(Notification.objects.count())

