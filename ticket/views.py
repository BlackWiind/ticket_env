import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Ticket
from .form import CreateTicketForm, UpdateTicketForm
from users.models import User
from django.contrib.auth.decorators import login_required


# детали заявки
@login_required
def ticket_details(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    users_tickets = User.objects.get(username=ticket.created_by)
    tickets_legacy = users_tickets.created_by.all()
    context = {'ticket': ticket, 'tickets_legacy': tickets_legacy}
    return render(request, 'ticket/ticket_details.html', context)


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
@login_required
def all_tickets(request):
    tickets = Ticket.objects.filter(created_by=request.user).order_by('-date_created')
    context = {'tickets': tickets}
    return render(request, 'ticket/all_tickets.html', context)


"""Для сотрудников"""


# просмотр очетеди заявок
@login_required
def ticket_queue(request):
    tickets = Ticket.objects.filter(ticket_status='Pending')
    context = {'tickets': tickets}
    return render(request, 'ticket/ticket_queue.html', context)


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
@login_required
def workspace(request):
    tickets = Ticket.objects.filter(assigned_to=request.user, is_resolved=False)
    context = {'tickets': tickets}
    return render(request, 'ticket/workspace.html', context)


# Все закрытые заявки
@login_required
def all_closed_tickets(request):
    tickets = Ticket.objects.filter(assigned_to=request.user, is_resolved=True)
    context = {'tickets': tickets}
    return render(request, 'ticket/all_closed_tickets.html', context)
