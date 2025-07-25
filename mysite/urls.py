"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# The next step is to configure the global URLconf in the mysite project to include the URLconf defined in polls.urls. 
# To do this, add an import for django.urls.include in mysite/urls.py and insert an include() in the urlpatterns list

# The path() function expects at least two arguments: route and view. The include() 
# function allows referencing other URLconfs. Whenever Django encounters include(), it chops off whatever part of the URL matched up to that point and sends the remaining string to the included URLconf for further processing.

# The idea behind include() is to make it easy to plug-and-play URLs.

urlpatterns = [
    path('', include("myapp.urls")),
    path('admin/', admin.site.urls),
]
