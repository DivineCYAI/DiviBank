import os
import sys
import time
import sqlite3
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
import hashlib, getpass, random, secrets, string
from datetime import timezone, datetime, timedelta

APP_PREFIX = "DIB"
CURRENT_CHANNEL = "CONSOLE"

network_prefixes = {
    "MTN": [
        "0803", "0806", "0703", "0704", "0706",
        "0810", "0813", "0814", "0816",
        "0903", "0906", "0913", "0916"
    ],

    "Airtel": [
        "0802", "0808", "0701", "0708",
        "0812",
        "0901", "0902", "0904", "0907",
        "0912"
    ],

    "Glo": [
        "0805", "0807", "0705",
        "0811", "0815",
        "0905", "0915"
    ],

    "9mobile": [
        "0809", "0817", "0818",
        "0908", "0909"
    ]
}


num_months = {
    1: ["January", "Jan"],
    2: ["February", "Feb"],
    3: ["March", "Mar"],
    4: ["April", "Apr"],
    5: ["May", "May"],
    6: ["June", "Jun"],
    7: ["July", "Jul"],
    8: ["August", "Aug"],
    9: ["September", "Sep"],
    10: ["October", "Oct"],
    11: ["November", "Nov"],
    12: ["December", "Dec"]
}


WEIGHTS   = [3, 7, 3, 3, 7, 3, 3, 7, 3]

VALID_NETWORKS = ["MTN", "Airtel", "Glo", "9mobile"]

gender = ["MALE", "FEMALE", "OTHERS"]

class InvalidPhoneError(Exception):
    pass

class InvalidNameError(Exception):
    pass

class InvalidEmailError(Exception):
    pass

class InvalidHomeAddressError(Exception):
    pass

class InvalidBvnError(Exception):
    pass

class PasswordValidationError(Exception):
    pass    

class PinValidationError(Exception):
    pass           
                                 
def print_asterisks():
    console.print("[bold cyan]*[/bold cyan]" * 59)

def print_line(label, value, width=55):
    console.print(f"{label:<20} {str(value):>{width-20}}")

def connect_database():
    conn = sqlite3.connect('bank.db')

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            acc_number TEXT UNIQUE NOT NULL,
            acc_created_at TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            hashed_pin TEXT NOT NULL,
            balance REAL DEFAULT 0 CHECK (balance >=0),
            date_of_birth TEXT NOT NULL,
            phone_no TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            bvn TEXT UNIQUE NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    #column_name  DATA_TYPE  [optional rules]

def gen_acc_no() -> str:
   BANK_CODE = "673"
   serial_number = "".join(str(random.randint(0, 9)) for _ in range(6))
   base = BANK_CODE + serial_number
   total = sum(int(base[i]) * WEIGHTS[i] for i in range(9))
   check = (10 - (total % 10)) % 10
   acc_no = base + str(check)
   return acc_no

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

console = Console()

def validate_name(name):
    allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 -.'&")
    
    name = name.strip() 
    
    if not name:
        raise InvalidNameError("Name cannot be empty")
    if len(name) > 50: 
        raise InvalidNameError("Name is too long")
    if not set(name).issubset(allowed_chars):
        raise InvalidNameError("Name contains invalid characters. Only letters, numbers, space, -, ., ', & allowed")
    
    return name

def create_and_login_screen():
    header_text = (
        f"{'[bold cyan]DIVIBANK[/bold cyan]':^75}"
        f"""

"""        
        f"{'[dim gray]Your money, your control.[/dim gray]':^75}"        
        f"""

"""
        f"{'[bold cyan]WELCOME TO DIVIBANK[/bold cyan]':^75}"
        f"""

"""      
        f"{'[dim gray]Open a free account in minutes.[/dim gray]':^75}\n"
        f"{'[dim gray]No hidden charges. No stress.[/dim gray]':^75}"
)
    console.print(Panel(header_text, border_style="blue", expand=False))
    print()
    console.print("[bold cyan]1. Create Account           [/bold cyan]")
    console.print("[bold cyan]2. I already have an account[/bold cyan]")  

