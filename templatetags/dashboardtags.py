from django import template
from django.template.loader import get_template
from django.template.defaultfilters import stringfilter
from django.utils import html
from django.core.urlresolvers import reverse
from django.conf import settings
from pcp.apps.dashboard import render_dashboard

try:
    from django.utils.safestring import mark_safe
except ImportError: # v0.96 and 0.97-pre-autoescaping compat
    def mark_safe(x): return x

    
from pcp.apps.dashboard.models import DashboardItem, DashboardView

def do_get_new_dashboard_views(parser, token):
    """
    Gets all dashboard items in variable.
    """
    error_message = "%r tag must be of format {%% %r as OBJECT %%}" % (token.contents.split()[0], token.contents.split()[0])
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, error_message
    if split[1] != 'as':
        raise template.TemplateSyntaxError, error_message
    return GlobaleDashboardNewViewsNode(split[2])

class GlobaleDashboardNewViewsNode(template.Node):
    def __init__(self, context_name):
        self.context_name = context_name
    def render(self, context):
        context[self.context_name] = DashboardView.objects.exclude(related_dashboardview__user=context["user"]).order_by("title")
        return ''

def do_get_dashboard_views(parser, token):
    """
    Gets all dashboard items in variable.
    """
    error_message = "%r tag must be of format {%% %r as OBJECT %%}" % (token.contents.split()[0], token.contents.split()[0])
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, error_message
    if split[1] != 'as':
        raise template.TemplateSyntaxError, error_message
    return GlobaleDashboardViewsNode(split[2])

class GlobaleDashboardViewsNode(template.Node):
    def __init__(self, context_name):
        self.context_name = context_name
    def render(self, context):
        context[self.context_name] = DashboardView.objects.order_by("title")
        return ''
    

def do_get_user_dashboard_items(parser, token):
    """
    Gets all dashboard items in variable.
    """
    error_message = "%r tag must be of format {%% %r as OBJECT %%}" % (token.contents.split()[0], token.contents.split()[0])
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, error_message
    if split[1] != 'as':
        raise template.TemplateSyntaxError, error_message
    return GlobaleUserDashboardItemsNode(split[2])

class GlobaleUserDashboardItemsNode(template.Node):
    def __init__(self, context_name):
        self.context_name = context_name
    def render(self, context):
        context[self.context_name] = DashboardItem.objects.filter(user=context["user"]).order_by("ordernr")
        return ''

def do_render_dashboard(parser, token):
    """
    Renders a Dashboard Item
    """
    error_message = "%r tag must be of format {%% %r DASHBOARDITEM %%}" % (token.contents.split()[0], token.contents.split()[0])
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, error_message
    return RenderDashboardNode(split[1])

class RenderDashboardNode(template.Node):
    def __init__(self, context_name):
        self.context_name = context_name

    def render(self, context):
        return render_dashboard(context[self.context_name], context)

register = template.Library()
register.tag('render_dashboard', do_render_dashboard)
register.tag('get_user_dashboard_items', do_get_user_dashboard_items)
register.tag('get_dashboard_views', do_get_dashboard_views)
register.tag('get_new_dashboard_views', do_get_new_dashboard_views)
