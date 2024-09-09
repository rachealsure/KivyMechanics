from kivymd.uix.screen import MDScreen
from .commons import *
import requests

class LoginManager(MDScreen):
    log_url = base_url+"login"
    def login(self):
        email = self.ids.email.text
        passwd = self.ids.passwd.text
        
        for x in [email,passwd]:
            if x == None or x == "":
                self.app.alert(text = "Email or Password missing")
                return
        
        data = {
            "email": email,
            "passwd": passwd,
        }
        data = str(data).replace("'",'"')
        try:
            response = requests.post(self.log_url,data,headers=headers)
            data = response.json()

            if response.status_code != 200: 
                self.app.alert(text=data["message"])
                return
            else:
                
                home = self.manager.get_screen("main")
                admin = self.manager.get_screen("admin")
                
                priv_user_id = data["priv"]
                user_priv, user_id = priv_user_id.split("::")

                self.app.user_id = int(user_id)
                self.app.is_loggedin = True
                
                self.app.reqmail = data["email"]
                self.app.is_admin = data["status"]
                
                if not self.app.is_admin:
                    home.ids.email.text = data["email"]

                    self.app.alert(text="Login successful")
                    self.manager.transition.direction = "left"
                    self.manager.current = "main"
                else:
                    admin.ids.email.text = data["email"]
                    
                    self.app.alert(text="Login successful")
                    self.manager.transition.direction = "left"
                    self.manager.current = "admin"
                        
                    
                
        except:
            self.app.alert(text="Server seem down")
            return
        finally:
            self.ids.email.text = ""
            self.ids.passwd.text = ""
        