def acc_created_date_and_time():
    # WAT = West Africa Time = UTC + 1 hour
    WAT = timezone(timedelta(hours=1))
    # Get current local time in Nigeria
    created_date_and_time = datetime.now(WAT)
    date_and_time = created_date_and_time.strftime("%Y-%m-%d|%H:%M:%S:%f")
    return date_and_time

def get_birth_year():
    while True:
        console.print("[bold white]What year were you born?[/bold white]")
        console.print("1. 2000s")
        console.print("2. 1900s")
        console.print("3. Others (before 1900)")
        choice = console.input("[bold white]Select choice (1/2/3): [/bold white]").strip()

        if choice == "1":        # 2000s
            while True:
                inp = console.input("[bold white]Enter the last 2 digits (e.g. 06 for 2006, or 25 for 2025): [/bold white]").strip()
                try:
                    num = int(inp)
                    if 0 <= num <= 99:
                        year = 2000 + num
                        year_str = f"{year:04}" 
                        #console.print(f"[green]Formatted year: {year_str}[/green]")
                        return year_str
                    else:
                        console.print("Please enter a number between 0 and 99.")
                except ValueError:
                    console.print("Please enter numbers only.")

        elif choice == "2":      
            while True:
                inp = console.input("[bold white]Enter the last 2 digits (e.g. 85 for 1985): [/bold white]").strip()
                try:
                    num = int(inp)
                    if 0 <= num <= 99:
                        year = 1900 + num
                        year_str = f"{year:04}"
                        #console.print(f"[green]Formatted year: {year_str}[/green]")
                        return year_str
                    else:
                        console.print("Please enter a number between 0 and 99.")
                except ValueError:
                    console.print("[bold red]Please enter numbers only.[/bold red]")

        elif choice == "3":      
            while True:
                inp = console.input("[bold white]Enter full year (4 digits max, e.g. 1895 or 1453): [/bold white]").strip()
                try:
                    year = int(inp)
                    if 1 <= year <= 1899:
                        year_str = f"{year:04}"
                        #console.print(f"[green]Formatted year: {year_str}[/green]")
                        return year_str
                    elif year > 1899:
                        console.print("For years 1900+, please choose option 1 or 2.")
                    else:
                        console.print("Year must be at least 1.")
                except ValueError:
                    console.print("[bold red]Please enter a valid number.[/bold red]")

        else:
            console.print("[bold red]Invalid choice. Please select 1, 2, or 3.[/bold red]")

def check_password(password: str) -> bool:
    password = password.strip()
    if not (8 <= len(password) <= 10):
        raise PasswordValidationError("Password must be between 8 and 10 characters long.")
    if not any(char.islower() for char in password):
        raise PasswordValidationError("Password must contain at least one lowercase letter.")
    if not any(char.isupper() for char in password):
        raise PasswordValidationError("Password must contain at least one uppercase letter.")
    if not any(char.isdigit() for char in password):
        raise PasswordValidationError("Password must contain at least one number.")
    special_characters = '!@#$%^&*(),.?":{}|<>'
    if not any(char in special_characters for char in password):
        raise PasswordValidationError("Password must contain at least one special character.")
    
    return True

def check_pin(pin: str) -> bool:
    pin = pin.strip()
    if len(pin) != 4:
        raise PinValidationError("PIN must be exactly 4 digits long.")
    if not pin.isdigit():
        raise PinValidationError("PIN must contain numbers only.")
    # Block identitical numbers
    if len(set(pin)) == 1:
        raise PinValidationError("PIN cannot be identical numbers (e.g., 1111).")
    # Block repititive sequence
    if pin in "0123456789" or pin in "9876543210":
        raise PinValidationError("PIN cannot be sequential numbers (e.g., 1234).")
        
    return True

def generate_txn_id() -> str:
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    ts_ms = utc_now.strftime("%Y%m%d%H%M%S%f")[:-3]
    alphabet = string.ascii_uppercase + string.digits
    rand = "".join(secrets.choice(alphabet) for _ in range(6))
    return f"{APP_PREFIX}-{CURRENT_CHANNEL}-{ts_ms}-{rand}"
    
prefixes_to_network = {}
for network, prefixes in network_prefixes.items():
    for prefix in prefixes:
        prefixes_to_network[prefix] = network
        
