import json

import requests
from constance import config
from django.conf import settings
from django.core.exceptions import ValidationError
from oscar.core.loading import get_model

from common.tasks import mail_admins_task
from deliveries.serializers import ShippingAddressDeliverSerializer

Order = get_model('order', 'Order')
ShipmentLabel = get_model('deliveries', 'ShipmentLabel')


def get_company_data():
    return {
        'name': config.DELIVERY_NAME,
        'address1': config.DELIVERY_ADDRESS1,
        'address2': config.DELIVERY_ADDRESS2,
        'country_code': config.DELIVERY_COUNTRY_CODE,
        'zipcode': config.DELIVERY_ZIPCODE,
        'city': config.DELIVERY_CITY,
        'attention': config.DELIVERY_ATTENTION,
        'email': config.DELIVERY_EMAIL,
        'telephone': config.DELIVERY_TELEPHONE,
        'mobile': config.DELIVERY_MOBILE,
        'instruction': config.DELIVERY_INSTRUCTION
    }


def get_customer_data(order):
    return {
        **ShippingAddressDeliverSerializer(order.shipping_address).data,
        "name": order.get_user_name(),
        'email': order.email
    }


def get_parcels_data(order):
    return [{
        "number": config.DELIVERY_PARCEL_NUMBER,
        "weight": order.get_total_weight()
    }]


def package_out(order):
    """
    Prepares data for request for Output Label, based on received order.

    :param order: Instance of Order model.
    :return: Prepared dictionary for request.
    """
    return {
        "test_mode": settings.DELIVERY_TEST_MODE,
        "own_agreement": settings.DELIVERY_OUT_OWN_AGREEMENT,
        "label_format": settings.DELIVERY_OUT_LABEL_FORMAT,
        "product_code": settings.DELIVERY_OUT_PRODUCT_CODE,
        "service_codes": settings.DELIVERY_OUT_SERVICE_CODES,
        "automatic_select_service_point": settings.DELIVERY_OUT_AUTOMATIC_SELECT_SERVICE_POINT,
        "sender": get_company_data(),
        "receiver": get_customer_data(order),
        "parcels": get_parcels_data(order),
    }


def package_back(order):
    """
    Prepares data for request for Return Label, based on received order.

    :param order: Instance of Order model.
    :return: Prepared dictionary for request.
    """
    return {
        "test_mode": settings.DELIVERY_TEST_MODE,
        "own_agreement": settings.DELIVERY_BACK_OWN_AGREEMENT,
        "label_format": settings.DELIVERY_BACK_LABEL_FORMAT,
        "product_code": settings.DELIVERY_BACK_PRODUCT_CODE,
        "service_codes": settings.DELIVERY_BACK_SERVICE_CODES,
        # "automatic_select_service_point": settings.DELIVERY_BACK_AUTOMATIC_SELECT_SERVICE_POINT,
        "display_name": "return package for {}".format(order.get_user_name()),
        "description": "return package for {}".format(order.get_user_name()),
        "sender": get_customer_data(order),
        "receiver": get_company_data(),
        "parcels": get_parcels_data(order),
    }


def _create_shipment(data, title='Shipment'):
    """
    Makes request to 3rd-party API for create shipment

    :param data: data for request.
    :return: data of succeeded response. or ValidationError
    """

    # Prepare data for request.
    path = '/shipments'
    url = '%s%s' % (settings.DELIVERY_BASE_URL, path)
    pl_auth = (settings.DELIVERY_AUTH_LOGIN, settings.DELIVERY_AUTH_PASSWORD)

    # Make a request.
    r = requests.post(url=url, json=data, auth=pl_auth)

    # Parse and return response (as dict).
    json_data = json.loads(r.text)
    if 'id' in json_data:
        # Set shipment ID into order instance.
        return json_data
    else:
        mail_admins_task.delay(
            subject='%s request cannot be created.' % title,
            message='Status_code: %s\nOriginal response:\n%s' % (r.status_code, json_data))
        raise ValidationError('Invalid request. %s' % json_data)


def create_shipment_request(order):
    """
    Makes request to 3rd-party API with prepared data,
    based on received order.

    :param order: Instance of Order model.
    :return: Dictionary or ValidationError.
    """
    data = package_out(order)    
    response_data = _create_shipment(data, 'Shipment')
    order.shipping_id = response_data['id']
    order.save()
    return response_data


