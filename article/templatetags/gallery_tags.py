from django import template
from wagtail.models import Page
from ..models import GalleryPage

register = template.Library()


@register.simple_tag
def get_galleries():
    return Page.objects.type(GalleryPage).live().public()
