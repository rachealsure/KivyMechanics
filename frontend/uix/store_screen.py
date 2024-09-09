from kivymd.uix.screen import MDScreen
from .commons import *
from kivy.clock import Clock
from kivy.utils import rgba, get_color_from_hex
from kivymd.uix.label import MDLabel
from kivy.utils import rgba
from kivymd.uix.dialog import MDDialog
import requests
from datetime import datetime

class StoreScreen(MDScreen):
    purchase_url = base_url+"purchase"
    delete_url = base_url+"remove"
    overlay_color = get_color_from_hex("#6042e4")
    menu = None
    category = StringProperty()
    item_card = None
    quality = []
    price = 0
    quantity = 0
    selected_delete_widget = None
    widget = ObjectProperty()
    is_quality = False
    tag = ""
    my_notice_items = {}

    items = []

    store_data = {}

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
        Clock.schedule_interval(self.refresh,5)

        
    def load_products(self,*args):
        self.force_refresh()
        ignore = [
            "tire",
            "steer",
            "light",
            "oil",
            "battery",
            "coolant",
        ]
        self.items = []

        for data in self.store_data:
            if data["tag"] not in ignore:
                self.items.append(data)
        self.ids.shop.clear_widgets()
        for item in self.items:
            product_card = ShopCard(
                on_release= self.display_item,
                product = item["product"],
                info = item,
                description = f"{item['car']} {item['tag']}",
            )
            self.ids.shop.add_widget(product_card)
    
    def refresh(self,*args):
        # if not self.app.is_loggedin:
        #     Clock.unschedule(self.refresh)
        #     return

        main = self.manager.get_screen("main")
        if main.data_dict.get("store"): self.store_data = main.data_dict["store"]
        if main.data_dict.get("cart"): self.my_notice_items = main.data_dict["cart"]
    
    def force_refresh(self):
        main = self.manager.get_screen("main")
        main.refresh_data()
        if main.data_dict.get("store"): self.store_data = main.data_dict["store"]
        if main.data_dict.get("cart"): self.my_notice_items = main.data_dict["cart"]
    
    def get_default(self):
        return MDLabel(
            text= "No notification",
            font_name="Motion",
            font_size="25sp",
            halign= "center",
            bold=True,
            color= rgba(71,92,119,255),
        )

    def disble_all(self,disable=True):
        widgets = [
            self.ids.tire_card,
            self.ids.steer_card,
            self.ids.light_card,
            self.ids.oil_card,
            self.ids.batt_card,
            self.ids.cool_card,
        ]

        for wid in widgets:
            wid.disabled = disable


    def get_gps(self):
        address = None
        gps = GPS()
        try:
            address = gps.get_address()
        except:
            pass
        if not address:
            self.app.alert("Unable to get location!")
            return
        self.ids.location.text = address

    def display_item(self,*args):
        item = args[0].info
        if item['quantity'] == 0:
            self.app.alert("Out of stock!")
            return
        self.item_card = ScaleCard(
            product=item["product"],
            description=f"Durable and good quality {item['car']} {item['tag']}. Costs Ksh.{item['price']}/{item['tag']}. We have {item['quantity']} in stock, so hurry and order while exists. We offer free derivery on any goods purchased.",
            quantity=item['quantity'],
            cost=item['price'],
            car=item['car'],
            tag=item['tag'],
            # source="",
            md_bg_color= "brown",
            size_hint= (None,None),
            size= (dp(200), dp(200)),
            radius= [dp(100),],
            pos_hint= {"center_x":.5,"center_y":.5},
        )
        
        self.add_widget(self.item_card)

    def check_time(self,date):
        dateObject = datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
        timeDiff = datetime.strptime(datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")-datetime.strptime(datetime.strftime(dateObject,"%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
        total_seconds = timeDiff.total_seconds()
        offdays = timeDiff.days
        sent_on = ""
        
        if int(offdays) == 0:
            hours = int(total_seconds/3600)
            minutes = int((total_seconds%3600)/60)
            if hours == 0 and minutes > 0: sent_on = f"{minutes}m ago"
            if hours > 0: sent_on = f"{hours}h {minutes}m ago"
            if hours == 0 and minutes == 0: sent_on = "Just Now"
        if int(offdays) == 1:
            sent_on = f'Yesterday, {datetime.strftime(dateObject,"%H:%M:%S")}'
        if int(offdays) > 1:
            sent_on = datetime.strftime(dateObject,"%Y-%m-%d %H:%M:%S")
        
        return sent_on
    
    def load_cart(self):
        self.disble_all()
        self.ids.selection_list.clear_widgets()
        self.ids.selection_list.add_widget(self.get_default())
        if self.my_notice_items:
            self.ids.selection_list.clear_widgets()
            self.my_notice_items.reverse()
            for item in self.my_notice_items:
                if self.app.user_id != item["ref"] or item["status"] == -1: continue
                CartItemObj = CustomCartItem(
                    lbl_product = f"Product: {item['product']}",
                    lbl_car = f"Car Type: {item['car']}",
                    lbl_price = f"Quantity: {item['quantity']} @ Ksh. {item['price']}",
                    lbl_location = f"Location: {item['location']}",
                    lbl_status = f"Status: Delivered" if item['status'] == 1 else "Status: Pending",
                )
                self.ids.selection_list.add_widget(CartItemObj)
        self.app.hide_widget(self.ids.my_cart,dohide=False)

    def load_quick(self,widget):
        
        self.items = []
        self.tag = ""
        self.widget = widget
        
        if widget.text == "Car Tire":
            self.tag = "tire"
        if widget.text == "Car Steering":
            self.tag = "steer"
        if widget.text == "Head Lights":
            self.tag = "light"
        if widget.text == "Oil & Lubrication":
            self.tag = "oil"
        if widget.text == "Batteries":
            self.tag = "battery"
        if widget.text == "Coolants":
            self.tag = "coolant"
        
        for data in self.store_data:
            if data["tag"] == self.tag:
                self.items.append(data)
        
        if not self.store_data or not self.items:
            self.app.alert("Out of stock!")
            return

        self.disble_all()

        # self.quality = [
        #     {
        #         "viewclass": "IconListItem",
        #         "icon": widget.icon,
        #         "text": item,
        #         "height": dp(56),
        #         "on_release": lambda x=item: self.set_item(x),
        #     } for item in items
        # ]


        self.ids.scroll.disabled = True
        self.ids.service_title.text = widget.text
        self.ids.car_type.hint_text = "* Vehicle Type" if widget.text != "Head Lights" else "* Lights Type"
        self.app.hide_widget(self.ids.quick_store,dohide=False)

        
    
    def list_lights(self):
        service_type = [("Parking Lights","car-parking-lights"), ("Alarm Light","alarm-light-outline"),("Frontal Lights","car-light-high"),("Break Lights","car-light-dimmed")]
        menu_items = [
                {
                    "viewclass": "IconListItem",
                    "icon": service[1],
                    "text": service[0],
                    "height": dp(56),
                    "on_release": lambda x=service[0]: self.set_item(x),
                } for service in service_type
            ]
        return menu_items

    def get_car_type(self):
        car_type = [("Truck","truck-outline"), ("Bus","bus"),("Minivan","van-passenger"),("SUV","car-pickup"),("Tractor","tractor-variant"),("Personal","car-outline")]
        menu_items = [
                {
                    "viewclass": "IconListItem",
                    "icon": car[1],
                    "text": car[0],
                    "height": dp(56),
                    "on_release": lambda x=car[0]: self.set_item(x),
                } for car in car_type
            ]
        return menu_items


    def dialog(self,quality=False):
        menu_items = self.items
        
        self.is_quality = quality

        if not menu_items: return
        
        if self.app.dialog: 
            self.app.dialog.dismiss(force=True)
            self.app.dialog = None
        if not self.app.dialog:
            items = []
            for menu in menu_items:
                if quality:
                    items.append(ItemConfirm(text=menu["product"],category=f'{menu["price"]},{menu["quantity"]}', grouped=menu["tag"], is_dialog=True))
                if not quality:
                    items.append(ItemConfirm(text=menu["car"],category=f'{menu["price"]},{menu["quantity"]}', grouped=menu["tag"], is_dialog=True))
                
            self.app.dialog = MDDialog()
            self.app.dialog.title="Vehicle Type" if not quality else "Quality"
            self.app.dialog.type="confirmation"
            self.app.dialog.items = items
            self.app.dialog.create_buttons()
            self.app.dialog.create_items()
            self.app.dialog.open()

    
    def check_quantity(self,*args):
        if args:
            try:
                if args[1] != " ":
                    quantity = int(args[1])
                else:
                    quantity = 0
                if int(quantity) > int(self.quantity): self.ids.quantity.text = str(self.quantity)
                self.ids.cost.text = f"Cost: {int(self.price) * int(self.ids.quantity.text)} Ksh."
            except:
                self.app.alert("Only numbers required!")
                return

    
    def set_item(self, text_item="",info=""):
        if text_item:
            
            if self.is_quality:
                self.ids.quality.text = text_item
                if info:
                    self.price ,self.quantity = info.split(",")
                    if int(self.quantity) <= 0: return self.app.alert(f"{text_item}: Out of stock")
                self.ids.quantity.disabled = False
                
            elif not self.is_quality:
                self.ids.car_type.text = text_item
                self.ids.quality.disabled = False

    def on_selected(self, instance_selection_list, instance_selection_item):
        self.ids.delete_msg.disabled = False
        self.selected_delete_widget = instance_selection_list.get_selected_list_items()

    def on_unselected(self, instance_selection_list, instance_selection_item):
        if not len(instance_selection_list.get_selected_list_items()):
            self.ids.delete_msg.disabled = True
            self.selected_delete_widget = None

    def remove_all(self,force=False):
        if force: self.selected_delete_widget = self.ids.selection_list.children
        selected_message_info = []
        if not self.selected_delete_widget:
            if not force: self.app.alert(text="No Message selected")
            return
        for widget in self.selected_delete_widget:
            selected_message_info.append(widget.children[1].info)
            self.ids.selection_list.remove_widget(widget)
        self.ids.delete_msg.disabled = True
        self.selected_delete_widget = None
        return selected_message_info

    def delete(self,force=False):
        all_info = self.remove_all(force=force)
        
        for info in all_info:
            data = {
                "reqmail":self.app.reqmail,
                "id": info['id'],
            }
            data = str(data).replace("'",'"')
            try:
                response = requests.patch(self.delete_url,data,headers=headers)
                
                if response.status_code != 201:
                    data = response.json()
                    self.app.alert(str(data["message"]))
                    continue
            except:
                self.app.alert(text="Server seem down")
                continue
        self.force_refresh()
        self.load_cart()
        self.app.alert("Message deleted.")
    
    def order(self):
        car_type = self.ids.car_type.text
        quality = self.ids.quality.text
        quantity = self.ids.quantity.text
        location = self.ids.location.text

        cost = int(self.ids.cost.text.split(" ")[1])

        for x in [car_type,quality,quantity,location]:
            if not x or x == "":
                self.app.alert("All fields marked * required!")
                return

        message = f"{quantity} {car_type} {self.tag}, {quality}:: {location}"

        data = {
            "reqmail":self.app.reqmail,
            "tag":self.tag,
            "quantity":quantity,
            "product":quality,
            "car":car_type,
            "cost":cost,
            "message":message,
            "location":location,
        }

        data = str(data).replace("'",'"')

        try:
            response = requests.put(self.purchase_url,data,headers=headers)
            data = response.json()
            
            if response.status_code != 201: 
                self.app.alert(text=data["message"])
                return
        except:
            self.app.alert(text="Server seem down")
            return
        self.app.alert("Purchase made. Wait for delivery")
        
        self.ids.car_type.text = ""
        self.ids.quality.text = ""
        self.ids.quantity.text = ""
        self.ids.location.text = ""
        self.ids.cost.text = "Cost: 0 Ksh."
        self.disble_all(False)
        self.app.hide_widget(self.ids.quick_store)

        self.force_refresh()

