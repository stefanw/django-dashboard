from django import template
from django.http import HttpResponse
from django.conf import settings
from helper.modulehelper import get_class_from_module, get_module
from models import DashboardView

def get_dashboard_view_class(app_name, view_name):
    imp_str = "apps.%s.dashboard.%s" % (app_name,view_name)
    Dashboard_view = get_class_from_module(imp_str)
    return Dashboard_view
    
def get_all_dashboard_items():
    pass
        
def sync_dashboard_items():
    dashboard_classes_list = []
    added, synced, deleted = [], [], []
    for app_name in settings.INSTALLED_APPS:
        if not app_name.startswith("pcp.apps."): continue
        app = app_name.split('.')[-1]
        try:
            app_module = get_module("apps.%s.dashboard" % app)
        except ImportError:
            continue
        dashboard_classes = dir(app_module)
        for dashboard_class_str in dashboard_classes:
            dashboard_class = getattr(app_module,dashboard_class_str)
            if hasattr(dashboard_class, "__base__") and DashboardBaseView.__name__ == dashboard_class.__base__.__name__:
                dashboard_classes_list.append("%s.%s" % (app,dashboard_class.__name__))
                dashboard_view = DashboardView.objects.filter(app=app, view=dashboard_class.__name__)
                view_description = getattr(dashboard_class, "description", "")
                view_default_config = getattr(dashboard_class, "default_config", {})                
                view_title = getattr(dashboard_class,"title",None)
                if view_title is None:
                    raise Exception, "DashboardViewClass %s has no required attribute title" % dashboard_class.__name__
                if not len(dashboard_view):
                    dashboard_view = DashboardView(app          =   app, 
                                                  view          =   dashboard_class.__name__,
                                                  title         =   view_title, 
                                                  description   =   view_description, 
                                                  config        =   view_default_config)
                    dashboard_view.save()
                    added.append(dashboard_view.id)
                else:
                    dashboard_view = dashboard_view[0]
                    dashboard_view.title = unicode(view_title)
                    dashboard_view.description = unicode(view_description)
                    dashboard_view.config = view_default_config
                    dashboard_view.save()
                    synced.append(dashboard_view.id)
    dashboard_views = DashboardView.objects.all()
    for db_view in dashboard_views:
        if "%s.%s" % (db_view.app, db_view.view) not in dashboard_classes_list:
            deleted.append(db_view.id)
            db_view.delete()
    return (added, synced, deleted)
                
    
    
    
def render_dashboard(dashboard_item, global_context):
    # Get Context Class for dashboard_item.dashboard_view
    dashboard_view_class = get_dashboard_view_class(dashboard_item.dashboard_view.app, dashboard_item.dashboard_view.view)
    # Instantiate dashboard_view_class with global_context
    dashboard_view_obj = dashboard_view_class(global_context)
    # Get context from object
    dashboard_view_context = dashboard_view_obj.create_context(dashboard_item.config)
    # Update Context with dashboard_item
    dashboard_view_context.update({"dashboard_item": dashboard_item})
    # Create real Template Context
    view_context = template.Context(dashboard_view_context)
    template_name = "_%s" % dashboard_item.dashboard_view.view.lower()
    try:
        t = template.loader.get_template('%s/%s.html' % (dashboard_item.dashboard_view.app, template_name))
    except:
        if settings.TEMPLATE_DEBUG:
            raise
        return ''
    return '<!--%d-->\n%s' % (dashboard_item.id, t.render(view_context))
    
def render_dashboard_to_response(dashboard_item, global_context):
    return HttpResponse(render_dashboard(dashboard_item, global_context))
    
    
class DashboardBaseView(object):
    context = {}
    default_config = {}
    
    def __init__(self, global_context):
        self.global_context = global_context
    
    def create_context(self, config):
        own_config = getattr(self.__class__,"default_config",{})
        if config is not None:
            own_config.update(config)
        else:
            config = own_config
        self.__class__.context.update(self.get_context(self.global_context, config))
        return self.__class__.context
    
    def get_context(self, global_context, config):
        raise NotImplemented