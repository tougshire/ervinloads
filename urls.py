from django.views.generic.base import RedirectView
from django.urls import path, reverse_lazy
from . import views

app_name = 'ervinloads'

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('ervinloads:load-list'))),
    path('load/', RedirectView.as_view(url=reverse_lazy('ervinloads:load-list'))),
    path('load/create/', views.LoadCreate.as_view(), name='load-create'),
    path('load/<int:pk>/update/', views.LoadUpdate.as_view(), name='load-update'),
    path('load/<int:pk>/detail/', views.LoadDetail.as_view(), name='load-detail'),
    path('load/<int:pk>/delete/', views.LoadSoftDelete.as_view(), name='load-delete'),
    path('load/list/', views.LoadList.as_view(), name='load-list'),
    path('load/<int:pk>/close/', views.LoadClose.as_view(), name="load-close"),
    path('location/', RedirectView.as_view(url=reverse_lazy('ervinloads:location-list'))),
    path('location/create/', views.LocationCreate.as_view(), name='location-create'),
    path('location/<int:pk>/update/', views.LocationUpdate.as_view(), name='location-update'),
    path('location/<int:pk>/detail/', views.LocationDetail.as_view(), name='location-detail'),
    path('location/<int:pk>/delete/', views.LocationDelete.as_view(), name='location-delete'),
    path('location/<int:pk>/merge/', views.LocationMerge.as_view(), name='location-merge'),
    path('location/list/', views.LocationList.as_view(), name='location-list'),
    path('location/<int:pk>/close/', views.LocationClose.as_view(), name="location-close"),
    path('supplier/', RedirectView.as_view(url=reverse_lazy('ervinloads:supplier-list'))),
    path('supplier/create/', views.SupplierCreate.as_view(), name='supplier-create'),
    path('supplier/<int:pk>/update/', views.SupplierUpdate.as_view(), name='supplier-update'),
    path('supplier/<int:pk>/detail/', views.SupplierDetail.as_view(), name='supplier-detail'),
    path('supplier/<int:pk>/delete/', views.SupplierDelete.as_view(), name='supplier-delete'),
    path('supplier/list/', views.SupplierList.as_view(), name='supplier-list'),
    path('supplier/<int:pk>/close/', views.SupplierClose.as_view(), name="supplier-close"),
    path('notification/queue/', views.NotificationQueue.as_view(), name='notification-queue'),
    path('notifications/count/', views.notification_count, name='notifications-count')

]
