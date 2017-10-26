import datetime
import json
import urllib

import math
from django.conf import settings
import base64
import requests


class SageOneAccountAPI(object):
    SAGE_URL = "https://accounting.sageone.co.za"
    API_VERSION = "1.1.2"

    sage = None
    invoice = {}
    customer = {}
    total_zar = 0.00
    from_currency_code = "ZAR"

    SAGEONE_USERNAME = settings.SAGEONE_USERNAME
    SAGEONE_PASSWORD = settings.SAGEONE_PASSWORD
    SAGEONE_COMPANY_ID = settings.SAGEONE_COMPANY_ID
    SAGEONE_API_KEY = settings.SAGEONE_API_KEY
    SAGEONE_BANK_ACCOUNT_ID = settings.SAGEONE_BANK_ACCOUNT_ID

    def __init__(self):
        self.xero = None
        self.invoice = None

    def send_request(self, url_ammend, data, extra_var=None):
        if not extra_var:
            extra_var = {}

        core_url = "%s/api/%s/%s" % (self.SAGE_URL, self.API_VERSION,  url_ammend)
        headers = {
            'Authorization': 'Basic %s' % base64.b64encode(bytes("%s:%s" % (self.SAGEONE_USERNAME, self.SAGEONE_PASSWORD)), 'utf-16be'),
        }
        new_url = "%s?apikey={%s}&companyid=%s" % (core_url, self.SAGEONE_API_KEY, self.SAGEONE_COMPANY_ID)
        added_vars = '&'.join(["{}={}".format(k, v) for k, v in extra_var.items()])
        if added_vars:
            new_url += "&%s" % added_vars

        if data != {}:
            res = requests.post(new_url, json=data, headers=headers)
        else:
            headers['Content-Type'] = "application/json"
            res = requests.get(new_url, headers=headers)

        try:
            return res.json()
        except:
            return {"message":res.text}

    # customers
    def get_customers(self):
        items = self.send_request("Customer/Get", {})
        results_list = []
        for item in items["Results"]:
            results_list.append(item)
        if items["TotalResults"] > 100:
            div = int(math.floor(float(items["TotalResults"]) / 100))
            skip_list = []
            for i in range(0, div + 1):
                if i:
                    top = int((float(i - 1) * 100.00))
                    skip = (top + 101)
                else:
                    skip = 0
                skip_list.append(skip)

            for skip in skip_list:
                if skip:
                    items = self.send_request("Customer/Get", {}, {"$skip": skip})
                    for item in items["Results"]:
                        results_list.append(item)
        return results_list

    def put_customer(self, data):
        return self.send_request("Customer/Save", data)

    def get_customer(self, object_id):
        return self.send_request("Customer/Get/%s" % object_id, {})

    def get_or_create_customer(self, customer):
        customer_list = self.get_customers()
        for sage_customer in customer_list:
            if customer.email == sage_customer.get("Email", "") and customer.email != "":
                return sage_customer

        category = self.get_or_create_category("OOP")
        data = {
            "Name": "%s %s" % (customer.first_name, customer.last_name),
            "ContactName": "%s" % customer.first_name,
            "Email": "%s" % customer.email,
            "Active": True,
            "Category": {"Description": category["Description"], "ID": category["ID"]},
            "DeliveryAddress01": customer.userprofile.shipping_address,
            "DeliveryAddress02": customer.userprofile.shipping_suburb,
            "DeliveryAddress03": customer.userprofile.shipping_city,
            "DeliveryAddress05": customer.userprofile.shipping_postal_code,
            "PostalAddress01": customer.userprofile.shipping_address,
            "PostalAddress02": customer.userprofile.shipping_suburb,
            "PostalAddress03": customer.userprofile.shipping_city,
            "PostalAddress05": customer.userprofile.shipping_postal_code,
            "Telephone": customer.userprofile.contact_number,
            "Mobile": customer.userprofile.contact_number,
            "CurrencySymbol": "ZAR"
        }
        sage_customer = self.put_customer(data)
        return sage_customer

    # categories
    def get_categories(self):
        items = self.send_request("CustomerCategory/Get", {})
        results_list = []
        for item in items["Results"]:
            results_list.append(item)
        if items["TotalResults"] > 100:
            div = int(math.floor(float(items["TotalResults"]) / 100))
            skip_list = []
            for i in range(0, div + 1):
                if i:
                    top = int((float(i - 1) * 100.00))
                    skip = (top + 101)
                else:
                    skip = 0
                skip_list.append(skip)

            for skip in skip_list:
                if skip:
                    items = self.send_request("CustomerCategory/Get", {}, {"$skip": skip})
                    for item in items["Results"]:
                        results_list.append(item)
        return results_list

    def put_category(self, data):
        return self.send_request("CustomerCategory/Save", data)

    def get_or_create_category(self, category):
        category_list = self.get_categories()
        for sage_category in category_list:
            if category == sage_category.get("Description", "") and category != "":
                return sage_category
        data = {"Description": category}
        sage_category = self.put_category(data)
        return sage_category


    # bank accounts
    def get_bank_accounts(self):
        items = self.send_request("BankAccount/Get", {})
        results_list = []
        for item in items["Results"]:
            results_list.append(item)
        if items["TotalResults"] > 100:
            div = int(math.floor(float(items["TotalResults"]) / 100))
            skip_list = []
            for i in range(0, div + 1):
                if i:
                    top = int((float(i - 1) * 100.00))
                    skip = (top + 101)
                else:
                    skip = 0
                skip_list.append(skip)

            for skip in skip_list:
                if skip:
                    items = self.send_request("BankAccount/Get", {}, {"$skip": skip})
                    for item in items["Results"]:
                        results_list.append(item)
        return results_list


    def get_bank_account(self, object_id):
        return self.send_request("BankAccount/Get/%s" % object_id, {})

    # account balance
    def get_account_balance(self):
        return self.send_request("AccountBalance/Get", {})

    # items
    def get_tax_types(self):
        items = self.send_request("TaxType/Get", {})
        results_list = []
        for item in items["Results"]:
            results_list.append(item)
        if items["TotalResults"] > 100:
            div = int(math.floor(float(items["TotalResults"]) / 100))
            skip_list = []
            for i in range(0, div + 1):
                if i:
                    top = int((float(i - 1) * 100.00))
                    skip = (top + 101)
                else:
                    skip = 0
                skip_list.append(skip)

            for skip in skip_list:
                if skip:
                    items = self.send_request("TaxType/Get", {}, {"$skip": skip})
                    for item in items["Results"]:
                        results_list.append(item)
        return results_list


    def get_tax_type(self, object_id):
        return self.send_request("TaxType/Get/%s" % object_id, {})

    # items
    def get_items(self):
        items = self.send_request("Item/Get", {}, {"includeAdditionalItemPrices":False})
        results_list = []
        for item in items["Results"]:
            results_list.append(item)
        if items["TotalResults"] > 100:
            div = int(math.floor(float(items["TotalResults"]) / 100))
            skip_list = []
            for i in range(0, div+1):
                if i:
                    top = int((float(i-1) * 100.00))
                    skip = (top + 101)
                else:
                    skip = 0
                skip_list.append(skip)

            for skip in skip_list:
                if skip:
                    items = self.send_request("Item/Get", {}, {"includeAdditionalItemPrices": False, "$skip": skip})
                    for item in items["Results"]:
                        results_list.append(item)
        return results_list


    def get_item(self, object_id):
        return self.send_request("Item/Get/%s" % object_id, {})

    def put_item(self, data):
        return self.send_request("Item/Save", data)

    def get_or_create_item(self, item, item_code, item_name):
        item_list = self.get_items()
        for sage_item in item_list:
            if item_code.strip().upper() == sage_item.get("Code", "").upper().strip() and item_code != "":
                return sage_item

        data = {
            "Code": item_code,
            "Name": "%s - %s" % (item.product_item.product.title, item.product_item.size.title),
            "Description": "%s - %s" % (item.product_item.product.title, item.product_item.size.title),
            "Active": True,
            "Physical": True,
            "Unit": item.product_item.size.title,
            "LastCost": item.product_item.get_cost(),
        }
        sage_item = self.put_item(data)
        return sage_item

    def put_customer_receipt(self, data):
        return self.send_request("CustomerReceipt/Save", data)

    def put_allocate(self, data):
        return self.send_request("Allocation/Save", data)

    #invoices
    def get_invoice(self, object_id):
        return self.send_request("TaxInvoice/Get/%s" % object_id, {})

    def put_invoice(self, data):
        return self.send_request("TaxInvoice/Save", data)

    def create_invoice(self, order, customer):
        sage_customer = self.get_or_create_customer(customer)
        line_items = []
        for item in order.orderitem_set.all().select_related("product_item", "product_item__size"):
            name = "%s - %s" % (item.product_item.product.title, item.product_item.size.title.upper().strip())
            code = "%s-%s" % (item.product_item.get_sku_code(), item.product_item.size.title.upper().strip())
            litem = self.get_or_create_item(item, code, name)

            tax_type_id = ""
            for tax_type in self.get_tax_types():
                if "Standard Rate" in tax_type["Name"]:
                    tax_type_id = tax_type["ID"]
                    break

            item_data = {
                "SelectionId": litem["ID"],
                "TaxTypeId": tax_type_id,
                "Description": litem["Description"],
                "UnitPriceExclusive": item.product_item.get_cost(),
                "DiscountPercentage": 0.00,
                "PriceInclusive": item.product_item.get_cost(),
                "Quantity": item.qty,
                "TaxPercentage": 14.00,
                "Total": float(item.get_total()),
            }
            line_items.append(item_data)
        #
        # # todo: Add shipping cost as a line item.
        #
        if customer.userprofile.on_30_days:
            due_date = datetime.datetime.now() + datetime.timedelta(days=30)
        else:
            due_date = datetime.datetime.now() + datetime.timedelta(hours=48)

        due_date = due_date.strftime("%Y-%m-%d")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

        data = {
            "DueDate": due_date,
            "Reference": order.reference_id,
            "StatusId": 1,
            "CustomerId": sage_customer["ID"],
            "AllowOnlinePayment": True,
            "CustomerName": sage_customer["Name"],
            "Customer": sage_customer,
            "Date": timestamp,
            "Exclusive": True,
            "Tax": order.cart_tax,
            "Total": order.cart_total,
            "CurrencyId": 1,
            "DeliveryAddress01": customer.userprofile.shipping_address,
            "DeliveryAddress02": customer.userprofile.shipping_suburb,
            "DeliveryAddress03": customer.userprofile.shipping_city,
            "DeliveryAddress05": customer.userprofile.shipping_postal_code,
            "Lines": line_items,
        }
        return self.put_invoice(data)

    def mark_invoice_as_paid(self, invoice):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
        allocate_to = invoice["ID"]
        amount = invoice["AmountDue"]
        bank_account_id = None

        if not self.SAGEONE_BANK_ACCOUNT_ID:
            bank_account_id = None
            for account in self.get_bank_accounts():
                # get the first bank account in the system
                bank_account_id = account["ID"]
                break
        else:
            for account in self.get_bank_accounts():
                if str(account["ID"]) == str(self.SAGEONE_BANK_ACCOUNT_ID):
                    bank_account_id = account["ID"]
                    break

        if bank_account_id:
            data = {
                "CustomerId":invoice["CustomerId"],
                "Date":timestamp,
                "Reference": invoice["Reference"],
                "DocumentNumber": allocate_to,
                "Total": amount,
                "Discount": 0.00,
                "Reconciled": False,
                "Accepted": True,
                "Payee": invoice["CustomerName"],
                "BankAccountId": bank_account_id,
                "PaymentMethod": 3
            }
            receipt = self.put_customer_receipt(data)

            data = {
                "SourceDocumentId": receipt["ID"],
                "AllocatedToDocumentId": allocate_to,
                "Discount": 0.00,
                "Total": amount,
            }
            allocate = self.put_allocate(data)

            return receipt, allocate, self.get_invoice(allocate_to)
        else:
            print "No Banks Account In Sage ONE Account. Please Contact Admin"

