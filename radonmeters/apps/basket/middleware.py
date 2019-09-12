from django.contrib import messages
from django.utils.translation import ugettext as _
from oscar.apps.basket.middleware import Basket
from oscar.apps.basket.middleware import BasketMiddleware as BaseBasketMiddleware
from oscar.core.compat import user_is_authenticated


class BasketMiddleware(BaseBasketMiddleware):
    """
    Overridden for changing logic in `get_basket` method.
    """

    def get_basket(self, request):
        """
        Overridden for adding message about merging carts
        only for old customers.

        Most part of code in this method just copy-pasted from default method,
        only code between START CUSTOM REALISATION and END CUSTOM REALISATION
        is custom.
        """

        if request._basket_cache is not None:
            return request._basket_cache

        num_baskets_merged = 0
        manager = Basket.open
        cookie_key = self.get_cookie_key(request)
        cookie_basket = self.get_cookie_basket(cookie_key, request, manager)

        if hasattr(request, 'user') and user_is_authenticated(request.user):
            # Signed-in user: if they have a cookie basket too, it means
            # that they have just signed in and we need to merge their cookie
            # basket into their user basket, then delete the cookie.
            try:
                basket, __ = manager.get_or_create(owner=request.user)
            except Basket.MultipleObjectsReturned:
                # Not sure quite how we end up here with multiple baskets.
                # We merge them and create a fresh one
                old_baskets = list(manager.filter(owner=request.user))
                basket = old_baskets[0]
                for other_basket in old_baskets[1:]:
                    self.merge_baskets(basket, other_basket)
                    num_baskets_merged += 1

            # Assign user onto basket to prevent further SQL queries when
            # basket.owner is accessed.
            basket.owner = request.user

            if cookie_basket:
                self.merge_baskets(basket, cookie_basket)
                num_baskets_merged += 1
                request.cookies_to_delete.append(cookie_key)

            # START CUSTOM REALISATION:
            # =================================================================

            # TODO: Need more safe method to understand user it's new customer.

            # Check that user in request is previously registered customer.
            # We need to use `buffer_seconds` because:
            # `last_login` - `date_joined` can be equal with several seconds.
            user = request.user
            buffer_seconds = 2
            diff_seconds = (user.last_login - user.date_joined).total_seconds()
            is_old_customer = diff_seconds > buffer_seconds

            # Add warning message about merging carts.
            if is_old_customer and num_baskets_merged > 0:
                messages.warning(
                    request,
                    _("We have merged a basket from a previous session. "
                      "Its contents might have changed."))

            # =================================================================
            # END CUSTOM REALISATION

        elif cookie_basket:
            # Anonymous user with a basket tied to the cookie
            basket = cookie_basket
        else:
            # Anonymous user with no basket - instantiate a new basket
            # instance.  No need to save yet.
            basket = Basket()

        # Cache basket instance for the during of this request
        request._basket_cache = basket

        return basket
