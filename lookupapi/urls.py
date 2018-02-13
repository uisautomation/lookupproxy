"""
The default URL mapping for :py:mod:`lookupapi` can be added to the global URL configuration in the
following way:

.. code::

    from django.urls import include

    # ...

    urlpatterns = [
        # ...
        path('', include('lookupapi.urls')),
        # ...
    ]

"""
from django.urls import path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from . import views

schema_view = get_schema_view(
   openapi.Info(
      title="Lookup API",
      default_version='v1',
      description="University of Cambridge Lookup API",
      # terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="automation@uis.cam.ac.uk"),
      # license=openapi.License(name="BSD License"),
   ),
   validators=['flex', 'ssv'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)
"""
A configured drf-yasg schema view. The default URL config renders only the schema document but you
can use this in your URL config to render a Swagger UI for the API:

.. code::

    # yourproject/urls.py
    from django.urls import path
    from lookupapi.urls import schema_view

    urlpatterns = [
        # ...
        path('ui', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
        # ...
    ]

"""


urlpatterns = [
    path('attributes/people', views.PersonFetchAttributes.as_view(), name='person-attributes'),
    path('people', views.PersonList.as_view(), name='person-list'),
    path('people/token/self', views.PersonSelf.as_view(), name='person-token-self'),
    path('people/<scheme>/<identifier>', views.Person.as_view(), name='person-detail'),

    path('groups/<groupid>', views.Group.as_view(), name='group-detail'),

    path('institutions', views.InstitutionList.as_view(), name='institution-list'),
    path('institutions/<instid>', views.Institution.as_view(), name='institution-detail'),
    path('attributes/institutions', views.InstitutionFetchAttributes.as_view(),
         name='institution-attributes'),

    # See https://stackoverflow.com/questions/43380939/ for why this is "healthz".
    path('healthz', views.Health.as_view(), name='healthz'),

    # Schema documents
    re_path(r'^swagger(?P<format>.json|.yaml)$', schema_view.without_ui(cache_timeout=None),
            name='schema-json'),
]
