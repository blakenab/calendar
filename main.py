from datetime import datetime, timedelta
import calendar


class Event:
    def __init__(self, title, start_time, end_time, shared_with=None):
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.shared_with = shared_with if shared_with else []
    
    def update_event(self, title=None, start_time=None, end_time=None):
        if title:
            self.title = title
        if start_time:
            self.start_time = start_time
        if end_time:
            self.end_time = end_time

    def share_event(self, user):
        if user not in self.shared_with:
            self.shared_with.append(user)
    
    def is_visible_to(self, user):
        return user in self.shared_with


class Calendar:
    def __init__(self, name, owner, time_zone="UTC", is_public=False):
        self.name = name
        self.owner = owner
        self.time_zone = time_zone
        self.is_public = is_public
        self.events = []
        self.shared_with = []

    def add_event(self, event):
        for existing_event in self.events:
            if (existing_event.start_time < event.end_time and event.start_time < existing_event.end_time):
                print("Error: Event overlaps with an existing event.")
                return
        self.events.append(event)
        print(f"Event '{event.title}' successfully added to '{self.name}'.")
    
    def remove_event(self, event_title):
        event_to_remove = next((event for event in self.events if event.title.lower() == event_title.lower()), None)

        if event_to_remove:
            self.events.remove(event_to_remove)
            print(f"Event '{event_title}' successfully deleted from '{self.name}'.")
        else:
            print(f"Error: Event '{event_title}' not found in calendar '{self.name}'. Please check the event name and try again.")


    
    def share_calendar(self, user):
        if user in self.shared_with:
            print(f"Calendar '{self.name}' is already shared with {user.username}.")
        else:
            self.shared_with.append(user)
            print(f"Calendar '{self.name}' shared with {user.username}.")

    
    def toggle_public_private(self):
        self.is_public = not self.is_public
        if self.is_public:
            print(f"Calendar '{self.name}' is now public.")
        else:
            print(f"Calendar '{self.name}' is now private.")
            self.shared_with = []  # Remove shared users when making it private

    def view_calendar(self, user, year, month):
        if not self.is_public and user != self.owner and user not in self.shared_with:
            print("Access denied. This is a private calendar.")
            return

        print(f"\nCalendar: {self.name} (Time Zone: {self.time_zone}) - {calendar.month_name[month]} {year}\n")
        
        month_days = calendar.monthrange(year, month)[1]
        
        for day in range(1, month_days + 1):
            day_events = [event for event in self.events if event.start_time.date() == datetime(year, month, day).date()]

            print(f"{month:02}/{day:02}:")
            
            if day_events:
                for event in day_events:
                    print(f"  - [{event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}] {event.title}")
            else:
                print("  - No events")

    def update_event(self, event_title):
        event = next((e for e in self.events if e.title == event_title), None)
        
        if not event:
            print(f"Event '{event_title}' not found.")
            return

        print(f"Updating event: {event.title} (Current: {event.start_time} to {event.end_time})")

        new_title = input("Enter new title (press Enter to keep current): ").strip()
        if new_title:
            event.title = new_title

        def get_valid_datetime(prompt, current_value):
            while True:
                new_input = input(prompt).strip()
                if not new_input:
                    return current_value  # Keep existing value
                try:
                    return datetime.strptime(new_input, "%Y-%m-%d %H:%M")
                except ValueError:
                    print("Invalid date format! Please use 'YYYY-MM-DD HH:MM'.")

        event.start_time = get_valid_datetime("Enter new start time (YYYY-MM-DD HH:MM): ", event.start_time)
        event.end_time = get_valid_datetime("Enter new end time (YYYY-MM-DD HH:MM): ", event.end_time)

        print(f"Event updated: {event.title} ({event.start_time} to {event.end_time})")


class User:
    def __init__(self, username):
        self.username = username
        self.calendars = []
        self.current_timezone = "UTC"
        self.current_timezone_offset = 0
    
    def create_calendar(self, name, time_zone="UTC", is_public=False):
        calendar = Calendar(name, self, time_zone, is_public)
        self.calendars.append(calendar)
    
    def delete_calendar(self, calendar_name):
        calendar_to_remove = next((cal for cal in self.calendars if cal.name == calendar_name), None)
        if calendar_to_remove:
            self.calendars.remove(calendar_to_remove)
            print(f"Calendar '{calendar_name}' deleted.")
        else:
            print(f"Calendar '{calendar_name}' not found.")
    
    def set_timezone(self, new_offset):
        try:
            new_offset = int(new_offset)
            time_difference = new_offset - self.current_timezone_offset
            for calendar in self.calendars:
                for event in calendar.events:
                    event.start_time += timedelta(hours=time_difference)
                    event.end_time += timedelta(hours=time_difference)
            self.current_timezone_offset = new_offset
            print(f"Timezone updated to UTC{new_offset:+}. All event times adjusted.")
        except ValueError:
            print("Invalid timezone format. Please enter a numeric value (e.g., -5 for UTC-5).")



