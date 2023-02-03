import random
from enum import Enum, auto

class _GameStates(Enum):
    GAME_NOT_STARTED = auto()
    WAITING_FOR_PLAYER_INPUT = auto()
    EXIT_STATE = auto()

class _PlayerCommands:
    NEW_GAME = "/new_game"
    EXIT_GAME = "/exit_game"

class _GameMessages:
    TO_START = "Чтобы начать новую игру, введите %s\n" % _PlayerCommands.NEW_GAME + \
               "Вы можете начать новую игру в любой момент."
    TO_END = "Чтобы выйти из игры, введите %s\n" % _PlayerCommands.EXIT_GAME + \
             "Вы можете выйти из игры в любой момент."
    NEW_GAME = "Новая игра."
    NEXT_CITY = "Следующий город на %s."
    AI_S_TURN = "Мой город: %s."
    PLAYER_S_TURN = "Введите ваш город."
    NO_SUCH_CITY = "Я не знаю такого города."
    CITY_ALREADY_BEEN = "Такой город уже был."
    WRONG_FIRST_LETTER = "Не с той буквы."
    ENTER_ANOTHER_CITY = "Введите другой город."
    YOU_WON = "Я не знаю таких городов.\n" + \
              "Поздравляю! Вы победили!"

class CitiesGame:
    _cities = []
    _cities_initialized = False

    @classmethod
    def _init_cities(cls, file_name = "cities_utf8.txt", encoding = "utf-8"):
        if not cls._cities_initialized:
            with open(file_name, "r", encoding = encoding) as f_in:
                for line in f_in:
                    line = line.strip()
                    cls._cities.append(line)
            cls._cities_initialized = True

    def __init__(self):
        CitiesGame._init_cities()
        
        self._random_generator = random.Random()
        self._random_generator.seed()
        self._state = _GameStates.GAME_NOT_STARTED
        self._current_cities = []
        self._first_letters = []
        self._current_messages = self._get_messages_not_started()

    def _get_messages_not_started(self):
        return [_GameMessages.TO_START, _GameMessages.TO_END]

    def _start_new_game(self):
        self._current_cities = CitiesGame._cities.copy()
        self._first_letters = []
        self._current_messages += [_GameMessages.NEW_GAME]
        is_ai_first = self._random_generator.choice([False, True])
        if is_ai_first:
            self._make_ai_turn()
        else:
            self._current_messages += [_GameMessages.PLAYER_S_TURN]
            self._state = _GameStates.WAITING_FOR_PLAYER_INPUT

    def _end_current_game(self):
        self._current_messages += self._get_messages_not_started()
        self._state = _GameStates.GAME_NOT_STARTED

    def _make_ai_turn(self):
        if self._first_letters:
            cities_to_choose = list(filter(lambda city: any(city.startswith(first_letter)
                                               for first_letter in self._first_letters),
                                           self._current_cities))
        else:
            cities_to_choose = self._current_cities
        if cities_to_choose:
            city = self._random_generator.choice(cities_to_choose)
            self._current_messages += [_GameMessages.AI_S_TURN % city]
            self._current_cities.remove(city)
            self._calculate_next_first_letters(city)
            self._current_messages += [_GameMessages.PLAYER_S_TURN]
            self._state = _GameStates.WAITING_FOR_PLAYER_INPUT
        else:
            self._current_messages += [_GameMessages.YOU_WON]
            self._end_current_game()

    def _process_player_turn(self, player_input):
        if self._find_city_in_list(CitiesGame._cities, player_input):
            if (not self._first_letters) or (player_input[0].upper() in self._first_letters):
                if found_city := self._find_city_in_list(self._current_cities, player_input):
                    self._current_cities.remove(found_city)
                    self._calculate_next_first_letters(found_city)                   
                    self._make_ai_turn()
                else:
                    self._current_messages += [_GameMessages.CITY_ALREADY_BEEN, _GameMessages.ENTER_ANOTHER_CITY]
            else:
                self._current_messages += [_GameMessages.WRONG_FIRST_LETTER, _GameMessages.ENTER_ANOTHER_CITY]
        else:
            self._current_messages += [_GameMessages.NO_SUCH_CITY, _GameMessages.ENTER_ANOTHER_CITY]
        
    def _calculate_next_first_letters(self, city):
        last_letter = city[-1]
        if last_letter == "ь":
            self._first_letters = [city[-2].upper()]
        elif last_letter == "ы":
            self._first_letters = [city[-2].upper(), "Ы"]
        elif last_letter == "й":
            self._first_letters = ["Й", "И"]
        elif last_letter == "ё":
            self._first_letters = ["Ё", "Е"]
        elif last_letter == "Ъ":
            self._first_letters = ["Ъ"]
        else:
            self._first_letters = [last_letter.upper()]
        self._current_messages += [_GameMessages.NEXT_CITY % " или ".join(self._first_letters)]

    def _find_city_in_list(self, cities_list, city_input):
        for city in cities_list:
            if city.lower().replace("-", " ").replace("ё", "е") == \
               city_input.lower().replace("-", " ").replace("ё", "е"):
                return city
        return None

    def get_current_messages(self):
        return list(self._current_messages)

    def process_player_input(self, player_input):
        self._current_messages = []
        if player_input == _PlayerCommands.EXIT_GAME:
            self._state = _GameStates.EXIT_STATE
        elif player_input == _PlayerCommands.NEW_GAME:
            self._start_new_game()
        elif self._state == _GameStates.GAME_NOT_STARTED:
            self._current_messages += self._get_messages_not_started()
        elif self._state == _GameStates.WAITING_FOR_PLAYER_INPUT:
            self._process_player_turn(player_input)
        else:
            assert False, "Unknown state"

    def is_exit_state(self):
        return self._state == _GameStates.EXIT_STATE
