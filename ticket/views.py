import datetime

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import DetailView

from .models import Ticket
from .form import CreateTicketForm, UpdateTicketForm
from users.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView


# детали заявки
class Ticket_Details(DetailView):
    model = Ticket
    template_name = 'ticket/ticket_details.html'


class Tickets_Legacy(ListView):
    paginate_by = 5
    model = Ticket
    template_name = 'ticket/all_tickets.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        return Ticket.objects.filter(created_by=self.request.user).order_by('-date_created')



# @login_required
# def ticket_details(request, pk):
#     ticket = Ticket.objects.get(pk=pk)
#     users_tickets = User.objects.get(username=ticket.created_by)
#     tickets_legacy = users_tickets.created_by.all()
#     context = {'ticket': ticket, 'tickets_legacy': tickets_legacy}
#     return render(request, 'ticket/ticket_details.html', context)


"""Для юзеров"""


# Создане заявки
@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = CreateTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.ticket_status = 'Pending'
            ticket.department = request.user.department
            ticket.save()
            messages.info(request, 'Заявка успешно создана.')
            return redirect('dashboard')
        else:
            messages.warning(request, 'Что-то пошло не так. Проверьте введённые данные.')
            return redirect('create-ticket')
    else:
        form = CreateTicketForm()
        context = {'form': form}
        return render(request, 'ticket/create_ticket.html', context)


# Изменение заявки
@login_required
def update_ticket(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    if not ticket.is_resolved:
        if request.method == 'POST':
            form = UpdateTicketForm(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
                messages.info(request, 'Заявка успешно обнавлена.')
                return redirect('dashboard')
            else:
                messages.warning(request, 'Что-то пошло не так. Проверьте ввeдённые данные.')
        else:
            form = UpdateTicketForm(instance=ticket)
            context = {'form': form}
            return render(request, 'ticket/update_ticket.html', context)
    else:
        messages.warning(request, 'Заявка закрыта. Изменения неаозможны.')
        return redirect('dashboard')


# Просмотр всех созданных заявок
class All_Tickets(ListView):
    paginate_by = 5
    model = Ticket
    template_name = 'ticket/all_tickets.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        return Ticket.objects.filter(created_by=self.request.user).order_by('-date_created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

#
# @login_required
# def all_tickets(request):
#     tickets = Ticket.objects.filter(created_by=request.user).order_by('-date_created')
#     paginator = Paginator(tickets, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     context = {'tickets': tickets, 'page_obj': page_obj}
#     return render(request, 'ticket/all_tickets.html', context)


"""Для сотрудников"""


# просмотр очетеди заявок
class Ticket_queue(ListView):
    model = Ticket
    paginate_by = 10
    template_name = 'ticket/ticket_queue.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        return Ticket.objects.filter(ticket_status='Pending')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# @login_required
# def ticket_queue(request):
#     tickets = Ticket.objects.filter(ticket_status='Pending')
#     context = {'tickets': tickets}
#     return render(request, 'ticket/ticket_queue.html', context)


# Принтяие заявки из очереди
@login_required
def accept_ticket(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    ticket.assigned_to = request.user
    ticket.ticket_status = 'Active'
    ticket.save()
    messages.info(request, 'Заявка принята.')
    return redirect('workspace')


# Закрытие заявки
@login_required
def close_ticket(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    ticket.ticket_status = 'Completed'
    ticket.is_resolved = True
    ticket.closed_date = datetime.datetime.now()
    ticket.save()
    messages.info(request, 'Заявка выполнена.')
    return redirect('ticket-queue')


# Заявка в работе
class Workspace(ListView):
    model = Ticket
    paginate_by = 5
    template_name = 'ticket/workspace.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        return Ticket.objects.filter(assigned_to=self.request.user, is_resolved=False)


# @login_required
# def workspace(request):
#     tickets = Ticket.objects.filter(assigned_to=request.user, is_resolved=False)
#     context = {'tickets': tickets}
#     return render(request, 'ticket/workspace.html', context)


# Все закрытые заявки
class All_Closed_Tickets(ListView):
    model = Ticket
    paginate_by = 5
    template_name = 'ticket/all_closed_tickets.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        return Ticket.objects.filter(assigned_to=self.request.user, is_resolved=True)


# @login_required
# def all_closed_tickets(request):
#     tickets = Ticket.objects.filter(assigned_to=request.user, is_resolved=True)
#     context = {'tickets': tickets}
#     return render(request, 'ticket/all_closed_tickets.html', context)
