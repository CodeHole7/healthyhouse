from oscar.apps.checkout.utils import CheckoutSessionData as BaseCheckoutSessionData


class CheckoutSessionData(BaseCheckoutSessionData):
    """
    Overridden for:
    - Patching `ship_to_new_address` method.
    """

    def ship_to_new_address(self, address_fields):
        """
        Overridden for removing `phone_number.as_international`,
        because we have overridden the `phone_number` field, and now it is
        just CharField, so `as_international` property is not available now.
        """
        self._unset('shipping', 'new_address_fields')
        phone_number = address_fields.get('phone_number')
        if phone_number:
            # Phone number is stored as a PhoneNumber instance. As we store
            # strings in the session, we need to serialize it.
            address_fields = address_fields.copy()
        self._set('shipping', 'new_address_fields', address_fields)
