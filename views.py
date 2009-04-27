# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import DashboardView, DashboardItem
from dashboard import render_dashboard_to_response, sync_dashboard_items
from django.contrib.auth.decorators import login_required

def index(request):
    return render_to_response("index.html",{})

def imprint(request):
    return render_to_response("imprint.html",{})

@login_required
def dashboard_view(request,view_id):
    if request.method=="POST":
        view_id = int(view_id)
        dashboard_view = DashboardView.objects.get(id=view_id)
        ordernr = DashboardItem.objects.count()
        dashboard_item = DashboardItem(dashboard_view=dashboard_view, configuration = dashboard_view.default_config, user=request.user, ordernr=ordernr)
        dashboard_item.save()
        return render_dashboard_to_response(dashboard_item, RequestContext(request))
    return HttpResponse("")
    
@login_required
def dashboard_item(request,item_id):
    item_id = int(item_id)
    try:
        dashboard_item = DashboardItem.objects.get(id=item_id, user=request.user)
    except DashboardItemDoesNotExist:
        raise Http404
    return render_dashboard_to_response(dashboard_item, RequestContext(request))

@login_required
def remove_item(request,item_id):
    if request.method=="POST":
        item_id = int(item_id)
        try:
            dashboard_item = DashboardItem.objects.get(id=item_id, user=request.user)
        except DashboardItemDoesNotExist:
            raise Http404
        dashboard_item.delete()
        return HttpResponse("OK")
    else:
        return HttpResponse("Fail")

@login_required
def save_dashboard(request):
    if request.method=="POST":
        dashboard_items = request.POST.getlist('dashboarditem[]')
        pos = 0
        user_dashboard_ids = []
        for dashboard_item in dashboard_items: 
            if dashboard_item == "None":
                pos+=1
                continue
            try:
                dashboard_item_id = int(dashboard_item)
                try:
                    dashboard_item = DashboardItem.objects.get(id = dashboard_item_id, user = request.user)
                except DashboardItem.DoesNotExist:
                    return HttpResponseBadRequest()
                dashboard_item.ordernr = pos
                dashboard_item.save()
                user_dashboard_ids.append(dashboard_item.id)
            except IndexError:
                return HttpResponseBadRequest()
            except ValueError:
                return HttpResponseBadRequest()
            pos += 1
        user_dashboards = DashboardItem.objects.filter(user = request.user)
        for ud in user_dashboards:
            if ud.id not in user_dashboard_ids:
                ud.delete()
    return HttpResponse("OK")
    
@login_required
def save_config(request, item_id):
    if request.method=="POST":
        try:
            dashboard_item = DashboardItem.objects.get(id=item_id)
        except DashboardItemDoesNotExit:
            raise Http404
        new_config = {}
        for k,v in dashboard_item.config.items():
            post_value = request.POST[k] if k in request.POST else None
            if post_value is not None:
                if isinstance(v,int):
                    try:
                        post_value = int(post_value)
                    except ValueError:
                        continue
                if isinstance(v,str):
                    try:
                        post_value = unicode(post_value)
                    except ValueError:
                        continue
                if isinstance(v,list):
                    post_value = request.POST.getlist(k)
                    temp_list = []
                    for p in post_value:
                        try:
                            temp_list.append(int(p))
                        except ValueError:
                            continue
                    post_value = temp_list
                new_config[k] = post_value
            else:
                new_config[k] = v
        dashboard_item.config = new_config
        dashboard_item.save()
    return render_dashboard_to_response(dashboard_item, RequestContext(request))
        
@login_required
def management(request):
    if request.user.is_staff:
        added, synced, deleted = sync_dashboard_items()
        dashboard_views = DashboardView.objects.all()
        for db_view in dashboard_views:
            if db_view.id in added:
                db_view.added = True
            if db_view.id in synced:
                db_view.synced = True
        deleted = len(deleted)
        return render_to_response("dashboard/management.html", RequestContext(request, {"dashboard_views": dashboard_views, "deleted":deleted}))
    else:
        return HttpResponseForbidden()

        