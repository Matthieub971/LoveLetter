import random

class Player:
    def __init__(self, sid, username):
        self.sid = sid
        self.username = username
        self.hand = []
        self.eliminated = False

    def draw_card(self, deck):
        if deck:
            self.hand.append(deck.pop())

    def play_card(self, card_index):
        if 0 <= card_index < len(self.hand):
            return self.hand.pop(card_index)
        return None

class Game:
    def __init__(self):
        self.players = []
        self.deck = []
        self.discard_pile = []
        self.started = False
        self.current_turn = 0

    def add_player(self, sid, username):
        if not self.started:
            self.players.append(Player(sid, username))
            return True
        return False

    def start(self):
        if len(self.players) < 2:
            return False

        self.started = True
        self.deck = self.generate_deck()
        random.shuffle(self.deck)

        # Chaque joueur pioche 1 carte
        for player in self.players:
            player.draw_card(self.deck)

        self.current_turn = 0
        return True

    def generate_deck(self):
        # Deck simplifié (Love Letter a 16 cartes)
        deck = []
        deck += ["Espionne"] * 2
        deck += ["Garde"] * 6
        deck += ["Pretre"] * 2
        deck += ["Baron"] * 2
        deck += ["Servante"] * 2
        deck += ["Prince"] * 2
        deck += ["Chancelier"] * 2
        deck += ["Roi"] * 1
        deck += ["Comtesse"] * 1
        deck += ["Princesse"] * 1
        return deck

    def get_game_state_for(self, username):
        return {
            "players": [
                {
                    "username": p.username,
                    "hand": p.hand if p.username == username else [],
                    "hand_count": len(p.hand),
                    "eliminated": p.eliminated
                }
                for p in self.players
            ],
            "discard_pile": self.discard_pile,
            "current_turn": self.players[self.current_turn].username if self.players else None,
            "deck_count": len(self.deck),
            "started": self.started
        }


    def play_card(self, sid, card_index):
        player = self.get_player_by_sid(sid)
        if player and self.players[self.current_turn].sid == sid:
            card = player.play_card(card_index)
            if card:
                self.discard_pile.append({"player": player.username, "card": card})
                # Pioche une nouvelle carte
                player.draw_card(self.deck)
                # Tour suivant
                self.current_turn = (self.current_turn + 1) % len(self.players)
                return True
        return False

    def get_player_by_sid(self, sid):
        for p in self.players:
            if p.sid == sid:
                return p
        return None
