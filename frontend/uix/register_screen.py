from kivymd.uix.screen import MDScreen
import requests

from .commons import *

class RegisterManager(MDScreen):
    reg_url = base_url+"register"
    def register(self):
        email = self.ids.email.text
        passwd = self.ids.passwd.text
        confpass = self.ids.confpasswd.text
        
        for x in [email,passwd,confpass]:
            if x == None or x == "":
                self.app.alert(text = "Fields marked * are required")
                return
        
        if passwd != confpass:
            self.app.alert(text = "Passwords didn't match!")
            return
        
        
        data = {
            "email": email,
            "passwd": passwd,
        }

        data = str(data).replace("'",'"')

        try:
            response = requests.put(self.reg_url,data,headers=headers)
            data = response.json()
            
            if response.status_code != 201: 
                self.app.alert(text=data["message"])
                return
            else:
                self.app.alert(text="Registration successful")
                self.manager.transition.direction = "right"
                self.manager.current = "signin"
        except:
            self.app.alert(text="Server seem down")
            return
        finally:
            self.ids.email.text = ""
            self.ids.passwd.text = ""
            self.ids.confpasswd.text = ""
 