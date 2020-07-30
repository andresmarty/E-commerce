from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/<int:listing_id>", views.product, name="product"),
    path("listings/endbid/<int:listing_id>", views.endBid, name="endBid"),
    path("listings/watchlist/add/<int:listing_id>", views.addWatchList, name="addWatchList"),
    path("listings/watchlist/remove/<int:listing_id>", views.removeWatchList, name="removeWatchList"),
    path("listings/comments/<int:listing_id>", views.addComment, name="addComment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listings/categories", views.categories, name="categories"),
    path("listings/categories/<str:category>", views.getListingByCategory, name="getListingByCategory"),
    path("add", views.add, name="add")
]