def get_network(phone: str) -> str:
    phone = clean_nigerian_phone(phone)
    prefix = phone[ : 4]
    detected_network = prefixes_to_network.get(prefix, "Unkown")
    return detected_network
    
def clean_nigerian_phone(number: str) -> str:
    number = "".join(ch for ch in number if ch.isdigit()) 
    if len(number) == 10 and number[0] in "789":
        number = "0" + number 
    elif len(number) == 11 and number.startswith("0"):
        pass
    else:
        raise InvalidPhoneError("Enter 10 digits after +234. e.g. 8012345678")

    if number[1] not in "789":
        raise InvalidPhoneError("Invalid network code. Use 070, 080, or 090")

    return number

def validate_bvn(bvn):
    bvn = bvn.strip()

    if not bvn.isdigit():
        raise InvalidBvnError("Invalid: BVN must be only numbers")
    if len(bvn)!= 11:
        raise InvalidBvnError("Invalid: BVN must be 11 digits")
    if bvn[0] in ["0", "1"]:
        raise InvalidBvnError("Invalid: BVN cannot start with 0 or 1")

    return bvn

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise InvalidEmailError("Invalid email format. Example: name@gmail.com")
        return False
    
    if len(email) > 254:
        raise InvalidEmailError("Email is too long")
        return False
        
    return email

def validate_address(address):
    address = address.strip()  
    if len(address) < 5:
        raise InvalidHomeAddressError("Invalid: Address too short. Enter full address")
    
    if len(address) > 200:
        raise InvalidHomeAddressError("Invalid: Address too long. Max 200 characters")
    
    if not re.search(r'[a-zA-Z]', address):
        raise InvalidHomeAddressError("Invalid: Address must contain letters")
    if not re.search(r'[0-9]', address):
        raise InvalidHomeAddressError("Invalid: Address should include house number")
    
    if not re.search(r'[a-zA-Z0-9,./ - ]', address):
        raise InvalidHomeAddressError("Invalid: Use letters, numbers, comma, dot, / or -")
        
    return address            

def print_step_header(step, title, *subtitle_lines):
    clear_screen()
    print_asterisks()
    
    console.print(f"[dim gray]Step {step} of 5[/dim gray]\n")
    console.print(f"[bold white]{title}[/bold white]\n")
    
    for line in subtitle_lines:
        console.print(f"[dim gray]{line}[/dim gray]")
    
    print_asterisks()
    print()                                    
                                                         
