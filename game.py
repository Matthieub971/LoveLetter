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
        self.espionne = None
        self.servante = None
        self.pretre = None
        self.garde = None
        self.is_playing = 0

    def draw_card(self, card: Card):
        self.hand.append(card)

    def discard_card(self, index: int):
        """Retire la carte à l'index donné et la retourne"""
        if 0 <= index < len(self.hand):
            return self.hand.pop(index)
        return None
    
    def handle_card(self, index: int):
        """
        Gère la carte jouée selon sa valeur :
        - 0 (Espionne)  → stockée dans self.espionne
        - 4 (Servante)  → stockée dans self.servante
        """
        if index < 0 or index >= len(self.hand):
            raise IndexError("Index de carte invalide")
        
        self.servante = None
        self.pretre = None

        card = self.hand[index]

        match card.value:
            case 0:
                self.espionne = card
                self.is_playing = 0
            case 1:
                self.is_playing = 2
            case 2:
                self.is_playing = 2
            case 3:
                self.is_playing = 2
            case 4:
                self.servante = card
                self.is_playing = 0
            case 5:
                for i in range(2):
                    if self.hand[i].value == 8:
                        self.is_playing = 0
                        return self.discard_card(i)
                self.is_playing = 2
            case 6:                
                self.is_playing = 4
            case 7:
                for i in range(2):
                    if self.hand[i].value == 8:
                        self.is_playing = 0
                        return self.discard_card(i)
                self.is_playing = 2
            case 8:
                self.is_playing = 0
            case 9:
                self.eliminated = True
                self.is_playing = 0

        return self.discard_card(index)


    def to_dict(self):
        """Version complète pour le joueur lui-même"""
        return {
            "sid": self.sid,
            "name": self.name,
            "hand": [card.to_dict() for card in self.hand],
            "eliminated": self.eliminated
        }
    
    def get_hand(self):
        return [card.to_dict() for card in self.hand]
    
    def get_visible_hand(self):
        return {
            "card": [self.pretre.to_dict()] if self.pretre else []
        }

