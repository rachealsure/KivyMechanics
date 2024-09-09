from urllib.request import urlopen
from geopy.geocoders import Nominatim
import json
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import HoverBehavior
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivymd.uix.templates import ScaleWidget
from kivy.metrics import dp
from kivy.animation import Animation
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.list import OneLineAvatarIconListItem, TwoLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFlatButton
from kivymd.uix.relativelayout import MDRelativeLayout
import requests

base_url = "http://localhost:5000/api/v1/autogarage/"
headers = {'Content-type': 'application/json'}

class NoticeBlock(MDRelativeLayout):
    lbl_date = StringProperty()
    lbl_location = StringProperty()
    lbl_product = StringProperty()
    info = ObjectProperty()
    action = ObjectProperty()
    def on_release(self,*args):
        self.action(self)
    

class CustomItem(TwoLineIconListItem):
    text = StringProperty()
    secondary_text = StringProperty()
    icon = StringProperty("information-variant")
    info = ObjectProperty()

class CustomCartItem(MDCard):
        lbl_product = StringProperty()
        lbl_car = StringProperty()
        lbl_price = StringProperty()
        lbl_location = StringProperty()
        lbl_status = StringProperty()


class ShopCard(MDCard):
    source = StringProperty("frontend/assets/spares.png")
    product = StringProperty()
    description = StringProperty()
    info = ObjectProperty()

class ItemConfirm(OneLineAvatarIconListItem):
    dialog = ObjectProperty()
    category = StringProperty()
    grouped = StringProperty()
    is_dialog = BooleanProperty(False)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.divider = None

    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False

class Content(MDRelativeLayout):
    def get_gps(self):
        pass

class GPS:
    url='http://ipinfo.io/json'
    def __get_lon_lat__(self):
        response = urlopen(self.url)
        data = json.load(response)
        loc = None
        if data.get("loc"): loc = data["loc"]
        return loc

    def get_address(self,loc=None):
        if not loc: loc = self.__get_lon_lat__()
        getloc = Nominatim(user_agent="GetLoc")
        address = "Address unidentified"
        if loc:
            locname = getloc.reverse(loc)
            if locname: address = locname.address
        return address

