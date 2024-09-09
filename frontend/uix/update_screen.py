from kivymd.uix.screen import MDScreen
import requests

from .commons import *

class UpdateManager(MDScreen):
    update_url = base_url+"update"
        
    def update(self):
        email = self.ids.email.text
        passwd = self.ids.passwd.text
        confpass = self.ids.confpasswd.text
        
        if passwd != confpass:
            self.app.alert(text = "Passwords didn't match!")
            return
        
        
        data = {
            "reqmail": self.app.reqmail,
            "email": email,
            "passwd": passwd,
        }

        data = str(data).replace("'",'"')
        home = self.manager.get_screen("main")
        admin = self.manager.get_screen("admin")
        try:
            response = requests.patch(self.update_url,data,headers=headers)
            data = response.json()
            
            if response.status_code != 201: 
                self.app.alert(text=data["message"])
                return
            else:
                self.app.alert(text="Update successful")

                if email:
                    if not self.app.is_admin:
                        home.ids.email.text = email
                    else:
                        admin.ids.email.text = email
                    self.app.reqmail = email

                if not self.app.is_admin:
                    self.manager.transition.direction = "right"
                    self.manager.current = "main"
                else:
                    self.manager.transition.direction = "right"
                    self.manager.current = "admin"
                    
               
        except:
            self.app.alert(text="Update Failed")
            return
        finally:
            self.ids.email.text = ""
            self.ids.passwd.text = ""
            self.ids.confpasswd.text = ""
 