import django
from django.conf.urls import url
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.utils import (
    dict_strip_unicode_keys,
    trailing_slash
)
from api.models import Student, Course


class StudentResource(ModelResource):
    courses = fields.ToManyField(
        'api.resources.CourseResource',
        'courses',
        full=True
    )

    class Meta:
        resource_name = 'student'
        queryset = Student.objects.all().prefetch_related('courses').all()
        allowed_methods = ('get', 'post', 'put')
        courses_allowed_methods = ('get')
        detail_allowed_methods = ('get', 'post', 'put', 'delete')
        excludes = ['email', 'password', 'is_superuser']
        authorization = Authorization()
        filtering = {
            'id': ALL_WITH_RELATIONS,
            'courses': ALL_WITH_RELATIONS
        }

    def base_urls(self):
        courses_url = url(
            r"^(?P<resource_name>{0})/(?P<pk>.*?)/courses{2}$".format(
                self._meta.resource_name,
                self._meta.detail_uri_name,
                trailing_slash()
            ),
            self.wrap_view("dispatch_courses"),
            name="api_courses"
        )

        base_urls = super(StudentResource, self).base_urls()
        base_urls.insert(0, courses_url)
        return base_urls

    def dispatch_courses(self, request, **kwargs):
        return self.dispatch('courses', request, **kwargs)

    def get_courses(self, request, **kwargs):
        exclude = [
            'is_staff',
            'is_active',
            'date_joined',
            'first_name',
            'last_login',
            'last_name',
            'id',
            'resource_uri',
            'student_id',
            'username'
        ]

        basic_bundle = self.build_bundle(request=request)

        try:
            obj = self.cached_obj_get(
                bundle=basic_bundle,
                **self.remove_api_resource_names(kwargs)
            )
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices(
                "More than one resource is found at this URI."
            )

        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)
        for key in exclude:
            bundle.data.pop(key)
        return self.create_response(request, bundle)


class CourseResource(ModelResource):
    class Meta:
        queryset = Course.objects.all()
        resource_name = 'course'
        allowed_methods = ('get', 'post', 'put', 'delete')
        authorization = Authorization()
