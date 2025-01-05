from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Orders, OrderPart
from inventory.models import Inventory
from parts.models import Part


# Create your tests here.
class GenerateListsTests(APITestCase):
    def setUp(self):
        Orders.objects.create(order_id = 12345)
        
    def test_varied(self):
        print("___________ STARTING TEST test_varied _______________")
        order = Orders.objects.get(order_id = 12345)
        Part.objects.bulk_create(
            [
                Part(sku_color='equal to inventory'),
                Part(sku_color='more than inventory'),
                Part(sku_color='less than inventory'),
                Part(sku_color='not in inventory'),
            ]
        )
        parts = Part.objects.all()
        print("all created parts in test db:")
        for p in parts:
            print(p.sku_color)
        Inventory.objects.bulk_create(
            [
                Inventory(location = 'loc1Test', sku_color = parts[0], qty=10, warehouse_number = 'TestHouse', amount_needed = 0),
                Inventory(location = 'loc2Test', sku_color = parts[1], qty=3, warehouse_number = 'TestHouse', amount_needed = 0),
                Inventory(location = 'loc3Test', sku_color = parts[2], qty=8, warehouse_number = 'TestHouse', amount_needed = 0),
                Inventory(location = 'loc4Test', sku_color = parts[2], qty=12, warehouse_number = 'TestHouse', amount_needed = 0),
            ]
        )
        OrderPart.objects.bulk_create(
            [
                OrderPart(order_id = order, sku_color = parts[0], qty = 10),
                OrderPart(order_id = order, sku_color=parts[1], qty = 10),
                OrderPart(order_id = order, sku_color=parts[2], qty = 10),
                OrderPart(order_id = order, sku_color=parts[3], qty = 10),
            ]
        )
        url = reverse('generateLists')
        response = self.client.post(url, {'orderID' : '12345'}, format='json')
        print('varied test case')
        print(response.data)
        pass
        
    def test_no_inventory_picklist(self):
        print("___________ STARTING TEST test_no_inventory_picklist _______________")
        order = Orders.objects.get(order_id = 12345)
        Part.objects.bulk_create(
            [
                Part(sku_color='not in inventory'),
            ]
        )
        parts = Part.objects.all()
        print("all created parts in test db:")
        for p in parts:
            print(p.sku_color)
        OrderPart.objects.bulk_create(
            [
                OrderPart(order_id = order, sku_color = parts[0], qty = 10),
            ]
        )
        url = reverse('generateLists')
        response = self.client.post(url, {'orderID' : '12345'}, format='json')
        print('no inventory picklist test case')
        print(response.data)
        pass
        
    def test_no_manuList(self):
        print("___________ STARTING TEST test_no_manuList _______________")
        order = Orders.objects.get(order_id = 12345)
        Part.objects.bulk_create(
            [
                Part(sku_color='only in inventory'),
            ]
        )
        parts = Part.objects.all()
        print("all created parts in test db:")
        for p in parts:
            print(p.sku_color)
        Inventory.objects.bulk_create(
            [
                Inventory(location = 'loc3Test', sku_color = parts[0], qty=8, warehouse_number = 'TestHouse', amount_needed = 0),
                Inventory(location = 'loc4Test', sku_color = parts[0], qty=12, warehouse_number = 'TestHouse', amount_needed = 0),
            ]
        )
        OrderPart.objects.bulk_create(
            [
                OrderPart(order_id = order, sku_color = parts[0], qty = 5),
            ]
        )
        url = reverse('generateLists')
        response = self.client.post(url, {'orderID' : '12345'}, format='json')
        print('no manuList test case')
        print(response.data)
        pass   
