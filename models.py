from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from pcp.apps.account.models import PCPUser as User
from django.contrib.contenttypes import generic
from django.core import serializers
import simplejson


class DashboardView(models.Model):
    app             = models.CharField(max_length=100)
    view            = models.CharField(max_length=100)
    title           = models.CharField(max_length=100)
    description     = models.TextField(blank=True)
    default_config  = models.TextField(blank=True)
    
    def __unicode__(self):
        return u"%s (%s.dashboard.%s)" % (self.title, self.app, self.view)

    def get_config(self):
        try:
            return simplejson.loads(self.default_config)
        except ValueError:
            self.set_config({})
            return {}

    def set_config(self,value):
        self.default_config = simplejson.dumps(value)
        
    config = property(get_config, set_config)

    

class DashboardItem(models.Model):
    dashboard_view  = models.ForeignKey(DashboardView, related_name="related_dashboardview")
    user            = models.ForeignKey(User)
    ordernr         = models.IntegerField(blank=True, null=True)
    configuration   = models.TextField(blank=True)

    def __unicode__(self):
        return u"%s for %s" % (self.dashboard_view, self.user)
    
    def get_config(self):
        try:
            return simplejson.loads(self.configuration)
        except ValueError:
            self.set_config({})
            return {}
    
    def set_config(self,value):
        self.configuration = simplejson.dumps(value)
    config = property(get_config, set_config)
    
"""
[{"name":"something", "value": X, type="string|int|bool"}]
"""