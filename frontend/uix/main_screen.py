from kivymd.uix.screen import MDScreen
from .commons import *
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
import requests
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivy.utils import rgba, get_color_from_hex
from datetime import datetime

class MainScreen(MDScreen):
    menu = ObjectProperty()
    category = StringProperty()
    req_url = base_url+"message"
    load_url = base_url+"load"
    overlay_color = get_color_from_hex("#6042e4")
    
    tow_data = {}
    puncture_data = {}
    service_data = {}
    tow_cost = {}
    puncture_cost = {}
    service_cost = {}
    my_notice_items = {}
    data_dict = {}

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.refresh_data,10)
    

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
        self.refresh_data()
        self.load_messages()
        self.app.alert("Message deleted.")
    

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
    

    def load_messages(self):
        self.refresh_data()
        if not self.data_dict['message']: return self.app.alert("You have no notifications!")
        self.my_notice_items = self.data_dict['message']
        self.ids.selection_list.clear_widgets()
        self.ids.selection_list.add_widget(self.get_default())
        if self.my_notice_items:
            self.ids.selection_list.clear_widgets()
            self.my_notice_items.reverse()
            for item in self.my_notice_items:
                if self.app.user_id != item["ref"] or item["status"] == -1: continue
                service_product,location = item['message'].split("::")
                CartItemObj = CustomItem(
                    icon = "message-question-outline" if item["status"] == 0 else "checkbox-marked-circle-outline",
                    text = f'{service_product}, {self.check_time(item["date"])}',
                    info=item,
                    secondary_text = f"Destination: {location}",
                )
                self.ids.selection_list.add_widget(CartItemObj)
        self.app.hide_widget(self.ids.notification,dohide=False)

    def get_default(self):
        return MDLabel(
            text= "No notification",
            font_name="Motion",
            font_size="25sp",
            halign= "center",
            bold=True,
            color= rgba(71,92,119,255),
        )

    def load_store(self):
        self.refresh_data()
        if not self.data_dict['store']: return self.app.alert("Nothing at the store!")
        
        store = self.manager.get_screen("store")
        store.load_products()
        store.force_refresh()
        self.manager.transition.direction = "left"
        self.manager.current = "store"

    def load_data(self,filter=""):
        data = {
            "reqmail":self.app.reqmail,
            "filter":filter,
        }

        data = str(data).replace("'",'"')

        try:
            response = requests.post(self.load_url,data,headers=headers)
            all_data = response.json()
            
            if response.status_code != 200: 
                return []
        except:
            return []
        
        return all_data["results"]
    
    def refresh_data(self,*args):
        if not self.app.is_loggedin:
            return
        self.data_dict = {}
        target = [
            "service",
            "store",
            "cart",
            "message",
        ]


        for filter in target:
            data = self.load_data(filter)
            self.data_dict[filter] = data
        
        self.ids.msg_btn.right_text = str(len(self.data_dict['message'])) if len(self.data_dict['message']) <= 99 else "99+"
        self.get_costs()

    def get_costs(self):
        if self.data_dict.get("service"):  
            self.tow_data = {}
            self.puncture_data = {}
            self.service_data = {}
            self.tow_cost = {}
            self.puncture_cost = {}
            self.service_cost = {}

            for data in self.data_dict["service"]:
                service = data["sevice"]
                tag = data["tag"]

                if tag == "tow":
                    if not self.tow_cost.get(service):
                        self.tow_cost[service] = []
                    
                    if not self.tow_data.get(service):
                        self.tow_data[service] = []

                    self.tow_data[service].append(data)
                    self.tow_cost[service].append((data["car"],data["price"]))
                if tag == "puncture":
                    if not self.puncture_cost.get(service):
                        self.puncture_cost[service] = []

                    if not self.puncture_data.get(service):
                        self.puncture_data[service] = []

                    self.puncture_data[service].append(data)
                    self.puncture_cost[service].append((data["car"],data["price"]))
                if tag == "service":
                    if not self.service_cost.get(service):
                        self.service_cost[service] = []

                    if not self.service_data.get(service):
                        self.service_data[service] = []

                    self.service_data[service].append(data)
                    self.service_cost[service].append((data["car"],data["price"]))
       
    def select_car(self):
        car_items = []

        service = self.ids.service_type.text

        all_data = []

        if self.service_cost.get(service):
            all_data = self.service_cost[service]
        
        if not all_data:
            self.app.alert("No car assigned")
            return
        
        for data in all_data:
            if data not in car_items:
                car_items.append(data) 

        if not car_items: return

        if self.app.dialog: 
            self.app.dialog.dismiss(force=True)
            self.app.dialog = None
        if not self.app.dialog:
            items = []
            for car in car_items:
                items.append(ItemConfirm(text=car[0],category=str(car[1]), grouped="service_car", is_dialog=True))
            self.app.dialog = MDDialog()
            self.app.dialog.title="Car Type"
            self.app.dialog.type="confirmation"
            self.app.dialog.items = items
            self.app.dialog.create_buttons()
            self.app.dialog.create_items()
            self.app.dialog.open()

    def dialog(self):
        menu_items = []
        if self.category == "tow_service":
            for all_data in self.tow_data.values():
                for data in all_data:
                    menu_items.append(data["car"])
        if self.category == "puncture_service":
            for all_data in self.puncture_data.values():
                for data in all_data:
                    menu_items.append(data["car"])
        if self.category == "general_service":
            menu_items = self.service_data.keys()
        if not menu_items: return
        
        if self.app.dialog: 
            self.app.dialog.dismiss(force=True)
            self.app.dialog = None
        if not self.app.dialog:
            items = []
            for menu in menu_items:
                items.append(ItemConfirm(text=menu,category=menu, grouped=self.category, is_dialog=True))
            self.app.dialog = MDDialog()
            self.app.dialog.title="Car Type" if self.category != "general_service" else "Services"
            self.app.dialog.type="confirmation"
            self.app.dialog.items = items
            self.app.dialog.create_buttons()
            self.app.dialog.create_items()
            self.app.dialog.open()
    
    def get_cost(self,car="",cost=""):
        cost_data = "Cost: 0 Ksh."
        if cost:
            cost_data = f"Cost: {cost} Ksh."
        self.ids.car_service_type.text = car
        self.ids.service_cost.text = cost_data

    def set_item(self,text_item=""):
        if text_item:           
            cost = "Cost: 0 Ksh."
            target = None

            if self.category == "tow_service":
                target = self.tow_cost["Tow Service"]
            if self.category == "puncture_service":
                target = self.puncture_cost["Puncture"]
            
            exists = False
            for x in target:
                if x[0] == text_item:
                    cost = f"Cost: {x[1]} Ksh."
                    exists = True
            if exists:
                self.ids.car_type.text = text_item
            self.ids.cost.text = cost

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
        if self.category == "general_service":
            self.ids.service_location.text = address
            return
        self.ids.location.text = address

    def search_specific(self,category=""):
        found = False
        for data in self.data_dict['service']:
            if data['tag'] == category: found = True
        return found
    
    def ask_for_tow(self,widget):
        self.refresh_data()
        if not self.data_dict['service'] or not self.search_specific("tow"): return self.app.alert("Service not available")
        self.app.hide_widget(self.ids.ask_help,dohide=False)
        self.ids.puncture.disabled = True
        self.ids.tow.disabled = True
        self.ids.service.disabled = True
        self.ids.store.disabled = True
        self.ids.cost.text = "Cost: 0 Ksh."
        self.category = "tow_service"

        self.ids.service_title.text = "Tow Service"

    def has_puncture(self,widget):
        self.refresh_data()
        if not self.data_dict['service']  or not self.search_specific("puncture"): return self.app.alert("Service not available")
        self.app.hide_widget(self.ids.ask_help,dohide=False)
        self.ids.tow.disabled = True
        self.ids.puncture.disabled = True
        self.ids.service.disabled = True
        self.ids.store.disabled = True
        self.category = "puncture_service"
        self.ids.cost.text = "Cost: 0 Ksh."
        self.ids.service_title.text = "Puncture Repair"

    def need_service(self,widget):
        self.refresh_data()
        if not self.data_dict['service'] or not self.search_specific("service"): return self.app.alert("Service not available")
        self.app.hide_widget(self.ids.service_popup,dohide=False)
        self.ids.tow.disabled = True
        self.ids.puncture.disabled = True
        self.ids.service.disabled = True
        self.ids.store.disabled = True
        self.category = "general_service"
        self.ids.cost.text = "Cost: 0 Ksh."

        self.ids._service_title.text = "Car Service"
        self.ids.car_type.hint_text = "* Service Type"

    def ask(self):
        required = []
        message = ""
        cost_data = "Cost: 0 Ksh."
        if self.category == "general_service":
            car_type = self.ids.car_service_type.text
            location = self.ids.service_location.text
            cost_data = self.ids.service_cost.text
            service = self.ids.service_type.text
            required = [car_type,location,service]
            message = f"{service} for a {car_type}:: {location}"

        if self.category == "puncture_service":
            location = self.ids.location.text
            car_type = self.ids.car_type.text
            cost_data = self.ids.cost.text
            required = [car_type,location]
            message = f"Puncture repair for {car_type}:: {location}"
        if self.category == "tow_service":
            location = self.ids.location.text
            cost_data = self.ids.cost.text
            car_type = self.ids.car_type.text
            required = [car_type,location]
            message = f"Tow a {car_type}:: {location}"

        cost = int(cost_data.split(" ")[1])

        for x in required:
            if not x or x == "":
                self.app.alert("All fields marked * required!")
                return
        
        data = {
            "reqmail":self.app.reqmail,
            "message":message,
            "cost":cost,
        }

        data = str(data).replace("'",'"')

        try:
            response = requests.post(self.req_url,data,headers=headers)
            data = response.json()
            
            if response.status_code != 200: 
                self.app.alert(text=data["message"])
                return
        except:
            self.app.alert(text="Server seem down")
            return
        
        self.app.alert("Request sent. Please wait.")
        
        self.ids.service_location.text = ""
        self.ids.service_cost.text = "Cost: 0 Ksh."
        self.ids.service_type.text = ""
        self.ids.car_service_type.text = ""
        self.ids.car_type.text = ""
        self.ids.location.text = ""
        self.ids.cost.text = "Cost: 0 Ksh."
        self.ids.puncture.disabled = False
        self.ids.tow.disabled = False
        self.ids.service.disabled = False
        self.ids.store.disabled = False
        self.app.hide_widget(self.ids.ask_help)
        self.app.hide_widget(self.ids.service_popup)

            
        
