import datetime
import io

from django.http import HttpResponse
from docxtpl import DocxTemplate

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

# @login_required
# def report(request):
#     return render(request, 'ticket/report.html')


class Report(ListView):
    model = Ticket
    template_name = 'ticket/report.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        return Ticket.objects.filter(assigned_to=self.request.user, is_resolved=True)

    def get_report(self):
        doc = DocxTemplate("static/ticket/docx/report-sample.docx")
        context = {'last_name': self.request.user.last_name,
                   'first_name': self.request.user.first_name}
        doc.render(context)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return doc


def report(request):
    now = datetime.datetime.now()
    tickets = Ticket.objects.filter(assigned_to=request.user, is_resolved=True, closed_date__month=now.month)
    print_len = 0
    comp_len = 0
    bars_len = 0
    internet_len = 0
    mount_len = 0
    for ticket in tickets:
        if ticket.ticket_type == 'print':
            print_len += 1
        elif ticket.ticket_type == 'computer':
            comp_len += 1
        elif ticket.ticket_type == 'bars':
            bars_len += 1
        elif ticket.ticket_type == 'internet':
            internet_len += 1
        elif ticket.ticket_type == 'mounting':
            mount_len += 1
        else:
            pass

    doc = DocxTemplate("ticket/static/ticket/docx/report-sample.docx")
    rest = {'last_name': request.user.last_name,
            'first_name': request.user.first_name,
            'date': now.date(),
            'month': '{0:%B}'.format(now),
            'number': len(tickets),
            'print': print_len,
            'computer': comp_len,
            'bars': bars_len,
            'internet': internet_len,
            'mounting': mount_len,
            }
    doc.render(rest)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    response["Content-Disposition"] = f'attachment; filename = "{now.date()}-reporte.docx"'
    response["Content-Encoding"] = "UTF-8"
    return response
