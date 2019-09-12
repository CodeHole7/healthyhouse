import logging

from oscar.apps.offer import results
from oscar.core.loading import get_class
from oscar.core.loading import get_model

BaseApplicator = get_class('offer.applicator', 'Applicator')
ConditionalOffer = get_model('offer', 'ConditionalOffer')

logger = logging.getLogger('oscar.offers')


class Applicator(BaseApplicator):
    """
    Overridden for adding custom logic. This needed for add opportunity
    to use offers and coupons together (both types of discounts in one cart).
    """

    def apply(self, basket, user=None, request=None, test=False):
        """
        Overridden for adding new argument `test`.

        This is needed for marking that current call was initialized just
        for test that some discounts can be applied.
        """

        offers = self.get_offers(basket, user, request)
        self.apply_offers(basket, offers, test=test)

    def apply_offers(self, basket, offers, test=False):
        """
        Overridden for implement opportunity to use
        `DosimeterOffer` and `Coupon` discounts together (both for one cart).

        WARNING:
            Has new kwarg `test`. This flag shows us that we need
            to apply `DosimeterOffer` or not.
        """

        dosimeter_offer = None
        applications = results.OfferApplications()

        for offer in offers:

            # Exclude offer for dosimeters from list.
            if offer.slug == 'dosimeters':
                dosimeter_offer = offer
                continue

            # Hack for adding Voucher, when other offers have applied in cart.
            if test and offer.offer_type == 'Voucher':

                # Check that cart hasn't other voucher.
                if len([o for o in offers if o.offer_type == 'Voucher']) > 1:
                    continue
                else:
                    result = offer.apply_benefit(basket)
                    applications.add(offer, result)
                    continue

            num_applications = 0
            while num_applications < offer.get_max_applications(basket.owner):
                # Return to default realisation (for other offers):
                result = offer.apply_benefit(basket)
                num_applications += 1
                if not result.is_successful:
                    break
                applications.add(offer, result)
                if result.is_final:
                    break

        # When dosimeter offer in offers and it is not a request
        # for adding coupon, apply discount for dosimeters.
        if dosimeter_offer and not test:
            result = dosimeter_offer.apply_benefit(basket)
            if result.is_successful:
                applications.add(dosimeter_offer, result)

        # Store this list of discounts with the basket so it can be
        # rendered in templates
        basket.offer_applications = applications
