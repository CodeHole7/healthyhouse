from django.contrib import messages
from django.utils.translation import ugettext as _
from oscar.core.loading import get_class

Applicator = get_class('basket.views', 'Applicator')
BaseVoucherAddView = get_class('basket.views', 'VoucherAddView')


class VoucherAddView(BaseVoucherAddView):
    """
    Overridden for patching `apply_voucher_to_basket` method.

    It is needed for implement opportunity to use
    `DosimeterOffer` and `Coupon` discounts together (both for one cart).
    """

    def apply_voucher_to_basket(self, voucher):
        """
        Overridden for patching call of `Applicator.apply` method.

        WARNINGS:
            - All code of this method is default implementation
            from bases class, except call of `Applicator.apply`.
        """

        if voucher.is_expired():
            messages.error(
                self.request,
                _("The '%(code)s' voucher has expired") % {
                    'code': voucher.code})
            return

        if not voucher.is_active():
            messages.error(
                self.request,
                _("The '%(code)s' voucher is not active") % {
                    'code': voucher.code})
            return

        is_available, message = voucher.is_available_to_user(self.request.user)
        if not is_available:
            messages.error(self.request, message)
            return

        self.request.basket.vouchers.add(voucher)

        # Raise signal
        self.add_signal.send(
            sender=self, basket=self.request.basket, voucher=voucher)

        # PATCHED PART START
        # =====================================================================

        # Just add `test=True` into call.
        Applicator().apply(
            self.request.basket,
            self.request.user,
            self.request,
            test=True)

        # =====================================================================
        # PATCHED PART END

        discounts_after = self.request.basket.offer_applications

        # Look for discounts from this new voucher
        found_discount = False
        for discount in discounts_after:
            if discount['voucher'] and discount['voucher'] == voucher:
                found_discount = True
                break
        if not found_discount:
            messages.warning(
                self.request,
                _("Your basket does not qualify for a voucher discount"))
            self.request.basket.vouchers.remove(voucher)
        else:
            messages.info(
                self.request,
                _("Voucher '%(code)s' added to basket") % {
                    'code': voucher.code})
