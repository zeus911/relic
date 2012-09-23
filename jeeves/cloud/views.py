import uuid
import core
from cloud import aws
from cloud import forms
from cloud import models
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.http import Http404
from boto.ec2.autoscale import LaunchConfiguration


@login_required
def add(request):
    """
    Create a new cloud
    """
    message = ''
    if request.method == 'POST':
        form = forms.CloudForm(request.POST)
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.owner = request.user
            form_instance.uuid = uuid.uuid4()
            form_instance.save()
            message = 'Your cloud has been created'
            form = forms.CloudForm()
            return redirect('/cloud')
    else:
        form = forms.CloudForm()

    return direct_to_template(request,
        'cloud/add.html',
        {
            'request': request,
            'form': form,
            'message': message
        })


@login_required
def cluster(request, uuid):
    """
    List all clusters
    """
    try:
        cloud = models.Cloud.objects.get(uuid=uuid)
    except models.Cloud.DoesNotExist:
        raise Http404
    return direct_to_template(request,
        'cloud/cluster.html',
        {
            'request': request,
            'cloud': cloud,
            'clusters': models.Cluster.objects.filter()
        })


@login_required
def cluster_add(request, uuid):
    """
    Create a new cluster
    """
    try:
        cloud = models.Cloud.objects.get(uuid=uuid)
    except models.Cloud.DoesNotExist:
        raise Http404

    message = ''

    if request.method == 'POST':
        form = forms.ClusterForm(request.POST)
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.cloud = models.Cloud.objects.get(uuid=uuid)
            form_instance.save()
            message = 'Your cloud has been created'
            form = forms.CloudForm()
            return redirect('/cloud/%s/cluster' % cloud.uuid)
    else:
        form = forms.ClusterForm()

    return direct_to_template(request,
        'cloud/cluster_add.html',
        {
            'request': request,
            'form': form,
            'message': message,
            'cloud': cloud
        })


@login_required
def edit(request, uuid):
    """
    Edit preferences in a Cloud
    """
    cloud = models.Cloud.objects.get(uuid=uuid)

    if request.method == 'POST':
        form = forms.CloudForm(request.POST, instance=cloud)
        if form.is_valid():
            form.save()

            return redirect('/cloud/%s' % uuid)
    else:
        form = forms.CloudForm(instance=cloud)

    return direct_to_template(request,
        'cloud/cloud_edit.html',
        {
            'request': request,
            'form': form,
            'cloud': cloud
        })


@login_required
def index(request, uuid):
    """
    The overview of a single cloud
    """
    try:
        cloud = models.Cloud.objects.get(uuid=uuid)
    except models.Cloud.DoesNotExist:
        raise Http404

    return direct_to_template(request,
        'cloud/cloud_index.html',
        {
            'request': request,
            'cloud': cloud
        })


@login_required
def launch_config(request, uuid):
    """
    List all launch configurations
    """
    try:
        cloud = models.Cloud.objects.get(uuid=uuid)
    except models.Cloud.DoesNotExist:
        raise Http404

    conn = aws.HANDLER.get_as_connection(uuid)
    launch_configs = conn.get_all_launch_configurations()

    return direct_to_template(request,
        'cloud/launch_config.html',
        {
            'request': request,
            'cloud': cloud,
            'launch_configs': launch_configs
        })


@login_required
def launch_config_add(request, uuid):
    """
    Create a new launch configuration
    """
    try:
        cloud = models.Cloud.objects.get(uuid=uuid)
    except models.Cloud.DoesNotExist:
        raise Http404

    message = ''

    if request.method == 'POST':
        form = forms.LaunchConfigForm(request.POST)
        print "OK"
        if form.is_valid():
            conn = aws.HANDLER.get_as_connection(uuid)
            conn.create_launch_configuration(LaunchConfiguration(
                name=form.cleaned_data['name'],
                image_id=form.cleaned_data['image_id'],
                key_name=form.cleaned_data['key_name'],
                security_groups=[],
                user_data=form.cleaned_data['user_data'],))
            message = 'Your launch config has been created'
            return redirect('/cloud/%s/launch_config' % cloud.uuid)
    else:
        conn = aws.HANDLER.get_ec2_connection(uuid)
        sgs = conn.get_all_security_groups()
        security_groups = []
        for sg in sgs:
            security_groups.append((sg.name, sg.name))
        print security_groups
        form = forms.LaunchConfigForm(sg_choices=security_groups)

    return direct_to_template(request,
        'cloud/launch_config_add.html',
        {
            'request': request,
            'form': form,
            'message': message,
            'cloud': cloud
        })


@login_required
def list(request):
    """
    Show the clouds registered for the authenticated user
    """
    return direct_to_template(request,
        'cloud/list.html',
        {
            'request': request,
            'clouds': core.models.Account.clouds(request.user)
        })


@login_required
def security_group(request, uuid):
    """
    List all security groups
    """
    try:
        cloud = models.Cloud.objects.get(uuid=uuid)
    except models.Cloud.DoesNotExist:
        raise Http404

    conn = aws.HANDLER.get_ec2_connection(uuid)
    security_groups = conn.get_all_security_groups()
    return direct_to_template(request,
        'cloud/security_group.html',
        {
            'request': request,
            'cloud': cloud,
            'security_groups': security_groups
        })
