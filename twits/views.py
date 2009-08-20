from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from secretballot.middleware import SecretBallotIpUseragentMiddleware
from hateonyourjob.twits.models import *

def index(request):
    twit_list = Paginator(Hate.objects.all(), 25)
    page = int(request.GET.get('page', '1'))
    twits = twit_list.page(page)
    companies = Company.objects.all()[0:9]
    categories = Category.objects.all()
    return render_to_response("twits/index.html", {'twits': twits, 'companies': companies, 'categories': categories})

def company(request, slug, sort=None):
    company = get_object_or_404(Company, company_slug=slug)
    if sort:
        if sort == "votes":
            twit_list = Paginator(Hate.objects.filter(hate_company=company).order_by("-hate_vote"), 25)

        elif sort == "newest":
            twit_list = Paginator(Hate.objects.filter(hate_company=company).order_by("-created_date"), 25)

        elif sort == "oldest":
            twit_list = Paginator(Hate.objects.filter(hate_company=company).order_by("created_date"), 25)

        elif sort == "title":
            twit_list = Paginator(Hate.objects.filter(hate_company=company).order_by("hate_title"), 25)

        else:
            twit_list = Paginator(Hate.objects.filter(hate_company=company), 25)

    else:
        twit_list = Paginator(Hate.objects.filter(hate_company=company), 25)
    page = int(request.GET.get('page', '1'))
    twits = twit_list.page(page)
    companies = Company.objects.all()[0:9]
    categories = Category.objects.all()
    return render_to_response("twits/companies.html", {'twits': twits, 'companies': companies, 'categories': categories})

def company_id(request, id):
    company = get_object_or_404(Company, id=id)
    twit_list = Paginator(Hate.objects.filter(hate_company=company), 25)
    page = int(request.GET.get('page', '1'))
    twits = twit_list.page(page)
    companies = Company.objects.all()[0:9]
    categories = Category.objects.all()
    return render_to_response("twits/companies.html", {'twits': twits, 'companies': companies, 'categories': categories})

def category(request, slug):
    companies = Company.objects.all()[0:9]
    categories = Category.objects.all()
    category = get_object_or_404(Category, category_slug=slug)
    comps = Company.objects.filter(company_category=category.id)
    return render_to_response("twits/categories.html", {'comps': comps, 'companies': companies, 'categories': categories})

def hate_on(request, slug=None):
    companies = Company.objects.all()[0:9]
    categories = Category.objects.all()
    if request.method == 'POST':
        form = HateForm(request.POST)
        if form.is_valid():
            human = True
            form.save()
            return HttpResponseRedirect('/')
    else:
        if slug:
            item = get_object_or_404(Company, company_slug=slug)
            form = HateForm(initial={'hate_company': item.id})
        else:
            form = HateForm()
    return render_to_response("twits/hate_on.html", {'form': form, 'companies': companies, 'categories': categories})

def new_company(request):
    companies = Company.objects.all()[0:9]
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            human = True
            form.save()
            slug = defaultfilters.slugify(form.cleaned_data['company_name'])
            return HttpResponseRedirect('/hate_on/%s' % slug)
    else:
        form = CompanyForm(initial={'company_description': "Please place a short description of the company here. You'll then be sent to the hate form!"})
    return render_to_response("twits/new_company.html", {'form': form, 'companies': companies, 'categories': categories})

def about(request):
    companies = Company.objects.all()[0:9]
    categories = Category.objects.all()
    return render_to_response("twits/about.html", {'companies': companies, 'categories': categories})

def vote_up(request, id):
    twit = get_object_or_404(Hate, id=id)
    token = gen_token(request)
    twit.add_vote(token, "1")
    vote = Hate.objects.get(id=id)
    vote.hate_vote = vote.vote_total
    vote.save()
    #twit.hate_vote += 1
    #twit.save()
    return HttpResponseRedirect('/total_votes/%s' % twit.id)

def vote_down(request, id):
    twit = get_object_or_404(Hate, id=id)
    token = gen_token(request)
    twit.add_vote(token, "1")
    vote = Hate.objects.get(id=id)
    vote.hate_vote = vote.vote_total
    vote.save()
    #twit.hate_vote += -1
    #twit.save()
    return HttpResponseRedirect('/total_votes/%s' % twit.id)

def total_votes(request, id):
    twit = Hate.objects.get(id=id) 
    return render_to_response("twits/total_vote.html", {'twit': twit})

def gen_token(request):
    temp = SecretBallotIpUseragentMiddleware()
    token = temp.generate_token(request)
    return token

def greatest_hates(request):
    companies = Company.objects.all()[0:9]
    categories = Category.objects.all()
    twit_list = Paginator(Hate.objects.order_by('-hate_vote'), 25)
    page = int(request.GET.get('page', '1'))
    twits = twit_list.page(page)
    return render_to_response("twits/greatest.html", {'twits': twits, 'companies': companies, 'categories': categories})

def search(request):
    companies = Company.objects.all()[0:9]
    categories = Category.objects.all()
    if 'q' in request.GET:
        term = request.GET['q']
        comp_list = Paginator(Company.objects.filter(Q(company_name__icontains=term) | Q(company_description__icontains=term)), 5)
        page = int(request.GET.get('page', '1'))
        comp = comp_list.page(page)

    if comp is []:
       return HttpResponseRedirect('/')
    return render_to_response("twits/search.html", {'comp': comp, 'companies': companies, 'categories': categories})

def hate_id(request, id):
    companies = Company.objects.all()[0:9]
    categories = Category.objects.all()
    twit = get_object_or_404(Hate, id=id)
    return render_to_response("twits/hate.html", {'twit': twit, 'companies': companies, 'categories': categories})

def company_list(request):
    companies = Company.objects.all()[0:9]
    categories = Category.objects.all()
    comp_list = Paginator(Company.objects.all(), 25)
    page = int(request.GET.get('page', '1'))
    comp = comp_list.page(page)
    return render_to_response("twits/company_list.html", {'companies': companies, 'categories': categories, 'comp': comp})