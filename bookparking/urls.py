from django.urls import path
from . import views




urlpatterns=[
    path('', views.index, name="home"),
    path('parking-prices', views.pricing, name="pricing"),
    path('spaces/<str:parking_location>', views.spaces, name="spaces"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path('your-bookings', views.bookings, name="bookings"),
    path('parking-admin', views.parking_admin, name="admin_home"),
    path('login', views.login_user, name="login_user"),
    path('sign-up', views.register_user, name="register_user"),
    path('auth/logout', views.logout_user, name="logout"),
    path('book/<int:space_id>/', views.book , name="book"),
    path('create-space/<str:location>', views.create_spaces, name="create-space"),
    path('receipt/<int:pk>', views.billing_receipt, name="receipt"),
    path('delete/<int:pk>', views.delete_booking, name="delete_booking"),
    path('update/<int:pk>', views.update, name="update")

]

