# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json

from datetime import datetime

# actions.py

def time_to_float(time_str):
    time_obj = datetime.strptime(time_str, "%H:%M")
    time_float = time_obj.hour + time_obj.minute / 60.0

    return time_float


# def read_opening_hours_from_file(file_path: Text) -> Dict[Text, Any]:
#     # Read opening hours data from a JSON file
#     with open(file_path, "r") as file:
#         opening_hours = json.load(file)
#
#     return opening_hours


def is_restaurant_open(requested_day, requested_hour=None):

    # print("requested_day", requested_day)

    with open("data/opening_hours.json", "r") as file:
        data = json.load(file)

    opening_hours = data.get("items")
    opening_hours_per_day = opening_hours.get(requested_day, {})
    if requested_hour:
        is_open = float(opening_hours_per_day.get("open")) <= time_to_float(requested_hour) < float(
            opening_hours_per_day.get("close"))
    else:
        is_open = True

    return is_open, opening_hours_per_day


class ActionGetOpenInformation(Action):
    def name(self) -> Text:
        return "action_get_open_information"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        requested_day = next(tracker.get_latest_entity_values("day_"), None)
        requested_time = next(tracker.get_latest_entity_values("time_"), None)

        if requested_day is None or requested_day not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                                                          "Saturday", "Sunday"]:
            dispatcher.utter_message("I can't recognize the weekday you provided")
            return []

        is_open, opening_hours = is_restaurant_open(requested_day, requested_time)

        if is_open:
            if requested_time and requested_time:
                dispatcher.utter_message(
                    f"Yes, the restaurant is open on {requested_day} at {requested_time}.\n \
                    The opening hours are {opening_hours}.")
            elif requested_time is None:
                dispatcher.utter_message(f"Yes, the restaurant is open on {requested_day}.\n The opening hours are {opening_hours['open']} - {opening_hours['close']}.")

        else:
            dispatcher.utter_message(
                f"No, the restaurant is closed on {requested_day} at {requested_time}.\n The opening hours are: {opening_hours['open']} - {opening_hours['close']}.")

        return []


class ActionShowOpeningHours(Action):
    def name(self) -> Text:
        return "action_show_opening_hours"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open("data/opening_hours.json", "r") as file:
            data = json.load(file)

        opening_hours = data.get("items")

        response_message = "Here are the opening hours:\n"
        for day, hours in opening_hours.items():
            response_message += f"{day}: {hours['open']}  - {hours['close']} \n"

        dispatcher.utter_message(f"The opening hours are:\n{response_message}")

        return []


class ActionOrderFood(Action):
    def name(self) -> Text:
        return "action_order_food"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        food_item = next(tracker.get_latest_entity_values("food_item"), None)
        quantity = next(tracker.get_latest_entity_values("quantity"), None)
        special_request = next(tracker.get_latest_entity_values("special_request"), None)
        with_ = next(tracker.get_latest_entity_values("with_"), None)

        if food_item is None:
            dispatcher.utter_message("I cant recognize your food. Write one more time")

        with open("data/menu.json") as file:
            menu_data = json.load(file)

        items = menu_data.get('items', [])
        menu_items = [
            {"name": item.get('name', ''),
             "price": item.get('price', 0),
             "preparation_time": item.get('preparation_time', 0)}
            for item in items
        ]
        preparation_time = 0
        in_menu = False
        for item in menu_items:
            if item["name"] == food_item:
                preparation_time = item["preparation_time"]
                in_menu = True
                break
        if in_menu:
            preparation_time = float(preparation_time) * 60.0
        else:
            preparation_time = 45
        if quantity is None:
            quantity = 1

        if special_request and in_menu:
            dispatcher.utter_message(f"Your order has been placed. Waiting time: {preparation_time} minutes:\nfood: {food_item}\nquantity: {quantity}\nspecial request: {with_} {special_request}.")
        elif in_menu:
            dispatcher.utter_message(f"Your order has been placed. Waiting time: {preparation_time} minutes :\nfood: {food_item}\nquantity: {quantity}")
        elif special_request and in_menu is False:
            dispatcher.utter_message(f"Your order is not in our menu. You have to wait more time: {preparation_time} minutes.\nfood: {food_item}\nquantity: {quantity}\nspecial request: {with_} {special_request}.")
        else:
            dispatcher.utter_message(
                f"Your order is not in our menu. Waiting time: {preparation_time} minutes:\nfood: {food_item}\nquantity: {quantity}")



        # if food_item and special_request and quantity:
        #     dispatcher.utter_message(f"Your order of {quantity} {food_item} {with_} {special_request} has been placed.")
        # elif food_item and quantity:
        #     dispatcher.utter_message(f"Your order of {quantity} {food_item} has been placed.")
        # else:
        #     dispatcher.utter_message(f"Your order of {food_item} has been placed.")
        return []


class ActionShowMenu(Action):

    def name(self) -> Text:
        return "action_show_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open("data/menu.json") as file:
            menu_data = json.load(file)

        items = menu_data.get('items', [])
        menu_items = [
            {"name": item.get('name', ''),
             "price": item.get('price', 0),
             "preparation_time": item.get('preparation_time', 0)}
            for item in items
        ]

        menu_message = "Here's our menu:\n"
        for item in menu_items:
            menu_message += f"- {item['name'].capitalize()}: ${item['price']:.2f}, Preparation Time: {item['preparation_time']} hours\n"

        dispatcher.utter_message(text=menu_message)

        return []
