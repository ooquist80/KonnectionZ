from app.models.wordset import WordsetNotFoundError
from app.repositories.game import GameRepository
from app.repositories.wordset import WordsetRepository
from app.repositories.user import UserRepository
from app.repositories.gameset import GameSetRepository
from app.repositories.game import Wordset
from app.models.game import GameRead, GameNotFoundError, Resultmessage
from app.models.user import User, UserNotFoundError
from app.models.gameset import GameSet, GameSetNotFoundError
from app.db.client import DatabaseClient
from datetime import datetime


class GameService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.game_repository = GameRepository(database_client)
        self.user_repository = UserRepository(database_client)
        self.gameset_repository = GameSetRepository(database_client)
        self.wordset_repository = WordsetRepository(database_client)

    def create_game(self, payload) -> GameRead:
        start_time = datetime.now()
        user = self.user_repository.get_by_id(user_id= payload.user_id)
        if user is None:
            raise UserNotFoundError(f"User with id: {payload.user_id} was not found.")
        gameset = self.gameset_repository.get_by_id(payload.gameset_id)
        if gameset is None:
            raise GameSetNotFoundError(f"Gameset with id: {payload.gameset_id} was not found.")

        created_game = self.game_repository.create(user_id=payload.user_id, gameset_id=payload.gameset_id,
                                                   start_time=start_time)
        return created_game

    def get_game(self, game_id: int) -> GameRead:
        game_record = self.game_repository.get_by_id(game_id)
        if game_record is None:
            raise GameNotFoundError(f"Game with id: {game_id} was not found.")
        wordsets = []
        for wordset_id in game_record.completed_wordset_ids:
            wordsets.append(self.wordset_repository.get_by_id(wordset_id))
        return GameRead(id=game_record.id, user_id=game_record.user_id, gameset_id=game_record.gameset_id, start_time=game_record.start_time,
                        end_time=game_record.end_time, completed_wordsets=wordsets)



    def play_words(self, game, payload) -> Resultmessage:
        gameset_record = self.gameset_repository.get_by_id(game.gameset_id)
        wordsets = []
        for wordset_id in gameset_record.wordsets:
            wordset = self.wordset_repository.get_by_id(wordset_id)
            wordsets.append(wordset)

        for wordset in wordsets:
            correct_word_count = 0
            if wordset not in game.completed_wordsets:
                for word in wordset.words:
                    if word in payload:
                        correct_word_count = correct_word_count + 1
                if correct_word_count == 4:
                    self.game_repository.add_completed_wordset(game_id=game.id, wordset_id=wordset.id)
                    if len(game.completed_wordsets) == 3:
                        self.game_repository.add_game_end_time(game_id=game.id, end_time=datetime.now())
                    return Resultmessage.CORRECT
                if correct_word_count == 3:
                    return Resultmessage.CORRECT

        return Resultmessage.INCORRECT

    def get_games(self):
        game_records = self.game_repository.get_all()
        games = []
        for game_record in game_records:
            wordsets = []
            for wordset_id in game_record.completed_wordset_ids:
                wordsets.append(self.wordset_repository.get_by_id(wordset_id))
            games.append(GameRead(id=game_record.id, user_id=game_record.user_id, gameset_id=game_record.gameset_id, start_time=game_record.start_time,
                                  end_time=game_record.end_time, completed_wordsets=wordsets))
        return games

