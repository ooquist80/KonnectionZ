from datetime import datetime

from app.db.client import DatabaseClient
from app.models.game import GameRead, GameNotFoundError, GameWrite, GameAlreadyCompletedError
from app.models.gameset import GameSetNotFoundError, GameSetRead
from app.models.user import UserNotFoundError, UserRead
from app.repositories.game_repository import GameRepository
from app.repositories.gameset_repository import GameSetRepository
from app.repositories.user_repository import UserRepository
from app.repositories.wordset_repository import WordsetRepository


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
        created_game = self.game_repository.create(user.id, game_write, gameset)
        return created_game

    def get_game(self, game_id: int) -> GameRead:
        game = self.game_repository.get_by_id(game_id)
        if game is None:
            raise GameNotFoundError(f"Game with id: {game_id} was not found.")
        return game

    # def play_words(self, game, played_words) -> ResultMessage:
    #     if game.end_time is not None:
    #         raise GameAlreadyCompletedError(f"Game with id: {game.id} is already completed.")
    #     gameset_record = self.gameset_repository.get_by_id(game.gameset_id)
    #     wordsets = []
    #     for wordset_id in gameset_record.wordsets:
    #         wordset = self.wordset_repository.get_by_id(wordset_id)
    #         wordsets.append(wordset)
    #
    #     for wordset in wordsets:
    #         correct_word_count = 0
    #         if wordset not in game.completed_wordsets:
    #             for word in wordset.words:
    #                 if word in played_words:
    #                     correct_word_count = correct_word_count + 1
    #             if correct_word_count == len(wordset.words):
    #                 self.game_repository.add_completed_wordset(game_id=game.id, wordset_id=wordset.id)
    #                 if len(game.completed_wordsets) == len(wordsets) - 1:
    #                     self.game_repository.add_game_end_time(game_id=game.id, end_time=datetime.now())
    #                     return ResultMessage.COMPLETED
    #                 else:
    #                     return ResultMessage.CORRECT
    #             if correct_word_count == len(wordset.words) - 1:
    #                 return ResultMessage.ALMOST_CORRECT
    #
    #     return ResultMessage.INCORRECT

    def get_games(self):
        games = self.game_repository.get_all()
        return games