def register():
    print_step_header(1, "Personal Details", "Tell us who you are")
    print_asterisks()
    console.print("[dim gray]First name[/dim gray]")
    user_first_name = None
    user_last_name = None
    while True:
        first_name = input().strip().title()
        try:
            user_first_name = validate_name(first_name)
            break
        except InvalidNameError as e:
            console.print(f"[bold red]{e}[/bold red]")
            print()
    print()
    print_asterisks()
    console.print("[dim gray]Last name[/dim gray]")
    while True:
        last_name = input().strip().title()
        try:
            user_last_name = validate_name(last_name)
            break
        except InvalidNameError as e:
            console.print(f"[bold red]{e}[/bold red]")
            print()
    print()
    print_asterisks()
    console.print("[dim gray]Date of Birth[/dim gray]")
    print()
    while True:
        console.print(f"[bold white]Day:[/bold white]", end = "")
        day = input().strip()
        if not day:
            console.print("[bold red]Day section cannot be empty[/bold red]")
        try:
            day = int(day)            
            if day <= 31 and day > 0:
                break
            else:
                console.print("[bold red]Day cannot be greater than 31 or lesser than 0[/bold red]")
        except ValueError:
            console.print("[bold red]Only whole numbers are allowed[/bold red]")
    day_str = f"{day:02d}"
    
    month_num = None
    while True:
        console.print(f"[bold white]Month:[/bold white]", end = "")

        user_month = input().strip().title()
        if user_month.isdigit():
            num = int(user_month)
            if num in num_months:
                month_num = f"{num:02d}"
                break
            else:
                console.print("[bold red]Invalid month number\nEnter any number between 1 and 12[/bold red]")
        else:
            found = False
            for num, months in num_months.items():
                if user_month in months:  
                    month_num = f"{num:02d}"
                    print(month_num)
                    found = True
                    break
            if not found:
                console.print("[bold red]Invalid month name[/bold red]")
            else:
                break
    print()
    console.print(f"[bold white]Year[/bold white]")
    year = get_birth_year()
    year_str = str(year)

    name = f"{user_first_name} {user_last_name}"
    date = f"{year_str}-{month_num}-{day_str}"
    console.print(f"[bold green]Date of Birth\nDate:{date}[/bold green]") 

    print_asterisks()    
    console.print("[dim gray]Gender[/dim gray]")
    gend = (
        f"[bold white]1. MALE[/bold white]\n"
        f"[bold white]2. FEMALE [/bold white]\n"
        f"[bold white]3. OTHERS [/bold white]"
)
    
    console.print(gend)
    choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3"])
    gend = gender[int(choice) - 1]
    console.print("[bold gray]Proceeding to the next step...[/bold gray]")
    print_asterisks()
    time.sleep(2)
    
    print_step_header(2, "Contact Info", "How can we reach you?")
    print_asterisks()
    console.print("[dim gray]Phone number[/dim gray]")
    cleaned_no = None
    while True:
        console.print("[bold green]+234 | [bold green]", end = "")
        phone_no = input().strip()
        try:
            cleaned_no =  clean_nigerian_phone(phone_no)
            break
        except InvalidPhoneError as e:
            console.print(f"[bold red]{e}[bold red]")
    print(cleaned_no)
    console.print("[dim gray]Email Address[/dim gray]")
    validated_email = None
    while True:
        console.print("[bold green]Email: [bold green]", end = "")
        user_email = input().strip()
        try:
            validated_email = validate_email(user_email)
            break
        except InvalidEmailError as e:
            console.print(f"[bold red]{e}[/bold red]")
    print(validated_email)
    
    console.print("[dim gray]Home Address[/dim gray]")
    validated_home_address = None
    while True:
        console.print("[bold green]Address: [bold green]", end = "")
        user_address = input().strip()
        try:
            validated_home_address = validate_address(user_address)
            break
        except InvalidHomeAddressError as e:
            console.print(f"[bold red]{e}[/bold red]")
    print(validated_home_address)
    console.print("[bold gray]Proceeding to the next step...[/bold gray]")
    print_asterisks()
    time.sleep(2)
    
    print_step_header(
        3, 
        "BVN", 
        "Required by CBN for all accounts",              "What is BVN", 
        "Bank verification Number — your unique 11-digit CBN identity.")
    print_asterisks()    
    console.print("[dim gray]BVN[/dim gray]")
    validated_bvn = None
    while True:
        console.print("[bold green]BVN: [bold green]", end = "")
        user_bvn = input().strip()
        try:
            validated_bvn = validate_bvn(user_bvn)
            break
        except InvalidBvnError as e:
            console.print(f"[bold red]{e}[/bold red]")
    print(validated_bvn)
    console.print("[bold gray]Proceeding to the next step...[/bold gray]")
    print_asterisks()
    time.sleep(2)

