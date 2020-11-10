from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from markdown_deux import markdown
from comments.models import Comment
# Create your models here.



class PostManager(models.Manager):
    # overriding the Posts.objects.active() method by adding filters
    def active(self, *args, **kwargs):
        return super(PostManager, self).filter(draft=False).filter(publish__lte=timezone.now())


def upload_location(instance, filename):
    # PostModel = instance.__class__
    # new_id = PostModel.objects.order_by("id").last().id + 1
    return "%s/%s" % (instance.id, filename)


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=120)
    slug = models.SlugField(
        unique=True)  # It is a way of generating a valid URL, generally using data already obtained.
    content = models.TextField()

    # image = models.FileField(upload_to=upload_location, null=True, blank=True)
    image = models.ImageField(upload_to=upload_location,
                              null=True,
                              blank=True,
                              height_field="height_field",
                              width_field="width_field",
                              )
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)

    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now=False, auto_now_add=False)

    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    objects = PostManager()  # registering with the ModelManager

    # this objects == Posts."objects".all(),
    # if in case, we write hello = PostManager()
    # then, we should use, Posts.hello.all()
    # objects is the convention

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:detail", kwargs={"slug": self.slug})
        # namespace:view_name

    class Meta:
        ordering = ["-timestamp", "-last_updated"]

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

    # if property, we dont want to call the method, instead mention instance.comments instead of comments()
    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)  # making url ready title Eg. hello ALl 1 -> hello-all-1
    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_post_receiver, sender=Post)