class CalendarsApp:
    def __init__(self):
        self.users = {}
        self.current_user = None

    def register_user(self, username):
        if username in self.users:
            print("Username already exists. Please choose another one.")
            return None
        user = User(username)
        self.users[username] = user
        print(f"User '{username}' registered successfully.")
        return user
    
    def login(self, username):
        if username in self.users:
            self.current_user = self.users[username]
            print(f"Welcome back, {username}!")
        else:
            print("User not found. Please register first.")
    
    def logout(self):
        if self.current_user:
            print(f"User {self.current_user.username} logged out.")
            self.current_user = None
        else:
            print("No user currently logged in.")

    def run(self):
        print("Welcome to the Calendar App!")
        
        while True:
            if not self.current_user:
                action = input("Enter 'login', 'register', or 'exit': ").strip().lower()
                if action == "register":
                    username = input("Enter a username: ").strip()
                    self.register_user(username)
                elif action == "login":
                    username = input("Enter your username: ").strip()
                    self.login(username)
                elif action == "exit":
                    break
                else:
                    print("Invalid command. Please try again.")
            else:
                command = input("Enter command (create_calendar, add_event, view_calendar, update_event, delete_event, delete_calendar, set_timezone, share_calendar, toggle_privacy, logout, exit): ").strip().lower()
                if command == "create_calendar":
                    name = input("Enter calendar name: ").strip()
                    self.current_user.create_calendar(name)
                    print(f"Calendar '{name}' created.")
                elif command == "add_event":
                    calendar_name = input("Enter calendar name: ").strip()
                    calendar = next((c for c in self.current_user.calendars if c.name == calendar_name), None)
                    if calendar:
                        title = input("Enter event title: ").strip()
                        try:
                            start_time = datetime.strptime(input("Enter start time (YYYY-MM-DD HH:MM): "), "%Y-%m-%d %H:%M")
                            end_time = datetime.strptime(input("Enter end time (YYYY-MM-DD HH:MM): "), "%Y-%m-%d %H:%M")
                        except ValueError:
                            print("Invalid date format. Use YYYY-MM-DD HH:MM.")
                            continue
                        event = Event(title, start_time, end_time)
                        calendar.add_event(event)  
                    else:
                        print("Calendar not found.")
                elif command == "view_calendar":
                    calendar_name = input("Enter calendar name: ").strip()
                    calendar = next((c for c in self.current_user.calendars if c.name == calendar_name), None)
                    if calendar:
                        try:
                            year = int(input("Enter year: ").strip())
                            month = int(input("Enter month (1-12): ").strip())
                            calendar.view_calendar(self.current_user, year, month)
                        except ValueError:
                            print("Invalid input for year or month.")
                    else:
                        print("Calendar not found.")
                elif command == "update_event":
                    calendar_name = input("Enter calendar name: ").strip()
                    calendar = next((c for c in self.current_user.calendars if c.name == calendar_name), None)
                    if calendar:
                        event_title = input("Enter event title to update: ").strip()
                        calendar.update_event(event_title)  # Calls the method from Calendar class
                    else:
                        print("Calendar not found.")
                elif command == "share_calendar":
                    calendar_name = input("Enter calendar name: ").strip()
                    recipient_name = input("Enter username to share with: ").strip()
                    recipient = self.users.get(recipient_name)
                    if recipient:
                        calendar = next((c for c in self.current_user.calendars if c.name == calendar_name), None)
                        if calendar:
                            calendar.share_calendar(recipient)
                        else:
                            print("Calendar not found.")
                    else:
                        print("User not found.")
                elif command == "toggle_privacy":
                    calendar_name = input("Enter calendar name: ").strip()
                    calendar = next((c for c in self.current_user.calendars if c.name == calendar_name), None)
                    if calendar:
                        calendar.toggle_public_private()
                elif command == "delete_event":
                    calendar_name = input("Enter calendar name: ").strip()
                    calendar = next((c for c in self.current_user.calendars if c.name.lower() == calendar_name.lower()), None)
                    
                    if calendar:
                        event_title = input("Enter event title to delete: ").strip()
                        calendar.remove_event(event_title)  
                    else:
                        print("Error: Calendar not found.")

                elif command == "delete_calendar":
                    name = input("Enter calendar name to delete: ").strip()
                    self.current_user.delete_calendar(name)
                elif command == "set_timezone":
                    tz = input("Enter new timezone offset (e.g., -5 for UTC-5): ").strip()
                    self.current_user.set_timezone(tz)
                elif command == "logout":
                    self.logout()
                elif command == "exit":
                    break
                else:
                    print("Invalid command. Please try again.")


if __name__ == "__main__":
    app = CalendarsApp()
    app.run()
