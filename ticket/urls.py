from django.urls import path
from . import views
from .views import Ticket_Details, All_Tickets, Ticket_queue, Workspace, All_Closed_Tickets

urlpatterns = [
    path('ticket-details/<int:pk>/', Ticket_Details.as_view(), name='ticket-details'),
    path('create-ticket/', views.create_ticket, name='create-ticket'),
    path('update-ticket/<int:pk>/', views.update_ticket, name='update-ticket'),
    path('all-tickets/', All_Tickets.as_view(), name='all-tickets'),
    path('ticket-queue/', Ticket_queue.as_view(), name='ticket-queue'),
    path('accept-ticket/<int:pk>/', views.accept_ticket, name='accept-ticket'),
    path('close-ticket/<int:pk>/', views.close_ticket, name='close-ticket'),
    path('workspace/', Workspace.as_view(), name='workspace'),
    path('all-closed-tickets/', All_Closed_Tickets.as_view(), name='all-closed-tickets'),
    path('report/', views.report, name='report'),
]