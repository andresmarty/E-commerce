from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.forms import ModelForm, Textarea, TextInput, NumberInput
from django.db.models import Max
from datetime import datetime

from .models import User, Listing, Comment, Bid

from django import forms


class ListingDTO:
    def __init__(self, title=None, date=None, description=None, currentBid=None, photo=None, id=None, active=None):
        self.title = title
        self.date = date
        self.description = description
        self.currentBid = currentBid
        self.photo = photo
        self.id = id
        self.active = active

class NewContentForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'startingBid', 'photo', 'category']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control input'}),
            'description': Textarea(attrs={'class': 'form-control textarea'}),
            'startingBid': NumberInput(attrs={'class': 'form-control input'}),
            'photo': TextInput(attrs={'class': 'form-control input'}),
            'category': TextInput(attrs={'class': 'form-control input'}),
        }
        labels = {
            'title': 'Product Name',
            'description': 'Add a Description',
            'startingBid': 'Initial Price',
            'photo': 'Add Url Photo',
            'category': 'Category',
        }

form = NewContentForm()

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bids']
        widgets = {
            'bids': NumberInput(attrs={'class': 'form-control inputNumber'}),
        }
        labels = {
            'bids': 'Insert Your Bid',
        }
form = BidForm()

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["comments"]
        widgets = {
            'comments': Textarea(attrs={'class': 'form-control comments', 'id': 'newComment',})
        }
        labels = {
            'comments': 'Leave a comment',
        }

form = CommentForm()

def index(request):
    listings = Listing.objects.all()

    listingDTOlist = []
    lastBid = None
    for listing in listings:
        listingDTO = ListingDTO()
        lastBid = Bid.objects.filter(listing=listing.id).aggregate(Max('bids'))["bids__max"]
        if lastBid is None:
            lastBid = listing.startingBid
        listingDTO.currentBid = lastBid
        listingDTO.title = listing.title
        listingDTO.date = listing.date
        listingDTO.photo = listing.photo
        listingDTO.description = listing.description
        listingDTO.id = listing.id
        listingDTO.active = listing.active
        listingDTOlist.append(listingDTO)

    return render(request, "auctions/index.html", {
        "listing": listingDTOlist,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.add_message(request, messages.SUCCESS, 'Log In Successful.')
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        messages.add_message(request, messages.SUCCESS, 'User registered.')
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# Add a Listing
@login_required(login_url="login")
def add(request):
    if request.method == "POST":
        form = NewContentForm(request.POST)
        if form.is_valid():
            user = User()
            username = User.objects.get(username=request.user.username)
            print(username)
            newListing = Listing()
            newListing.user = username
            newListing.title = form.cleaned_data["title"]
            newListing.description = form.cleaned_data["description"]
            newListing.startingBid = form.cleaned_data["startingBid"]
            newListing.photo = form.cleaned_data["photo"]
            newListing.category = form.cleaned_data["category"]
            newListing.save()
            messages.add_message(request, messages.SUCCESS, 'Listing Added.')
            return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/add.html",{
        "form": NewContentForm()
        })

