import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Ticket
from .form import CreateTicketForm, UpdateTicketForm

"""Для юзеров"""


# Создане заявки
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
            messages.warning(request, 'Что-то пошло не так. Проверьте ввудённые данные.')
            return redirect('create-ticket')
    else:
        form = CreateTicketForm()
        context = {'form': form}
        return request(request, 'ticket/create_ticket.html', context)


# Изменение заявки
def update_ticket(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    if request.method == 'POST':
        form = UpdateTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.info(request, 'Заявка успешно обнавлена.')
            return redirect('dashboard')
        else:
            messages.warning(request, 'Что-то пошло не так. Проверьте ввудённые данные.')
            # return redirect('create-ticket')
    else:
        form = UpdateTicketForm()
        context = {'form': form}
        return request(request, 'ticket/update_ticket.html', context)


# Просмотр всех созданных заявок

def all_tickets(request):
    tickets = Ticket.objects.filter(created_by=request.user)
    context = {'tickets': tickets}
    return render(request, 'ticket/all_tickets.html', context)


"""Для сотрудников"""

# просмотр очетеди заявок
def ticket_queue(request):
    tickets = Ticket.objects.filter(ticket_status='Pending')
    context = {'tickets':tickets}
    return render(request, 'ticket/ticket_queue.html', context)

# Принтяие заявки из очереди
def accept_ticket(request,pk):
    ticket = Ticket.objects.get(pk=pk)
    ticket.assigned_to = request.user
    ticket.ticket_status = 'Active'
    ticket.save()
    messages.info(request, 'Заявка принята.')
    return redirect('ticket-queue')


# Закрытие заявки
def close_ticket(request,pk):
    ticket = Ticket.objects.get(pk=pk)
    ticket.ticket_status = 'Completed'
    ticket.is_resolved = True
    ticket.closed_date = datetime.datetime.now()
    ticket.save()
    messages.info(request, 'Заявка выполнена.')
    return redirect('ticket-queue')