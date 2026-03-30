from datetime import datetime

from app.db.client import DatabaseClient
from app.models.game import GameRead, GameNotFoundError, ResultMessage, GameWrite, GameAlreadyCompletedError
from app.models.gameset import GameSetNotFoundError
from app.models.user import UserNotFoundError, UserRead
from app.repositories.game import GameRepository
from app.repositories.gameset import GameSetRepository
from app.repositories.user import UserRepository
from app.repositories.wordset import WordsetRepository


class GameService:

    def __init__(self, database_client: DatabaseClient) -> None:
        self.game_repository = GameRepository(database_client)
        self.user_repository = UserRepository(database_client)
        self.gameset_repository = GameSetRepository(database_client)
        self.wordset_repository = WordsetRepository(database_client)

    def create_game(self, user: UserRead, game_write : GameWrite) -> GameRead:
        gameset = self.gameset_repository.get_by_id(game_write.gameset_id)
        if gameset is None:
            raise GameSetNotFoundError(f"Gameset with id: {game_write.gameset_id} was not found.")
        created_game = self.game_repository.create(user.id, game_write)
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

    def play_words(self, game, played_words) -> ResultMessage:
        if game.end_time is not None:
            raise GameAlreadyCompletedError(f"Game with id: {game.id} is already completed.")
        gameset_record = self.gameset_repository.get_by_id(game.gameset_id)
        wordsets = []
        for wordset_id in gameset_record.wordsets:
            wordset = self.wordset_repository.get_by_id(wordset_id)
            wordsets.append(wordset)

        for wordset in wordsets:
            correct_word_count = 0
            if wordset not in game.completed_wordsets:
                for word in wordset.words:
                    if word in played_words:
                        correct_word_count = correct_word_count + 1
                if correct_word_count == len(wordset.words):
                    self.game_repository.add_completed_wordset(game_id=game.id, wordset_id=wordset.id)
                    if len(game.completed_wordsets) == len(wordsets) - 1:
                        self.game_repository.add_game_end_time(game_id=game.id, end_time=datetime.now())
                        return ResultMessage.COMPLETED
                    else:
                        return ResultMessage.CORRECT
                if correct_word_count == len(wordset.words) - 1:
                    return ResultMessage.ALMOST_CORRECT

        return ResultMessage.INCORRECT

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