#Product view
@login_required(login_url="login")
def product(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    startingBid = listing.startingBid
    form = BidForm(request.POST)
    formComment = CommentForm(request.POST)
    comments = Comment.objects.filter(listing=listing_id).values('comments', 'date', 'user')
    lastBid = Bid.objects.filter(listing=listing_id).aggregate(Max('bids'))["bids__max"]
    winner = Bid.objects.filter(bids=lastBid).values('user')
    username = User.objects.get(username=request.user.username)
    print(winner)
    if lastBid is None:
        lastBid = startingBid
        #Post Bid
    if request.method == "POST":
        if form.is_valid():
            bid = form.cleaned_data["bids"]
            newBid = Bid()
            if lastBid < bid:
                newBid.bids = bid
                newBid.listing = listing
                newBid.user = username
                newBid.save()
                messages.add_message(request, messages.SUCCESS, 'Bid Added.')
                return HttpResponseRedirect(f"{listing.id}")
        
    return render(request, "auctions/product.html", {
        "listing": listing,
        "form": form,
        "lastBid": lastBid,
        "formComment": formComment,
        "comments": comments,
        "winner": winner
    })

@login_required(login_url="login")
def addWatchList(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    startingBid = listing.startingBid
    form = BidForm(request.POST)
    formComment = CommentForm(request.POST)
    comments = Comment.objects.filter(listing=listing_id).values('comments', 'date', 'user')
    lastBid = Bid.objects.filter(listing=listing_id).aggregate(Max('bids'))["bids__max"]
    if lastBid is None:
        lastBid = startingBid
        
        # Add product to Watchlist
    if request.method == "POST":
        listing.watchlist = True
        listing.save()
        messages.add_message(request, messages.SUCCESS, 'Listing Added to Watchlist.')
        return HttpResponseRedirect(f"{listing.id}")

    return render(request, "auctions/product.html", {
        "listing": listing,
        "form": form,
        "lastBid": lastBid,
        "formComment": formComment,
        "comments": comments,
    })
    
@login_required(login_url="login")
def removeWatchList(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    startingBid = listing.startingBid
    form = BidForm(request.POST)
    formComment = CommentForm(request.POST)
    comments = Comment.objects.filter(listing=listing_id)
    lastBid = Bid.objects.filter(listing=listing_id).aggregate(Max('bids'))["bids__max"]
    if lastBid is None:
        lastBid = startingBid

        # Remove Product from WatchList
    if request.method == "POST":
        listing.watchlist = False
        listing.save()
        messages.add_message(request, messages.SUCCESS, 'Listing Removed from Watchlist.')
        return HttpResponseRedirect(f"{listing.id}")
    
    return render(request, "auctions/product.html", {
    "listing": listing,
    "form": form,
    "lastBid": lastBid,
    "formComment": formComment,
    "comments": comments,
    })


@login_required(login_url="login")
def addComment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    startingBid = listing.startingBid
    form = BidForm(request.POST)
    formComment = CommentForm(request.POST)
    comments = Comment.objects.filter(listing=listing_id)
    lastBid = Bid.objects.filter(listing=listing_id).aggregate(Max('bids'))["bids__max"]

    if lastBid is None:
        lastBid = startingBid


    # Add comment to product
    if request.method == "POST":
        if formComment.is_valid():
            username = request.user.username
            newComment = Comment()
            comment = formComment.cleaned_data["comments"]
            newComment.username = username
            newComment.comments = comment.capitalize()
            newComment.listing = listing
            newComment.save()
            messages.add_message(request, messages.SUCCESS, 'New Comment Added.')
            return HttpResponseRedirect(f"{listing.id}")

    return render(request, "auctions/product.html", {
    "listing": listing,
    "form": form,
    "lastBid": lastBid,
    "formComment": formComment,
    "comments": comments,
    })

@login_required(login_url="login")
def watchlist(request):
    listings = Listing.objects.filter(watchlist=True)
    return render(request, "auctions/watchlist.html",{
        "listings": listings,
    })

@login_required(login_url="login")
def categories(request):
    categories = Listing.objects.filter(active=True).values_list('category', flat=True).distinct()
    return render(request, "auctions/categories.html",{
        "categories": categories,
    })

@login_required(login_url="login")
def getListingByCategory(request, category):
    products = Listing.objects.filter(category=category)
    return render(request, "auctions/categorylisting.html",{
        "products": products
    })

def endBid(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    startingBid = listing.startingBid
    form = BidForm(request.POST)
    formComment = CommentForm(request.POST)
    comments = Comment.objects.filter(listing=listing_id).values('comments', 'date', 'user')
    lastBid = Bid.objects.filter(listing=listing_id).aggregate(Max('bids'))["bids__max"]
    if lastBid is None:
        lastBid = startingBid

    # EndBid
    if request.method == "POST":
        listing.active = False
        listing.save()
        return HttpResponseRedirect(f"{listing.id}")

    return render(request, "auctions/product.html", {
    "listing": listing,
    "form": form,
    "lastBid": lastBid,
    "formComment": formComment,
    "comments": comments,
    })











