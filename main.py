from cities_game import CitiesGame

game = CitiesGame()

while True:
    game_messages = game.get_current_messages()
    for message in game_messages:
        print(message)
    player_input = input()
    game.process_player_input(player_input)
    if game.is_exit_state():
        break
    