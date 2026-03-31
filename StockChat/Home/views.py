from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages

# Create your views here.
def home(request):
    # render the landing page template for the stock market website
    return render(request, 'Home/home.html')

def about(request):
    # render a simple about page for StockChat
    return render(request, 'Home/about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        content = request.POST['content']
        DOB = request.POST['DOB']
        # print(name,phone,email,content)
        if len(name) < 3 or len(email) < 5 or len(phone) < 10 or len(content) < 3:
            messages.add_message(request, messages.WARNING, 'Fill the form Correctly')
        else:
            #TODO : save the data in database            
            messages.add_message(request, messages.SUCCESS, 'Your Form has been sent!')

    return render(request,'Home/contact.html')