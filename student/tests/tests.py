import datetime
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from api.models import Course, Student, Days
from functools import wraps


class TestStudent(TestCase):
    def setUp(self):
        python_class = Course.objects.create(
            title='Intro to Python',
            course_id='CS 251',
            prof_last_name='Teller',
            prof_first_name='Dana',
            start_time='9:00',
            end_time='12:00',
            year=2019,
            term='Spring'
        )
        python_class.save()
        class_day1 = Days.objects.create(day='Tuesday')
        class_day1.save()
        python_class.class_days.add(class_day1)
        st = Student.objects.create(
            first_name='Maritza',
            last_name='Sunil',
            username='msunil@test.com',
            password='pass',
            student_id='50575'
        )
        st.courses.add(python_class)
        st.save()

    def test_student_correct(self):
        st_1 = Student.objects.get(first_name='Maritza')
        acad_class = st_1.courses.all()[0]
        self.assertEqual(acad_class.title, 'Intro to Python')
        self.assertEqual(acad_class.class_days.all()[0].day, 'Tuesday')

    def test_student_update(self):
        st_1 = Student.objects.get(first_name='Maritza')
        self.assertEqual(st_1.student_id, '50575')
        st_1.student_id = '12345'
        st_1.save()
        self.assertEqual(st_1.student_id, '12345')

    def test_student_delete(self):
        new_count = Student.objects.count() - 1
        st_1 = Student.objects.get(first_name='Maritza')
        st_1.delete()
        self.assertEqual(Student.objects.count(), new_count)


class StudentResourceTest(ResourceTestCaseMixin, TestCase):
    def setUp(self):
        super(StudentResourceTest, self).setUp()
        python_class = Course.objects.create(
            title='Intro to Python',
            course_id='CS 251',
            prof_last_name='Teller',
            prof_first_name='Dana',
            start_time='9:00',
            end_time='13:00',
            year=2019,
            term='Spring'
        )
        python_class.save()
        class_day1 = Days.objects.create(day='Monday')
        class_day1.save()
        class_day2 = Days.objects.create(day='Tuesday')
        class_day2.save()
        python_class.class_days.add(class_day1, class_day2)
        st = Student.objects.create(
            first_name='Maritza',
            last_name='Sunil',
            username='msunil@test.com',
            password='pass',
            student_id='50575'
        )
        st.save()
        st.courses.add(python_class)
        st2 = Student.objects.create(
            first_name='Frank',
            last_name='Teller',
            username='ftellerl@test.com',
            password='pass',
            student_id='40324'
        )
        st2.save()

    def get_credentials(self):
        return self.create_basic(username='msunil@test.com', password='pass')

    def test_get_list_json(self):
        st_1 = Student.objects.get(first_name='Maritza')
        resp = self.api_client.get(
            '/api/v1/student/',
            format='json',
            authentication=self.get_credentials()
        )
        self.assertValidJSONResponse(resp)
        obj = self.deserialize(resp)['objects']
        self.assertEqual(obj[0]['first_name'], 'Maritza')
        self.assertEqual(obj[1]['first_name'], 'Frank')

    def test_get_single_student(self):
        st = Student.objects.get(first_name='Maritza')
        uri = '/api/v1/student/{0}/'.format(st.pk)
        resp = self.api_client.get(
            uri,
            format='json',
            authentication=self.get_credentials()
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.deserialize(resp)['first_name'], 'Maritza')

    def test_get_single_student_classes(self):
        st = Student.objects.get(first_name='Maritza')
        uri = '/api/v1/student/{0}/courses/'.format(st.pk)
        resp = self.api_client.get(
            uri,
            format='json',
            authentication=self.get_credentials()
        )
        self.assertEqual(resp.status_code, 200)
        course_title = self.deserialize(resp)['courses'][0]['title']
        self.assertEqual(course_title, 'Intro to Python')

    def test_create_student(self):
        new_count = Student.objects.count() + 1
        python_class = Course.objects.get(title='Intro to Python')
        python_cl_uri = '/api/v1/course/{0}/'.format(python_class.pk)
        post_data = {
            "first_name": "Nancy",
            "last_name": "Youn",
            "username": "nancy@example.com",
            "password": "pass",
            "courses": [python_cl_uri]
        }
        resp = self.api_client.post(
            '/api/v1/student/',
            format='json',
            data=post_data,
            authentication=self.get_credentials()
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Student.objects.count(), new_count)

    def test_put_detail(self):
        count = Student.objects.count()
        st = Student.objects.get(first_name='Frank')
        uri = '/api/v1/student/{0}/'.format(st.pk)
        original_data = self.deserialize(
            self.api_client.get(
                uri,
                format='json',
                authentication=self.get_credentials()
            )
        )
        new_data = original_data.copy()
        self.assertEqual(new_data['courses'], [])
        python_class = Course.objects.get(title='Intro to Python')
        python_cl_uri = '/api/v1/course/{0}/'.format(python_class.pk)
        new_data['courses'] = [python_cl_uri]
        self.api_client.put(
            uri,
            format='json',
            data=new_data,
            authentication=self.get_credentials()
        )
        self.assertEqual(Student.objects.count(), count)
        st = Student.objects.get(pk=st.pk)
        st_courses = list(st.courses.values_list('pk', flat=True))
        self.assertEqual(st_courses, [python_class.pk])

    def test_delete_detail(self):
        new_count = Student.objects.count() - 1
        st = Student.objects.get(first_name='Frank')
        uri = '/api/v1/student/{0}/'.format(st.pk)
        self.api_client.delete(
            uri,
            format='json',
            authentication=self.get_credentials()
        )
        self.assertEqual(Student.objects.count(), new_count)


