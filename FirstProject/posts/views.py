from urllib.parse import quote_plus

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from comments.forms import CommentForm
from comments.models import Comment
from .forms import PostForm
from .models import Post


# Create your views here.


def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = PostForm(request.POST or None, request.FILES or None)   # request.POST or None performs form validations if request type == POST, else no validations
    # if request.method == "POST":
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save() # save to db
        messages.success(request, "Successfully created :)")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": form,
        "title": "Create Form",
        "submit": "Create"
    }
    return render(request, "post_form.html", context)


# def post_detail(request, slug=None):
#     # instance = Post.objects.get(id=20)  # get object or exception
#     instance = get_object_or_404(Post, slug=slug)
#     if instance.publish > timezone.now().date() or instance.draft:
#         if not request.user.is_staff or not request.user.is_superuser:
#             raise Http404
#
#     # For sharing links
#     share_string = quote_plus(instance.content)
#
#     initial_data = {
#         "content_type": instance.get_content_type,
#         "object_id": instance.id
#     }
#     comments_form = CommentForm(request.POST or None, initial=initial_data)
#     if comments_form.is_valid():
#         c_type = comments_form.cleaned_data.get("content_type")
#         content_type = ContentType.objects.get(model=c_type)
#         object_id = comments_form.cleaned_data.get("object_id")
#         content = comments_form.cleaned_data.get("content")
#         new_comment, created = Comment.objects.get_or_create(
#             user=request.user,
#             content_type=content_type,
#             object_id=object_id,
#             content=content
#
#         )
#         if created:
#             print("it worked")
#         else:
#             print("not working")
#
#     # For comments
#     # comments = Comment.objects.filter_by_instance(instance=instance)
#     # adding comments as a property to Post and getting it
#     comments = instance.comments  # comments is a property of Post
#     context = {
#         "instance": instance,
#         "title": "Detail",
#         "share_string": share_string,
#         "comments": comments,
#         "comments_form": comments_form,
#     }
#     # initial_data = {
#     #     "content_type": instance.get_content_type,
#     #     "object_id": instance.id
#     # }
#     # form = CommentForm(request.POST or None, initial=initial_data)
#     # if form.is_valid():
#     #     c_type = form.cleaned_data.get("content_type")
#     #     content_type = ContentType.objects.get(model=c_type)
#     #     obj_id = form.cleaned_data.get('object_id')
#     #     content_data = form.cleaned_data.get("content")
#     #     new_comment, created = Comment.objects.get_or_create(
#     #         user=request.user,
#     #         content_type=content_type,
#     #         object_id=obj_id,
#     #         content=content_data
#     #     )
#     #
#     # comments = instance.comments
#     # context = {
#     #     "title": instance.title,
#     #     "instance": instance,
#     #     "share_string": share_string,
#     #     "comments": comments,
#     #     "comment_form": form,
#     # }
#     return render(request, "post_detail.html", context)


def post_list(request):

    # if request.user.is_authenticated:
    #     context = {
    #         "title": "My userlist"
    #     }
    # else:
    #     context = {
    #         "title": "List"
    #     }

    # filtering method 1
    # queryset_list = Post.objects.filter(draft=False).filter(publish__lte=timezone.now()) # .all()        # .order_by("-timestamp")

    # filtering using ModelManager method 2
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    queryset_list = Post.objects.active()        # .order_by("-timestamp")
    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
                ).distinct()         # Q package is used for searching
    paginator = Paginator(queryset_list, 3)  # Show 10 posts per page.
    page_request_var = 'page'
    page_number = request.GET.get(page_request_var)
    queryset = paginator.get_page(page_number)

    context = {
        "obj_list": queryset,
        "title": "My userlist",
        "page_request_var": page_request_var
    }

    return render(request, "post_list.html", context)


def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None,   # request.POST or None performs form validations if request type == POST, else no validations
                    request.FILES or None,   # request for files if present
                    instance=instance,      # if instance not None, data is filled in fields, else empty
                    )
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()  # save to db
        messages.success(request, "Changes saved! :)")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "instance": instance,
        "title": "Edit",
        "form": form,
        "submit": """Save Changes""" # only "Save" is printing, after space not printing, why?
    }
    return render(request, "post_form.html", context)


def post_delete(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request, "Deleted :)")
    return redirect("posts:list")                # namespace:viewname



def post_detail(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    if instance.publish > timezone.now().date() or instance.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404

    share_string = quote_plus(instance.content)

    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id
    }
    print("Hello0")
    form = CommentForm(request.POST or None, initial=initial_data)
    if form.is_valid():
        print("Hello1")
        c_type = form.cleaned_data.get("content_type")
        # content_type = ContentType.objects.get(model=c_type)
        content_type = ContentType.objects.get(
            app_label__iexact="posts", model__iexact=c_type
        )
        print("Hello2")
        obj_id = form.cleaned_data  .get('object_id')
        content_data = form.cleaned_data.get("content")
        new_comment, created = Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
            content=content_data
        )

        if created:
            print("Created")


    comments = instance.comments
    context = {
        "title": instance.title,
        "instance": instance,
        "share_string": share_string,
        "comments": comments,
        "comments_form":form,
    }
    return render(request, "post_detail.html", context)