# --- GENERATE ACCOUNT NUMBER HERE ---
    # date and time acc was created
    created_date_and_time = acc_created_date_and_time()
    account_number = gen_acc_no() 
            
    print_step_header(4, "Secure Your Account", "Create a login password")
    print_asterisks()
    
    console.print(f"[bold gold1]Congratulations! Your unique Account Number is: {account_number}[/bold gold1]")
    console.print("[dim gray]Please save this number. You will use it to log in.[/dim gray]\n")
    print_asterisks()
    
    # --- PASSWORD SIGN-UP LOOP ---
    console.print("[dim gray]Create Password[/dim gray]")
    password_hashed = None   
    while True:
        password = getpass.getpass("Password: ")
        try:
            check_password(password) # Your exception validator
            while True:
                confirm_password = getpass.getpass("Confirm Password: ")
                if password == confirm_password:
                    password_byte = password.encode()
                    password_hashed = hashlib.sha256(password_byte).hexdigest()
                    break
                else:
                    console.print(f"[bold red]Password do not match[/bold red]")
            break
        except PasswordValidationError as e:
            console.print(f"[bold red]Invalid password: {e}[/bold red]\n")
            
    print_asterisks()
    time.sleep(2)         

    print_step_header(5, "Set Transaction Pin", "You'll use this to authorise all payments")
    print_asterisks()
    console.print("[dim gray]ENTER PIN[/dim gray]\n")
    pin_hashed = None   
    while True:
        pin = getpass.getpass("PIN: ")
        try:
            check_pin(pin) #exception validator
            while True:
                confirm_pin = getpass.getpass("Confirm PIN: ")
                if pin == confirm_pin:
                    pin_byte = pin.encode()
                    pin_hashed = hashlib.sha256(pin_byte).hexdigest()
                    break
                else:
                    console.print(f"[bold red]PIN do not match[/bold red]")
            break
        except PinValidationError as e:
            console.print(f"[bold red]Invalid PIN: {e}[/bold red]\n")

    print_asterisks()
    time.sleep(2)
    clear_screen()

    # Set the initial opening balance 
    initial_balance = "5000.00"
    #for locked accounts currently empty
    #lock_time = ""

    # *********Save to bank.db*********
    connect_database()
    customer_data = (
        name, 
        account_number, 
        created_date_and_time, 
        password_hashed, 
        pin_hashed, 
        initial_balance, 
        date, 
        cleaned_no, 
        validated_email, 
        validated_bvn)
     #connect yo bank.db database
    conn = sqlite3.connect('bank.db')
    #create cursor
    cursor = conn.cursor()
    cursor.execute("INSERT INTO accounts (name, acc_number, acc_created_at, hashed_password, hashed_pin, balance, date_of_birth, phone_no, email, bvn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", customer_data)
    conn.commit()
    conn.close()

    # --- SAVE TO ACCOUNTS.TXT ---
    with open("accounts.txt", "a") as f:
        # Saving: acc_no, password, pin, balance, name, phone, email, bvn
        f.write(f"{account_number}|{password_hashed}|{pin_hashed}|{initial_balance}|"
                f"{name}|{date}|{cleaned_no}|{validated_email}|{validated_bvn}\n")


    text = (
        f"[bold green]{'*' * 59}[/bold green]\n"
        f"{'[bold gold1]OK[/bold gold1]':^78}\n"
        f"""
"""  
        f"{'[bold gold1]Account Created![/bold gold1]':^78}\n"
        f"""
""" 
        f"{f'[bold gold1]{name}[/bold gold1]':^78}\n"
        f"""
"""         
        f"{f'[dim gold1]{account_number}[/dim gold1]':^78}\n"
        f"""
"""         
        f"{'[dim green]N5,000 welcome bonus credited![/dim green]':^78}\n"
        f"""
""" 
        f"""
"""
        f"[bold green]{'*' * 59}[/bold green]\n"
        f"{'[bold green]Go to Dashboard[/bold green]':^78}\n"
        f"[bold green]{'*' * 59}[/bold green]"      
)        
    console.print(text)
    console.input("[dim gray]press enter...[dim gray]")
    time.sleep(2)
    clear_screen()

LOCK_FILE = "lock.txt"
BLOCK_TIME_MINUTES = 30
MAX_ATTEMPTS = 3

def is_account_locked(acc_no):
    """Check if account is locked and return remaining time in seconds"""
    if not os.path.exists(LOCK_FILE):
        return False, 0
    with open(LOCK_FILE, "r") as f:
        for line in f:
            row = line.strip().split("|")
            if len(row) >= 2 and row[0] == acc_no:
                lock_time = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                unlock_time = lock_time + timedelta(minutes=BLOCK_TIME_MINUTES)
                if datetime.now() < unlock_time:
                    remaining = unlock_time - datetime.now()
                    return True, remaining.total_seconds()
                else:
                    # lock expired, remove it
                    remove_lock(acc_no)
                    return False, 0
    return False, 0
    
def add_lock(acc_no):
    """Add account to lock file"""
    lock_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOCK_FILE, "a") as f:
        f.write(f"{acc_no}|{lock_time}\n")

