from kivymd.uix.screen import MDScreen
from .commons import *
import requests
from kivymd.uix.dialog import MDDialog
from kivy.utils import rgba, get_color_from_hex
from datetime import datetime
from kivymd.uix.label import MDLabel

class AdminManager(MDScreen):
    confirm_url = base_url+"status"
    overlay_color = get_color_from_hex("#6042e4")
    category = StringProperty()
    new_data_url = base_url+"multi"
    tag = StringProperty()

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

    def select_tag(self):
        tag_items = ["tire", "steer","light", "oil", "battery", "coolant",]
        
        if not tag_items: return

        if self.app.dialog: 
            self.app.dialog.dismiss(force=True)
            self.app.dialog = None
        if not self.app.dialog:
            items = []
            tag_items.append("Others")
            for tag in tag_items:
                items.append(ItemConfirm(text=tag,category=tag, grouped="tag", is_dialog=True))
            self.app.dialog = MDDialog()
            self.app.dialog.title="Category"
            self.app.dialog.type="confirmation"
            self.app.dialog.items = items
            self.app.dialog.create_buttons()
            self.app.dialog.create_items()
            self.app.dialog.open()

    def select_car(self,group=""):
        car_items = ["Truck","Bus","Minivan","SUV","Tractor","Personal"]
        
        if not car_items: return

        if self.app.dialog: 
            self.app.dialog.dismiss(force=True)
            self.app.dialog = None
        if not self.app.dialog:
            items = []
            car_items.append("Others")
            for tag in car_items:
                items.append(ItemConfirm(text=tag,category=group, grouped="car", is_dialog=True))
            self.app.dialog = MDDialog()
            self.app.dialog.title="Car Type"
            self.app.dialog.type="confirmation"
            self.app.dialog.items = items
            self.app.dialog.create_buttons()
            self.app.dialog.create_items()
            self.app.dialog.open()

    def select_service(self):
        menu_items = [("Car Wash","service"),("Maintainance","service"),("Tracking","service"),("Diagnostics","service"),("Puncture","puncture"), ("Tow Service","tow")]
        
        if not menu_items: return

        if self.app.dialog: 
            self.app.dialog.dismiss(force=True)
            self.app.dialog = None
        if not self.app.dialog:
            items = []
            for menu in menu_items:
                
                items.append(ItemConfirm(text=menu[0],category=menu[1], grouped="service", is_dialog=True))
            self.app.dialog = MDDialog()
            self.app.dialog.title="Services"
            self.app.dialog.type="confirmation"
            self.app.dialog.items = items
            self.app.dialog.create_buttons()
            self.app.dialog.create_items()
            self.app.dialog.open()

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
        self.check_orders()
        self.app.alert("Message deleted.")
    
    def get_default(self):
        return MDLabel(
            text= "No Orders or Purchase",
            font_name="Motion",
            font_size="25sp",
            halign= "center",
            bold=True,
            color= rgba(71,92,119,255),
        )

    def disble_all(self,disable=True):
        widgets = [
            self.ids.service,
            self.ids.store,
            self.ids.managers,
            self.ids.orders,
        ]

        for wid in widgets:
            wid.disabled = disable

    def check_active(self,all_data=[]):
        active = []
        for data in all_data:
            if data['status'] == 0:
                active.append(data)
        return active

    def check_orders(self):

        main = self.manager.get_screen("main")
        main.refresh_data()
        order_data = main.data_dict['message']

        messages = []
        carts = []

        new_orders = self.check_active(order_data)

        order_cart_items = {}

        for order in new_orders:
            if not order_cart_items.get(order['target']):
                order_cart_items[order['target']] = []
            message,location = order['message'].split('::')
            info = {
                "id": order['id'],
                "message": message,
                "date": self.check_time(order['date']),
                "price": order['cost'],
                "location": location,
                "ref": order['ref'],
                "status": order['status'],
            }
            
            order_cart_items[order['target']].append(info)

        
        if not order_cart_items: 
            self.disble_all(False)
            self.app.hide_widget(self.ids.orders_popup,dohide=True)
            self.app.alert("There is active orders or purchases!")
            return
        self.disble_all()
        self.ids.selection_list.clear_widgets()
        self.ids.selection_list.add_widget(self.get_default())
        if order_cart_items:
            self.ids.selection_list.clear_widgets()
            for email, all_data in order_cart_items.items():
                for data in all_data:
                    data['email'] = email
                    CartItemObj = CustomItem(
                        text = f"{data['message']} {data['date']}",
                        secondary_text = email,
                        info = data,
                        on_release=self.select_message,
                    )
                    self.ids.selection_list.add_widget(CartItemObj)
        self.app.hide_widget(self.ids.orders_popup,dohide=False)

    def select_message(self,*args):
        info = args[0].info
        self.add_widget(NoticeBlock(
            lbl_product = info["message"],
            lbl_location = info["location"],
            lbl_date = info["date"],
            action = self.confirm_order,
            info = info,
        ))

    def confirm_order(self,*args):
        caller = args[0] if len(args) else None
        
        if not caller:
            self.app.alert("Something went wrong!")
            return
        
        info = caller.info

        data = {
            "reqmail":self.app.reqmail,
            "filter":info['email'],
            "id":info['id'],
        }

        data = str(data).replace("'",'"')

        try:
            response = requests.patch(self.confirm_url,data,headers=headers)
            data = response.json()
            
            if response.status_code != 201: 
                self.app.alert(text=data["message"])
                return
        except:
            self.app.alert(text="Server seem down")
            return
        
        self.app.alert("Order or Purchase Confirmed.")
        
        self.remove_widget(caller)
        self.check_orders()

        


    def add_service(self,wid):
        self.category = "service_type"

        self.ids.service_title.text = str(wid.text)
        self.show_popup(self.ids.add_services)

    def add_store(self,wid):
        self.category = "store_type"
        self.ids.store_title.text = str(wid.text)
        self.show_popup(self.ids.add_resouce)

    def add_manager(self,wid):
        self.category = "manager_type"
        self.ids.manager_title.text = str(wid.text)
        self.show_popup(self.ids.add_managers)


    def show_popup(self,popup,hide=False):
        self.app.hide_widget(popup,dohide=hide)
        self.ids.service.disabled = not hide
        self.ids.store.disabled = not hide
        self.ids.managers.disabled = not hide
    
    def add(self,group=""):
        required = []
        data = {
            "reqmail": self.app.reqmail,
        }
        if group == "manager":
            email = self.ids.manager_email.text
            required.append(email)
            data["email"] = email

        if group == "service":
            service = self.ids.service_type.text
            cost = self.ids.service_cost.text
            service_car = self.ids.service_car.text

            required.append(service)
            required.append(cost)
            required.append(service_car)

            data["service"] = service
            data['tag'] = self.tag
            data["car"] = service_car
            data["cost"] = cost
        
        if group == "store":
            store_car = self.ids.store_car.text
            store_product = self.ids.store_product.text
            store_price = self.ids.store_price.text
            store_quantity = self.ids.store_quantity.text
            tag = self.ids.store_tag.text
            store_image = self.ids.store_image.text

            required.append(store_car)
            required.append(store_product)
            required.append(tag)
            required.append(store_price)
            required.append(store_quantity)
            
            data["car"] = store_car
            data["product"] = store_product
            data["cost"] = store_price
            data['tag'] = tag
            data["quantity"] = store_quantity
            if store_image:
                data["image"] = store_image


        for x in required:
            if x == None or x == "":
                self.app.alert(text = "Fields marked * are required")
                return
        
        data = str(data).replace("'",'"')

        try:
            response = requests.put(self.new_data_url,data,headers=headers)
            data = response.json()
            
            if response.status_code != 201: 
                self.app.alert(text=data["message"])
                return
            else:
                self.app.alert(text="Added record successful")
                return
        except:
            self.app.alert(text="Registration Failed")
            return
        finally:
            self.ids.manager_email.text = ""
            self.ids.service_type.text = ""
            self.ids.service_cost.text = ""
            self.ids.service_car.text = ""
            self.ids.store_tag.text = ""
            self.ids.store_car.text = ""
            self.ids.store_product.text = ""
            self.ids.store_price.text = ""
            self.ids.store_quantity.text = ""
            self.ids.store_image.text = ""
