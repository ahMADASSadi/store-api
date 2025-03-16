import re
from django.utils.functional import keep_lazy_text


class Utility:
    def __init__(self, prefix="prd"):
        self.prefix = prefix

    @keep_lazy_text
    def persian_slugify(self, prefix: str, title: str):
        product_name = re.sub(r'\s+', '-', title)
        product_slug = prefix if prefix else self.prefix + "-"
        product_slug += product_name
        return product_slug