class Game:
    def __init__(self):
        self.players = []  # Liste d'objets Player
        self.deck = []  # Liste d'objets Card
        self.discard_pile = []  # Liste d'objets Card
        self.started = False
        self.current_turn_index = 0
        self.roles = []
        self.target = None
        self.winner = []

    def add_player(self, sid: str, name: str):
        self.players.append(Player(sid, name))

    def remove_player(self, sid: str):
        self.players = [p for p in self.players if p.sid != sid]

    def setup_deck(self):
        """Crée le deck avec les cartes et mélange"""
        self.deck = (
            [Card("Espionne", 0, "/static/cartes/Espionne.png") for _ in range(2)] +
            [Card("Garde", 1, "/static/cartes/Garde.png") for _ in range(6)] +
            [Card("Prêtre", 2, "/static/cartes/Pretre.png") for _ in range(2)] +
            [Card("Baron", 3, "/static/cartes/Baron.png") for _ in range(2)] +
            [Card("Servante", 4, "/static/cartes/Servante.png") for _ in range(2)] +
            [Card("Prince", 5, "/static/cartes/Prince.png") for _ in range(2)] +
            [Card("Chancelier", 6, "/static/cartes/Chancelier.png") for _ in range(2)] +
            [Card("Roi", 7, "/static/cartes/Roi.png")] +
            [Card("Comtesse", 8, "/static/cartes/Comtesse.png")] +
            [Card("Princesse", 9, "/static/cartes/Princesse.png")]
        )

        random.shuffle(self.deck)
        self.deck.pop(0)

    def setup_roles(self):
        """Crée le deck avec les cartes et mélange"""
        self.roles = (
            [Card("Espionne", 0, "/static/cartes/Espionne.png")] +
            [Card("Prêtre", 2, "/static/cartes/Pretre.png")] +
            [Card("Baron", 3, "/static/cartes/Baron.png")] +
            [Card("Servante", 4, "/static/cartes/Servante.png")] +
            [Card("Prince", 5, "/static/cartes/Prince.png")] +
            [Card("Chancelier", 6, "/static/cartes/Chancelier.png")] +
            [Card("Roi", 7, "/static/cartes/Roi.png")] +
            [Card("Comtesse", 8, "/static/cartes/Comtesse.png")] +
            [Card("Princesse", 9, "/static/cartes/Princesse.png")]
        )

    def start_game(self):
        """Initialise la partie"""
        if len(self.players) < 2:
            raise ValueError("Il faut au moins 2 joueurs pour commencer")

        self.started = True
        self.setup_roles()
        self.setup_deck()

        # Distribuer 1 carte à chaque joueur
        for player in self.players:
            self.draw_for_player(player.sid)

        self.current_turn_index = 0
        self.players[self.current_turn_index].is_playing = 1

        self.discard_pile.append(Card("Dos", -1, "/static/cartes/Dos.png"))

        self.draw_for_player(self.players[self.current_turn_index].sid)

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
        
        while self.players[self.current_turn_index].eliminated:
            self.current_turn_index = (self.current_turn_index + 1) % len(self.players)

        self.players[self.current_turn_index].is_playing = 1

        # Tirer une carte pour le joueur actif
        self.draw_for_player(self.players[self.current_turn_index].sid)

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

    def to_dict(self):
        """Retourne un dictionnaire représentant l'état du jeu (pour tous les joueurs)"""
        return {
            "players": [p.to_dict() for p in self.players],
            "deck": [c.to_dict() for c in self.deck],
            "discard_pile": [c.to_dict() for c in self.discard_pile],
            "current_turn_index": self.current_turn_index
        }
    
    def get_infos_players(self):
        return [
            {
                "name": player.name,
                "sid": player.sid,
                "eliminated": player.eliminated,
                "card": (
                    player.servante.path if player.servante 
                    else player.espionne.path if player.espionne 
                    else "/static/cartes/Dos.png"
                )
            } for player in self.players
        ]

    def get_discard_pile(self):
        return [card.to_dict() for card in self.discard_pile]
    
    def get_roles(self):
        return [card.to_dict() for card in self.roles]
    
    def check_winner(self):
        self.winner = []
        max = -1
        active_players = [p for p in self.players if not p.eliminated]

        if len(active_players) == 1:
            # Il ne reste qu'un seul joueur en jeu
            self.winner.append(active_players[0])
            return True
        else:
            if not self.deck:
                for player in active_players:
                    if player.hand[0].value > max:
                        max = player.hand[0].value
                        self.winner.append(player)
                    elif player.hand[0].value == max:
                        self.winner.append(player)
                return True
        return False
    
    def handle_turn(self, card : Card):
        if card:
            # Défausse la carte
            self.discard_pile.append(card)

            if self.players[self.current_turn_index].is_playing == 0:
                # Passer au joueur suivant
                self.next_turn()
            elif self.players[self.current_turn_index].is_playing == 4:
                # Tirer une carte pour le joueur actif
                self.draw_for_player(self.players[self.current_turn_index].sid)
                self.draw_for_player(self.players[self.current_turn_index].sid)


    def handle_player(self, sid):
        current_player = self.get_current_player()
        last_card = self.discard_pile[-1].value
        player = self.get_player_by_sid(sid)

        if not player:
            return

        if player.servante:
            return

        match last_card:
            case 1:
                self.target = player
                current_player.is_playing = 3
            case 2:
                current_player.pretre = player.hand[0]
                current_player.is_playing = 0
            case 3:
                if player.hand[0].value > current_player.hand[0].value:
                    current_player.eliminated = True
                    self.discard_pile.append(current_player.hand[0])
                    current_player.hand.pop(0)
                elif player.hand[0].value < current_player.hand[0].value:
                    player.eliminated = True
                    self.discard_pile.append(player.hand[0])
                    player.hand.pop(0)

                current_player.is_playing = 0
            case 5:
                self.discard_pile.append(player.hand[0])
                card = player.hand.pop(0)
                if card.value == 9:
                    player.eliminated = True
                else:
                    self.draw_for_player(sid)

                current_player.is_playing = 0
            case 7:
                card = player.hand[0]
                player.hand[0] = current_player.hand[0]
                current_player.hand[0] = card

                current_player.is_playing = 0

        if self.players[self.current_turn_index].is_playing == 0:
                # Passer au joueur suivant
                self.next_turn()

    def handle_chancellor(self, index):
        current_player = self.get_current_player()

        self.deck.append(current_player.hand[index])
        current_player.hand.pop(index)

        if len(current_player.hand) == 1:
            current_player.is_playing = 0

        if self.players[self.current_turn_index].is_playing == 0:
                # Passer au joueur suivant
                self.next_turn()

    def handle_garde(self, value):
        current_player = self.get_current_player()

        if self.target.hand[0].value == value:
            self.discard_pile.append(self.target.hand[0])
            self.target.hand.pop(0)
            self.target.eliminated = True
            self.target = None

        current_player.is_playing = 0
        self.next_turn()





