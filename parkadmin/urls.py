from django.urls import path
from . import views




urlpatterns=[
    path('', views.index, name="index"),
    path('user_management/', views.user_management, name="user"),
    path('parkingspace_management/', views.parkingspace_management, name="parkingspace_management"),
    path('booking_management/', views.booking_management, name="booking_management"),
    path('parking_management/', views.parking_management, name="parking_management"),
    path('reports/', views.reports, name="reports"),
    path('edit-user/<int:user_id>', views.edit_user, name="edit_user"),
    path('delete-user/<int:user_id>', views.delete_user, name="delete_user"),
    path('add-user', views.add_user, name="add_user"),
    path('add-spaces', views.add_spaces, name="add_spaces"),
    path('update-space/<int:space_id>', views.edit_space, name="edit_space"),
    path('delete-space/<int:space_id>', views.delete_space, name="delete_space"),
    path('update-book/<int:pk>', views.update_book, name="update_book"),
    path('delete-book/<int:pk>', views.delete_book, name="delete_book"),
    path('add-reservation', views.add_reservation, name="add_reservation"),
    path('add-parking', views.add_parking, name="add_parking"),
    path('edit-parking/<int:parking_id>', views.edit_parking, name="edit_parking"),
    path('delete-parking/<int:parking_id>', views.delete_parking, name="delete_parking"),
    path('login', views.login_admin, name="login_employee"),
    path('logout', views.logout_admin, name="logout_employee"),
    path('change_permission/<int:id>-<str:pk>', views.change_permission, name="change_permission")
    


    

]