def remove_lock(acc_no):
    """Remove account from lock file after lock expires"""
    if not os.path.exists(LOCK_FILE): return
    with open(LOCK_FILE, "r") as f:
        lines = f.readlines()
    with open(LOCK_FILE, "w") as f:
        for line in lines:
            if not line.startswith(acc_no + "|"):
                f.write(line)                            
def login() -> list | None:
    """
    Handles user login.
    Returns the user's data list (row) if successful, or None if failed.
    """
    clear_screen()
    banner = r"""[bold gold1]         ____  _       _ ____              _      
        |  _ \(_)_   _(_) __ )  __ _ _ __ | | __    
        | | | | \ \ / / |  _ \ / _` | '_ \| |/ /    
        | |_| | |\ V /| | |_) | (_| | | | |   <     
        |____/|_| \_/ |_|____/ \__,_|_| |_|_|\_\   

               Simple. Secure. Nigerian.[/bold gold1]"""
    console.print(Panel(banner, border_style="gold1", expand=False))    
    print()
    
    # 1. SYSTEM CHECK: If no accounts exist at all in the bank
    if not os.path.exists("accounts.txt"):
        console.print("[bold red]No registered accounts found yet![/bold red]")
        choice = input("[bold yellow]Press 1 to Create Account or 2 to Exit: [/bold yellow]").strip()
        if choice == "1":
            register() # jump to your register function
        return None

    with open("accounts.txt", "r") as f:
        accounts = [line.strip().split("|") for line in f if line.strip()]

    if not accounts:
        console.print("[bold red]No registered accounts found yet![/bold red]")
        choice = input("[bold yellow]Press 1 to Create Account or 2 to Exit: [/bold yellow]").strip()
        if choice == "1":
            register()
            return None
        
        elif choice == "2": 
            console.print("[bold green]Exiting...[/bold green]")
            return None # go back to main menu

        else: 
            console.print("[bold red]Invalid choice[/bold red]")
            return None
    
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        acc_no = input("Account NO: ").strip()
    
        # Use getpass to hide the password while typing!
        passcode = getpass.getpass("Enter your password: ").strip()
    
        # Hash the input password to match database format
        passcode_byte = passcode.encode()
        hashed_passcode = hashlib.sha256(passcode_byte).hexdigest()

        user_row = next((row for row in accounts if acc_no == row[0]), None)
            
        # 2. SECURITY: Don't reveal if account exists or not
        # Check lock first, but only if account exists
        if user_row:
            locked, seconds_left = is_account_locked(acc_no)
            if locked:
                mins = int(seconds_left // 60)
                secs = int(seconds_left % 60)
                console.print(f"[bold red]Account is temporarily locked. Try again in {mins}m {secs}s[/bold red]")
                time.sleep(2)
                return None

        # 3. CHECK LOGIN
        if user_row and hashed_passcode == user_row[1]:
            # Success
            full_name = user_row[4]
            first_name = full_name.split()[0]
            clear_screen()
            granted_access = f"\n[bold green] ✔ Access Granted! Welcome back, {first_name}  [/bold green]\n"
            console.print(Panel(granted_access, border_style="gold1", expand=False)) 
            time.sleep(1.5)
            return user_row
        else:
            # Failed - could be wrong acc_no OR wrong password. We treat them the same
            attempts += 1
            remaining = MAX_ATTEMPTS - attempts
            
            if remaining > 0:
                console.print(f"[bold red]\nInvalid Account No or Password. {remaining} attempts remaining.[/bold red]\n")
                time.sleep(1)
            else:
                # 4. LOCK ONLY IF THE ACCOUNT ACTUALLY EXISTS
                if user_row:
                    add_lock(acc_no)
                    console.print(f"[bold red]\nToo many failed attempts. Account locked for {BLOCK_TIME_MINUTES} minutes.[/bold red]")
                else:
                    console.print(f"[bold red]\nToo many failed attempts.[/bold red]")
                time.sleep(2)
                return None

    return None
            
#        6732688974, Divi@673, 1458
# 6739173608, Sanda@89, 5465
# 6731137705 Dave@453 1989
           
#login()   
            
#register()

def dashboard(user_data: list):
    
    """
    This is the customer's personal portal after successful login.
    """
    while True:
        clear_screen()
        full_name = user_data[4]
        first_name = full_name.split()[0]
        account_number = user_data[0]
        balance = float(user_data[3])
        console.print("[dim sky_blue1]Good day,[/dim sky_blue1]")        
        console.print(f"[bold white]{first_name}[/bold white]")
        text = (
            f"[dim sky_blue1]Available balance[/dim sky_blue1]\n"
            f"""
"""            
            f"[bold White]₦ {balance:,.2f}  [/bold white]\n"
            f"""
"""            
            f"[dim sky_blue1]Acct: {account_number}{full_name:>35}"
        )
        console.print(Panel(text, border_style="gold1", expand=False))
       # input()
        options = (       
            f"{'[bold white]Quick actions[/bold white]':^76}\n"
            f"""
"""            
            f"[dim sky_blue1]1. Transfer[/dim sky_blue1]\n"
            f"[dim sky_blue1]2. Withdraw[/dim sky_blue1]\n"
            f"[dim sky_blue1]3. Bills[/dim sky_blue1]\n"
            f"[dim sky_blue1]4. Airtime[/dim sky_blue1]\n"
            f"[dim sky_blue1]5. Data[/dim sky_blue1]\n"
            f"[dim sky_blue1]6. Transaction History[/dim sky_blue1]\n"
            f"[dim sky_blue1]7. Logout[/dim sky_blue1]\n"
)                
        
        console.print(Panel(options, border_style="gold1", expand=False))        
        choice = Prompt.ask("What would you like to do?", choices=["1", "2", "3", "4", "5", "6", "7"])
        
        if choice == "1":
            console.print("\n[yellow]Transfer feature coming soon!...[/yellow]")
            time.sleep(2)
        if choice == "2":
            console.print("\n[yellow]Withdrawal feature coming soon!...[/yellow]")
            time.sleep(2)
        if choice == "3":
            console.print("\n[yellow]Bills feature coming soon!...[/yellow]")
            time.sleep(2)
        if choice == "4":
            console.print("\n[yellow]Airtime feature coming soon!...[/yellow]")
            time.sleep(2)
        if choice == "5":
            console.print("\n[yellow]Data feature coming soon!...[/yellow]")
            time.sleep(2)
        if choice == "6":
            console.print("\n[yellow]Transaction History feature coming soon!...[/yellow]")
            time.sleep(2)
        elif choice == "7":
            console.print("\n[bold gray]Logging out securely...[/bold gray]")
            time.sleep(1.5)
            break                       
# BANK HELPERS FILE
"""print("+234 | ", end="") 
try:
    current_network = get_network(input())
    
    if current_network: 
        print(f"DETECTED NETWORK:  {current_network}")
        while True:
            confirm_network = input("Is this your network y/n? ").strip().lower()
            if confirm_network in ["n", "no"]:
                print("Select Network:")
                for i, network in enumerate(VALID_NETWORKS, start=1):
                    print(f"{i}. {network}")
                try:
                    choice = int(input("Enter number: "))
                    current_network = VALID_NETWORKS[choice - 1]
                    print(f"You selected: {current_network}")
                    print(f"CORRECTED NETWORK: {current_network}")
                    break
                except (ValueError, IndexError):
                    console.print("[bold red]Invalid choice. Enter 1-4[/bold red]")
            elif confirm_network in ["y", "yes"]:
                print("CONFIRMED")
                break
            else:
                console.print("[bold red]Invalid input enter y/n[/bold red]")
    else:
        new_network = input(f"Could not detect. Enter network manually {VALID_NETWORKS}: ").strip().title()
        current_network = new_network if new_network in VALID_NETWORKS else None
        print(f"Network set to: {current_network}")

except InvalidPhoneError:
   console.print("[bold red]Enter 10 digits after +234. e.g. 8012345678[/bold red]")
   
user_input = input("Enter month number 1-12: ")

if user_input.isdigit():
    num = int(user_input)
    if num in months:
        full, short = months[num]
        print(f"Full: {full}, Short: {short}")
    else:
        print("Invalid month number")"""


         