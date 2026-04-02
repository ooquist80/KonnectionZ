from datetime import datetime

from app.db.client import DatabaseClient
from app.models.game import GameBelongsToAnotherUserError, GameNotFoundError
from app.models.play import GameStatus, PlayResult, GameAlreadyCompletedError, ResultMessage
from app.repositories.game_repository import GameRepository


class PlayService:
    def __init__(self, database_client: DatabaseClient):
        self.game_repository = GameRepository(database_client)

    def start_game(self, gameset_id, user_id) -> PlayResult:
        game = self.game_repository.create(gameset_id, user_id)
        words_remaining = []
        for wordset in game.gameset.wordsets:
            for word in wordset.words:
                words_remaining.append(word.word)

        game_status = GameStatus(start_time=game.start_time,
                                 end_time=game.end_time,
                                 words_remaining=words_remaining,
                                 wordsets_completed=[],
                                 turn_count=0)
        return PlayResult(game_id=game.id, game_status=game_status)

    def play_words(self, game_id, user_id, played_words) -> PlayResult:
        game = self.game_repository.get_by_id(game_id)
        if not game:
            raise GameNotFoundError(f"Game with id: {game_id} not found")
        if game.user_id != user_id:
            raise GameBelongsToAnotherUserError(f"Game with id: {game_id} belongs to another user")
        if game.end_time is not None:
            raise GameAlreadyCompletedError(f"Game with id: {game.id} is already completed.")
        for wordset in game.gameset.wordsets:
            correct_word_count = 0
            if wordset not in game.completed_wordsets:
                for word in wordset.words:
                    if word.word in played_words:
                        correct_word_count += 1
                if correct_word_count == len(wordset.words):
                    self.game_repository.add_completed_wordset(game_id=game.id, wordset_id=wordset.id)
                    result_message = ResultMessage.CORRECT
                elif correct_word_count == len(wordset.words) - 1:
                    result_message = ResultMessage.ALMOST_CORRECT
                else:
                    result_message = ResultMessage.INCORRECT
        game = self.game_repository.get_by_id(game_id)
        if len(game.completed_wordsets) == len(game.gameset.wordsets):
            result_message = ResultMessage.COMPLETED
            self.game_repository.add_game_end_time(game_id=game.id, end_time=datetime.now())

        words_remaining = []
        for wordset in game.gameset.wordsets:
            if wordset.id not in game.completed_wordsets:
                for word in wordset.words:
                    words_remaining.append(word.word)
        game_status = GameStatus(start_time=game.start_time,
                                 end_time=game.end_time,
                                 words_remaining=words_remaining,
                                 wordsets_completed=[],
                                 turn_count=0)
        return PlayResult(game_id=game.id, game_status=game_status, result_message=result_message)