class CourseTest(TestCase):

    def setUp(self):
        python_class = Course.objects.create(
            title='Intro to Python',
            course_id='CS 251',
            prof_last_name='Teller',
            prof_first_name='Dana',
            start_time='9:00',
            end_time='13:00',
            year=2019,
            term='Spring'
        )
        python_class.save()
        class_day1 = Days.objects.create(day='Monday')
        class_day1.save()
        class_day2 = Days.objects.create(day='Tuesday')
        class_day2.save()
        python_class.class_days.add(class_day1, class_day2)

    def test_course_correct(self):
        acad_class = Course.objects.get(title='Intro to Python')
        self.assertEqual(acad_class.course_id, 'CS 251')
        self.assertEqual(acad_class.class_days.all()[0].day, 'Monday')

    def test_course_update(self):
        acad_class = Course.objects.get(title='Intro to Python')
        self.assertEqual(acad_class.term, 'Spring')
        acad_class.term = 'Fall'
        acad_class.save()
        self.assertEqual(acad_class.term, 'Fall')

    def test_course_delete(self):
        new_count = Course.objects.count() - 1
        acad_class = Course.objects.get(title='Intro to Python')
        acad_class.delete()
        self.assertEqual(Course.objects.count(), new_count)


class CourseResourceTest(ResourceTestCaseMixin, TestCase):
    def setUp(self):
        super(CourseResourceTest, self).setUp()
        python_class = Course.objects.create(
            title='Intro to Python',
            course_id='CS 251',
            prof_last_name='Teller',
            prof_first_name='Dana',
            start_time='9:00',
            end_time='13:00',
            year=2019,
            term='Spring'
        )
        python_class.save()
        class_day1 = Days.objects.create(day='Monday')
        class_day1.save()
        class_day2 = Days.objects.create(day='Tuesday')
        class_day2.save()
        python_class.class_days.add(class_day1, class_day2)
        st = Student.objects.create(
            first_name='Maritza',
            last_name='Sunil',
            username='msunil@test.com',
            password='pass',
            student_id='50575'
        )
        st.save()

    def get_credentials(self):
        return self.create_basic(username='msunil@test.com', password='pass')

    def test_get_list_json(self):
        count = Course.objects.count()
        resp = self.api_client.get(
            '/api/v1/course/',
            format='json',
            authentication=self.get_credentials()
        )
        self.assertValidJSONResponse(resp)
        obj = self.deserialize(resp)['objects']
        self.assertEqual(obj[0]['title'], 'Intro to Python')

    def test_get_single_course(self):
        python_class = Course.objects.get(title='Intro to Python')
        uri = '/api/v1/course/{0}/'.format(python_class.pk)
        resp = self.api_client.get(
            uri,
            format='json',
            authentication=self.get_credentials()
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.deserialize(resp)['term'], 'Spring')

    def test_create_course(self):
        new_count = Course.objects.count() + 1
        post_data = {
            "course_id": "CS 400",
            "end_time": "11:00",
            "prof_first_name": "Donald",
            "prof_last_name": "Knuth",
            "start_time": "09:00",
            "term": "Winter",
            "title": "The Art of Computer Programming",
            "year": 1967
        }
        resp = self.api_client.post(
            '/api/v1/course/',
            format='json',
            data=post_data,
            authentication=self.get_credentials()
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Course.objects.count(), new_count)

    def test_put_detail(self):
        count = Course.objects.count()
        python_class = Course.objects.get(title='Intro to Python')
        uri = '/api/v1/course/{0}/'.format(python_class.pk)
        original_data = self.deserialize(
            self.api_client.get(
                uri,
                format='json',
                authentication=self.get_credentials()
            )
        )
        new_data = original_data.copy()
        self.assertEqual(new_data['year'], 2019)
        new_data['year'] = 2017
        self.api_client.put(
            uri,
            format='json',
            data=new_data,
            authentication=self.get_credentials()
        )
        self.assertEqual(Course.objects.count(), count)
        python_class = Course.objects.get(pk=python_class.pk)
        self.assertEqual(python_class.year, 2017)

    def test_delete_detail(self):
        new_count = Course.objects.count() - 1
        python_class = Course.objects.get(title='Intro to Python')
        uri = '/api/v1/course/{0}/'.format(python_class.pk)
        self.api_client.delete(
            uri,
            format='json',
            authentication=self.get_credentials()
        )
        self.assertEqual(Course.objects.count(), new_count)
