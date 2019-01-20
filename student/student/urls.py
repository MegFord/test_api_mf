from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from tastypie.api import Api
from api.resources import StudentResource, CourseResource


v1_api = Api(api_name='v1')
v1_api.register(StudentResource())
v1_api.register(CourseResource())

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/', include(v1_api.urls)),
]
