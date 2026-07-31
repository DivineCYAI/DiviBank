from rich.prompt import Prompt, IntPrompt
from bank_helpers import (
    console, 
    network_prefixes, 
    clear_screen, 
    create_and_login_screen, 
    register,
    login,
    dashboard
)


bank_logged_in = True

while bank_logged_in:
    clear_screen()
    create_and_login_screen()
    choice = Prompt.ask("\nSelect an option", choices=["1", "2"])
    
    if choice == "1":
        clear_screen()
        register()
    elif choice == "2":
        logged_user = login()  
        if logged_user:            
            dashboard(logged_user)         
  
    
# MAIN FILE        
