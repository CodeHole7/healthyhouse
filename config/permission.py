def custom_access_fn(user, url_name, url_args=None, url_kwargs=None):
    if not user.is_superuser and user.is_staff:

        #Catalogue
        if url_name == 'dashboard:catalogue-product-list':
            return False
        if url_name == 'dashboard:catalogue-class-list':
            return False
        if url_name == 'dashboard:catalogue-category-list':
            return False
        if url_name == 'dashboard:range-list':
            return False
        if url_name == 'dashboard:stock-alert-list':
            return False

        #fulfillments
        if url_name == 'dashboard:dosimeter-list':
            return False
        if url_name == 'dashboard:default-product-list':
            return False
        if url_name == 'dashboard:order-stats':
            return False
        if url_name == 'dashboard:partner-list':
            return False
        if url_name == 'dashboard:shipment-list':
            return False

        #Customers
        if url_name == 'dashboard:users-index':
            return False
        if url_name == 'dashboard:user-alert-list':
            return False

        #Offers Nav
        if url_name == 'dashboard:offer-list':
            return False
        if url_name == 'dashboard:voucher-list':
            return False
        if url_name == 'dashboard:send-voucher':
            return False

        #Content nav
        if url_name == 'dashboard:promotion-list':
            return False
        if url_name == 'dashboard:promotion-list-by-page':
            return False
        if url_name == 'dashboard:promotion':
            return False
        if url_name == 'dashboard:page-list':
            return False
        if url_name == 'dashboard:comms-list':
            return False
        if url_name == 'dashboard:reviews-list':
            return False
        
        #Reports
        if url_name == 'dashboard:reports-index':
            return False   

        #owners
        # if url_name == 'dashboard:owner-summary':
        #     return False
        # if url_name == 'dashboard:owner-report-template-list':
        #     return False

        #instructions 
        if url_name == 'dashboard:instruction-template-list':
            return False
        
        print(url_name)
        return True
    # print(url_name)
    return True