class DescBox(MDBoxLayout):
    menu = None
    product = StringProperty()
    description = StringProperty()
    cost = StringProperty()
    car = StringProperty()
    tag = StringProperty()
    location = StringProperty()
    quantity = NumericProperty()
    app = ObjectProperty()
    price = NumericProperty()
    parent_widget = ObjectProperty()
    purchase_url = base_url+"purchase"

    def set_quantity(self,*args):
        if args:
            quantity = 0
            try:
                quantity = int(args[1])
                
                if quantity == 0:
                    self.ids.buy.disabled = True
                    raise(Exception)

                if int(quantity) > int(self.quantity): self.ids.quantity_field.text = str(self.quantity)
                
                self.ids.cost.text = f"Cost: {int(self.price) * int(self.ids.quantity_field.text)} Ksh."
                self.ids.quantity.text = f"Quantity: {self.ids.quantity_field.text}"
                self.ids.buy.disabled = False
            except:
                self.app.alert("Only numbers required!")
                self.ids.cost.text = "Cost: 0 Ksh."
                self.ids.quantity.text = "Quantity: 0"
                self.ids.buy.disabled = True
                return
            
    def cancel(self,*args):
        if self.app.dialog: self.app.dialog.dismiss(force=True)
        self.app.dialog = None
        if self.parent_widget: self.parent_widget.on_leave()
        return
    
    def get_location(self,*args):
        if self.app.dialog: self.app.dialog.dismiss(force=True)
        self.location = self.app.dialog.content_cls.ids.location.text
        
        self.app.dialog = None

        self.buy()
        return

    def get_location_dialog(self,parent):
        if self.app.dialog: 
            self.app.dialog.dismiss(force=True)
            self.app.dialog = None
        if not self.app.dialog:
            self.parent_widget = parent
            self.app.dialog = MDDialog(
                title="Your Location:",
                type="custom",
                content_cls=Content(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.app.theme_cls.primary_color,
                        on_release=self.cancel,
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.app.theme_cls.primary_color,
                        on_release=self.get_location,
                    ),
                ],
            )
            self.app.dialog.open()

    def buy(self):
        car_type = self.car
        quality = self.product
        quantity = int(self.ids.quantity.text.split(" ")[1])
        location = self.location

        cost = int(self.ids.cost.text.split(" ")[1])

        for x in [car_type,quality,quantity,location]:
            if x == None or x == "":
                self.app.alert("Invalid Request")
                return

        message = f"{quality}:: {location}"

        data = {
            "reqmail":self.app.reqmail,
            "tag":self.tag,
            "quantity":quantity,
            "product":quality,
            "car":car_type,
            "cost":cost,
            "message":message,
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
        
        store = self.app.screen_manager.get_screen("store")
        store.force_refresh()
        store.load_products()
        if self.parent_widget: self.parent_widget.on_leave()

class ScaleImage(Image,ScaleWidget):
    scale_value_x = NumericProperty(0.7)
    scale_value_y = NumericProperty(0.7)

class ScaleCard(MDFloatLayout,HoverBehavior):
    desc = None
    open_card = False
    product = StringProperty()
    description = StringProperty()
    car = StringProperty()
    tag = StringProperty()
    quantity = NumericProperty()
    cost = NumericProperty()
    source = StringProperty("frontend/assets/spares.png")

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.anim_big_image = Animation(
            scale_value_x=1,
            scale_value_y=1,
            pos_hint={"center_x":.9},
            d=0.4,
            t="in_quart",
        )
        self.anim_big_image.bind(on_complete=self.show_desc_box)

        self.anim_small_image = Animation(
            scale_value_x=.7,
            scale_value_y=.7,
            pos_hint={"center_x":.5},
            d=0.4,
            t="in_quart",
        )

        self.anim_small_image.bind(on_complete=self.hide_item)
    
    def show_desc_box(self,*args):
        if self.desc: self.remove_widget(self.desc)
        self.desc = DescBox(
            y=self.y+dp(24),
            product = self.product,
            description = self.description,
            quantity = self.quantity,
            app=self.app,
            car=self.car,
            tag=self.tag,
            price=self.cost,
            )
        self.add_widget(self.desc,index=-1)
        Animation(
            pos_hint={"center_x":.5},
            opacity=1,
            d=.1,         
        ).start(self.desc)
    
    def lock_store(self,disable=True):
        store = self.app.screen_manager.get_screen("store")
        widgets = [
            store.ids.tire_card,
            store.ids.steer_card,
            store.ids.light_card,
            store.ids.oil_card,
            store.ids.batt_card,
            store.ids.cool_card,
        ]

        for wid in widgets:
            wid.disabled = disable

    def on_enter(self):
        if self.app.dialog: return
        if self.desc:
            self.remove_widget(self.desc)
        
        if not self.open_card:
            self.anim_big_image.start(self.ids.image)
            Animation(
                size=(dp(280),dp(260)),
                radius=[dp(24),dp(24),dp(24),dp(24)],
                d=0.2,
                t="in_quad",
            ).start(self)
        self.open_card = True

        self.lock_store(True)

    def on_leave(self):
        if self.app.dialog: return
        self.anim_small_image.start(self.ids.image)
        
        if self.desc:
            self.remove_widget(self.desc)

        if self.open_card:
            Animation(
                size=(dp(200),dp(200)),
                radius=[dp(100),dp(100),dp(100),dp(100)],
                d=0.3,
                t="in_quart",
            ).start(self)
        self.open_card = False

    def hide_item(self,*args):
        self.app.screen_manager.get_screen("store").remove_widget(self)
        self.lock_store(False)

