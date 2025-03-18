from django.shortcuts import render


def document(request):
    return render(request, "help_faqs/documents.html")

def nursingproforma(request):
    return render(request, "help_faqs/nursingproforma.html")

def index(request):
    return render(request, "help_faqs/index.html")

def terms_conditions(request):
    return render(request, "help_faqs/terms_conditions.html")

def nursingindex(request):
    return render(request, "help_faqs/nursingindex.html")


def introduction(request):
    return render(request, "help_faqs/introduction.html")

def whoapply(request):
    return render(request, "help_faqs/whoapply.html")

def mandatory(request):
    return render(request, "help_faqs/mandatory.html")

def guide(request):
    return render(request, "help_faqs/guide.html")

def contactdetail(request):
    return render(request, "help_faqs/contactdetail.html")

def paymentdetail(request):
    return render(request, "help_faqs/paymentdetail.html")