def create_shipment_return(order):
    """
    Makes request to 3rd-party API with prepared data,
    based on received order.

    :param order: Instance of Order model.
    :return: Dictionary or ValidationError.
    """
    data = package_back(order)
    response_data = _create_shipment(data, 'Return shipment')
    order.shipping_return_id = response_data['id']
    order.save()
    return response_data


def get_shipment_request(shipment_id):
    """
    Makes request to 3rd-party API for getting data about shipment.

    :param shipment_id: ID of shipment object in delivery service.
    :return: Dictionary or ValidationError.
    """

    # Prepare data for request.
    path = '/shipments/%s' % shipment_id
    url = '%s%s' % (settings.DELIVERY_BASE_URL, path)
    pl_auth = (settings.DELIVERY_AUTH_LOGIN, settings.DELIVERY_AUTH_PASSWORD)

    # Make a request.
    r = requests.get(url=url, auth=pl_auth)

    # Parse and return response (as dict).
    json_data = json.loads(r.text)
    if 'id' in json_data:
        return json_data
    else:
        mail_admins_task.delay(
            subject='Shipment #%s cannot be retrieved.' % shipment_id,
            message='Original response:\n%s' % json_data)
        raise ValidationError('Invalid request. %s' % json_data)


def create_label_request(external_id):
    """
    Makes request to 3rd-party API with prepared data,
    based on received order.

    :param external_id: Shipment id.
    :return: bytes or ValidationError.
    """

    # Prepare data for request.
    path = f'/shipments/{external_id}/labels?label_format=10x19_pdf'
    url = '%s%s' % (settings.DELIVERY_BASE_URL, path)
    pl_auth = (settings.DELIVERY_AUTH_LOGIN, settings.DELIVERY_AUTH_PASSWORD)

    # Make a request.
    r = requests.get(url=url, auth=pl_auth)

    # Parse and return response (as pdf content).
    json_data = json.loads(r.text)
    if len(json_data) and json_data[0].get('base64'):
        pdfbytes = json_data[0]['base64']
        # save label
        # label, _ = ShipmentLabel.objects.update_or_create(order=order)
        return pdfbytes
    else:
        mail_admins_task.delay(
            subject='Shipment labels cannot be created.',
            message='Original response:\n%s' % json_data)
        raise ValidationError('Invalid request. %s' % json_data)

def get_status_request(shipment_id):
    """
    Makes request to 3rd-party API for getting status about shipment.

    :param shipment_id: ID of shipment object in delivery service.
    :return: Dictionary
    """

    # Prepare data for request.
    path = '/shipment_monitor_statuses'
    url = '%s%s' % (settings.DELIVERY_BASE_URL, path)
    pl_auth = (settings.DELIVERY_AUTH_LOGIN, settings.DELIVERY_AUTH_PASSWORD)

    # Make a request.
    r = requests.get(url=url, auth=pl_auth, params={'ids': shipment_id})

    # Parse and return response (as dict).
    json_data = json.loads(r.text)
    if 'shipment_id' in json_data[0]:
        return json_data[0]
    else:
        mail_admins_task.delay(
            subject='Shipment #%s status cannot be retrieved.' % shipment_id,
            message='Original response:\n%s' % json_data)
        raise ValidationError('Invalid request. %s' % json_data)

def get_statuses_request(shipment_ids):
    """
    Makes request to 3rd-party API for getting status about many shipments at once.

    :param shipment_ids: list of IDs of shipment objects in delivery service.
    :return: list of Dictionaries
    """

    # Prepare data for request.
    path = '/shipment_monitor_statuses'
    url = '%s%s' % (settings.DELIVERY_BASE_URL, path)
    pl_auth = (settings.DELIVERY_AUTH_LOGIN, settings.DELIVERY_AUTH_PASSWORD)

    # Make requests.
    result = []
    ids_limit = 100 # from https://app.pakkelabels.dk/api/public/v3/specification
    for i in range(0, len(shipment_ids), ids_limit):
        r = requests.get(url=url, auth=pl_auth, params={'ids': ','.join([str(id) for id in shipment_ids[i:i+ids_limit]])})
        json_data = json.loads(r.text)
        if 'error' not in json_data and r.status_code == 200:
            result += json_data
    return result