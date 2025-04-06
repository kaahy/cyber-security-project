from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone
from django.template.loader import render_to_string
from .models import Choice, Question, Comment

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_questions_list'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        choice_id = request.POST['choice']
    except:
        context = {'question': question, 'error_message': "Something went wrong."}
        return render(request, 'polls/detail.html', context)
    else:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE polls_choice SET votes=votes+1 WHERE id={choice_id}")
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

    # Flaw 1: Injection
    # Description: the form value for choice id could be altered to something like "1 OR 2=2" so that every choice gets affected
    # Fix: uncomment the function below

"""
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        context = {'question': question, 'error_message': "You didn't select a choice."}
        return render(request, 'polls/detail.html', context)
    except:
        context = {'question': question, 'error_message': "Something went wrong."}
        return render(request, 'polls/detail.html', context)
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
"""

def delete_poll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # Flaw 2: Broken Access Control
    # Description: anyone could delete a poll by going to /<poll_id>/delete
    # or, if the csrf flaw was fixed, sending there a post request with 'id' and one's own 'csrfmiddlewaretoken'
    # Fix: uncomment the code below

    #if not request.user.is_superuser:
    #    return HttpResponseRedirect(reverse('polls:index'))

    try:
        pass
        # Flaw 3: Cross-Site Request Forgery (CSRF)
        # Description: even an admin could be tricked to delete a poll by getting them to load /<poll_id>/delete for example through an img tag
        # Fix: uncomment the code below AND what is commented out in detail.html

        #question = Question.objects.get(pk=request.POST['id'])
        question.delete()
    except:
        context = {'question': question, 'error_message': "Error while trying to delete the poll."}
        return render(request, 'polls/detail.html', context)
    else:
        return HttpResponseRedirect(reverse('polls:index'))

def add_comment(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    sent_comment = request.POST['comment_text']
    comment_to_save = Comment(question_id = question.id, comment_text = sent_comment)
    comment_to_save.save()
    return HttpResponseRedirect(reverse('polls:view_comments', args=(question.id,)))

def view_comments(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    comments = Comment.objects.filter(question_id=question_id)
    comments_str = map(str, comments)

    # Flaw 4: Cross-Site Scripting (XSS)
    # Description: users can write executable (potentially harmful) code
    # Fix: uncomment the code below

    #import html
    #comments_str = map(html.escape, comments_str)

    """
    Note: this flaw could also(/preferably) be fixed by
    using Django templates instead of writing any html here,
    but the assignment was to show backend fixes
    and I wasn't sure if templates count as backend
    """

    comment_form = render_to_string('polls/comment_form.html', {'question': question}, request=request)

    html_code = f"""
    {comment_form}
    {"<hr />".join(comments_str)}
    <hr />
    <p><a href="/{ question.id }">Back to voting</a></p>
    <p><a href="/">Back to polls</a></p>
    </div></body></html>
    """

    return HttpResponse(html_code)
