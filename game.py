# game.py
import random


class Card:
    def __init__(self, name: str, value: int, path: str):
        self.name = name
        self.value = value
        self.path = path

    def to_dict(self):
        """Pour envoyer facilement la carte au client"""
        return {
            "name": self.name,
            "value": self.value,
            "image": self.path
        }


class Player:
    def __init__(self, sid: str, name: str):
        self.sid = sid
        self.name = name
        self.hand = []  # Liste d'objets Card
        self.eliminated = False

    def draw_card(self, card: Card):
        self.hand.append(card)

    def discard_card(self, index: int):
        """Retire la carte à l'index donné et la retourne"""
        if 0 <= index < len(self.hand):
            return self.hand.pop(index)
        return None

    def to_public_dict(self):
        """Infos visibles par les autres joueurs (pas la main complète)"""
        return {
            "name": self.name,
            "eliminated": self.eliminated
        }

    def to_private_dict(self):
        """Infos visibles par le joueur lui-même (avec main complète)"""
        return {
            "name": self.name,
            "hand": [card.to_dict() for card in self.hand],
            "eliminated": self.eliminated
        }


class Game:
    def __init__(self):
        self.players = []  # Liste d'objets Player
        self.deck = []  # Liste d'objets Card
        self.discard_pile = []  # Liste d'objets Card
        self.started = False
        self.current_turn_index = 0

    def add_player(self, sid: str, name: str):
        self.players.append(Player(sid, name))

    def remove_player(self, sid: str):
        self.players = [p for p in self.players if p.sid != sid]

    def setup_deck(self):
        """Crée le deck avec les cartes et mélange"""
        self.deck = [
            Card("Espionne", 0, "/static/cartes/Espionne.png"),
            Card("Garde", 1, "/static/cartes/Garde.png"),
            Card("Prêtre", 2, "/static/cartes/Pretre.png"),
            Card("Baron", 3, "/static/cartes/Baron.png"),
            Card("Servante", 4, "/static/cartes/Servante.png"),
            Card("Prince", 5, "/static/cartes/Prince.png"),
            Card("Chancelier", 6, "/static/cartes/Chancelier.png"),
            Card("Roi", 7, "/static/cartes/Roi.png"),
            Card("Comtesse", 8, "/static/cartes/Comtesse.png"),
            Card("Princesse", 9, "/static/cartes/Princesse.png"),
        ] * 2  # Ex : 2 exemplaires de chaque carte pour les tests
        random.shuffle(self.deck)

    def start_game(self):
        """Initialise la partie"""
        if len(self.players) < 2:
            raise ValueError("Il faut au moins 2 joueurs pour commencer")

        self.started = True
        self.setup_deck()

        # Distribuer 1 carte à chaque joueur
        for player in self.players:
            self.draw_for_player(player.sid)

        self.current_turn_index = 0

    def draw_for_player(self, sid: str):
        """Donner une carte du deck à un joueur"""
        player = self.get_player_by_sid(sid)
        if player and self.deck:
            card = self.deck.pop(0)
            player.draw_card(card)

    def get_player_by_sid(self, sid: str):
        for p in self.players:
            if p.sid == sid:
                return p
        return None

    def next_turn(self):
        """Passer au joueur suivant"""
        if not self.players:
            return
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players)

    def get_current_player(self):
        if not self.players:
            return None
        return self.players[self.current_turn_index]

    def reset_game(self):
        self.players.clear()
        self.deck.clear()
        self.discard_pile.clear()
        self.started = False
        self.current_turn_index = 0
