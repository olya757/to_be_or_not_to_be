from django.http import *
from django.shortcuts import render
# Create your views here.
from django.urls import reverse_lazy
from django.views import generic
from .models import *
from .forms import *
from django.contrib import auth
from django.shortcuts import redirect



class SignUp(generic.CreateView):
    form_class = TeacherCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


class Home(generic.TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = GroupCurriculum.objects.filter()
        today = datetime.date.today()
        context['today'] = today.isoformat()
        user = self.request.user
        if user.is_authenticated:
            context['groups'] = GroupCurriculum.objects.filter(curriculum__in=Curriculum.objects.filter(teacher=user))
        return context


def select_in_home(request):
    user = request.user
    gc_id = request.POST['group_elem']
    gc = GroupCurriculum.objects.get(id=gc_id)
    if user and user.is_authenticated:
        date = request.POST['date']
        template = loader.get_template('visiting.html')
        students = Student.objects.filter(group=gc.group)
        context = {
            'students': students,
            'date': date,
            'gc': gc
        }

    else:
        template = loader.get_template('table.html')
        elems = Visit.objects.order_by('date')
        students = elems.filter(group_curriculum=gc)
        print(students)
        dates = set()

        table = dict()
        for elem in students:
            if elem.student in table:
                table[elem.student].append(elem.visit)
            else:
                table[elem.student]=list()
                table[elem.student].append(elem.visit)
            dates.add(elem.date)
        dates = list(dates)
        dates.sort()
        context = {
            'dates': dates,
            'values': table.items(),
            'subject':str(gc)
        }
        for i in table.items():
            print()

    return HttpResponse(template.render(context, request))


def save(request, gc_id, date):
    user = request.user
    gc = GroupCurriculum.objects.get(id=gc_id)
    #date = request.POST['date']
    students = Student.objects.filter(group=gc.group)
    for st in students:
        #print(request.POST(st.id))
        res = str(st.id) in request.POST
        print(res)
        visit = Visit()
        visit.student = st
        visit.group_curriculum = gc
        visit.date = date
        visit.visit = res
        visit.save()
    template = loader.get_template('home.html')
    return HttpResponseRedirect('../../home')




