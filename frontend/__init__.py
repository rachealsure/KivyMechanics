from kivy.uix.screenmanager import ScreenManager
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivymd.uix.snackbar import Snackbar
from kivy.utils import rgba
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog

from .uix.commons import ItemConfirm
from .uix import *

Builder.load_file("frontend/widgets/common.kv")

Window.size = (310,600)

LabelBase.register(name="MPoppins",fn_regular="frontend/assets/fonts/Poppins/Poppins-Medium.ttf")
LabelBase.register(name="BPoppins",fn_regular="frontend/assets/fonts/Poppins/Poppins-Bold.ttf")
LabelBase.register(name="BIPoppins",fn_regular="frontend/assets/fonts/Poppins/Poppins-BoldItalic.ttf")
LabelBase.register(name="Motion",fn_regular="frontend/assets/fonts/motion-font/motion.ttf")

class CustomSnackbar(Snackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("15sp")
 
class AutoSparesApp(MDApp):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.title = "Rosslyn Gates AutoGarage"
      
        self.dialog = None
        
        self.reqmail = ""
        self.is_admin = False
        self.user_id = 0

        self.is_loggedin = False

        self.screen_manager = ScreenManager()
    
    
    def hide_widget(self, wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True

    
    def set_selection(self,category="",value="",grouped="",is_dialog=False,dialog=None):
        if is_dialog:
            if self.dialog: self.dialog.dismiss(force=True)
            
            main = self.screen_manager.get_screen("main")
            store = self.screen_manager.get_screen("store")
            admin = self.screen_manager.get_screen("admin")

            if grouped == "tow_service":
                main.set_item(text_item=value)
            if grouped == "puncture_service":
                main.set_item(text_item=value)
            if grouped == "general_service":
               main.ids.service_type.text = value
            if grouped == "tire":
                store.set_item(text_item = value,info=category)
            if grouped == "steer":
                store.set_item(text_item = value,info=category)
            if grouped == "light":
                store.set_item(text_item = value,info=category)
            if grouped == "oil":
                store.set_item(text_item = value,info=category)
            if grouped == "battery":
                store.set_item(text_item = value,info=category)
            if grouped == "coolant":
                store.set_item(text_item = value,info=category)
            
            if grouped == "service_car":
                main.get_cost(car=value,cost=category)
            
            if grouped == "service":
                admin.ids.service_type.text = value
                admin.tag = category
            if grouped == "car":
                if category == "store":
                    admin.ids.store_car.text = value
                if category == "service":
                    admin.ids.service_car.text = value
            if grouped == "tag":
                admin.ids.store_tag.text = value
                
            self.dialog = None
            
       
    def alert(self,text=None):
        if not text: text = "Something went wrong"
        snackbar = CustomSnackbar(
            text=text,
            icon="information",
            snackbar_x="10dp",
            snackbar_y="10dp",
            duration=1,
            bg_color=rgba(125,202,222,255),
        )
        snackbar.size_hint_x = (
            Window.width - (snackbar.snackbar_x * 2)
        ) / Window.width
        snackbar.open()

    def hide(self):
        store = self.screen_manager.get_screen("store")
        home = self.screen_manager.get_screen("main")
        admin = self.screen_manager.get_screen("admin")
        quick_popup = store.ids.quick_store
        store_popup = store.ids.my_cart
        home_popup1 = home.ids.ask_help
        home_popup2 = home.ids.service_popup
        home_popup3 = home.ids.notification
        admin_popup1 = admin.ids.add_resouce
        admin_popup2 = admin.ids.add_services
        admin_popup3 = admin.ids.orders_popup
        admin_popup4 = admin.ids.add_managers

        hide_widget = [store_popup,home_popup1,home_popup2,home_popup3,admin_popup1,admin_popup2,admin_popup3,admin_popup4,quick_popup]
        for x in hide_widget:
            self.hide_widget(x)
    
    def on_start(self):
        Clock.schedule_once(self.login, 5)
    
    def login(self,*args):
        self.screen_manager.current = "welcome"


    def build(self):
        
        self.screen_manager.add_widget(Builder.load_file("frontend/widgets/splash.kv"))
        self.screen_manager.add_widget(Builder.load_file("frontend/widgets/welcome.kv"))
        self.screen_manager.add_widget(Builder.load_file("frontend/widgets/signin.kv"))
        self.screen_manager.add_widget(Builder.load_file("frontend/widgets/register.kv"))
        self.screen_manager.add_widget(Builder.load_file("frontend/widgets/home.kv"))
        self.screen_manager.add_widget(Builder.load_file("frontend/widgets/admin.kv"))
        self.screen_manager.add_widget(Builder.load_file("frontend/widgets/store.kv"))
        self.screen_manager.add_widget(Builder.load_file("frontend/widgets/update.kv"))
        self.hide()
        
        return self.screen_manager


