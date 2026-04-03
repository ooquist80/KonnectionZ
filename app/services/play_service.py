from datetime import datetime
import random
from app.db.client import DatabaseClient
from app.models.game import GameBelongsToAnotherUserError, GameNotFoundError, GameRead
from app.models.play import GameStatus, PlayResult, GameAlreadyCompletedError, ResultMessage, PlayGameSet
from app.models.wordset import WordsetRead
from app.repositories.game_repository import GameRepository
from app.repositories.gameset_repository import GameSetRepository


def get_correct_word_count(words, played_words):
    count = 0
    for word in words:
        if word.word in played_words:
            count += 1
    return count


def get_result(game: GameRead, played_words) -> tuple[ResultMessage, WordsetRead | None]:
    for wordset in game.gameset.wordsets:
        if wordset.id not in game.completed_wordsets:
            correct_word_count = get_correct_word_count(wordset.words, played_words)
            if correct_word_count == len(wordset.words):
                return ResultMessage.CORRECT, wordset
            elif correct_word_count == len(wordset.words) - 1:
                return ResultMessage.ALMOST_CORRECT, None
    return ResultMessage.INCORRECT, None


class PlayService:
    def __init__(self, database_client: DatabaseClient):
        self.game_repository = GameRepository(database_client)
        self.gameset_repository = GameSetRepository(database_client)

    def start_or_resume_daily_game(self, user_id: int):
        daily_gameset_id = self.gameset_repository.get_latest_daily_gameset_id()
        return self.start_or_resume_game(user_id=user_id, gameset_id=daily_gameset_id)

    def start_or_resume_game(self, user_id: int, gameset_id : int) -> PlayResult:
        played_games = self.game_repository.get_by_user_id(user_id=user_id)
        game = None
        for played_game in played_games:
            if played_game.gameset.id == gameset_id:
                game = played_game
        if not game:
            game = self.game_repository.create(gameset_id=gameset_id, user_id=user_id)
        words_remaining = []
        completed_wordsets = []
        for wordset in game.gameset.wordsets:
            if wordset.id not in game.completed_wordsets:
                for word in wordset.words:
                    words_remaining.append(word.word)
            else:
                completed_wordsets.append(wordset)
        random.shuffle(words_remaining)
        game_status = GameStatus(game_name=game.gameset.name,
                                 start_time=game.start_time,
                                 end_time=game.end_time,
                                 words_remaining=words_remaining,
                                 wordsets_completed=completed_wordsets,
                                 turn_count=game.turn_count)
        return PlayResult(game_id=game.id, game_status=game_status)

    def play_words(self, game_id, user_id, played_words) -> PlayResult:
        game = self.game_repository.get_by_id(game_id)
        if not game:
            raise GameNotFoundError(f"Game with id: {game_id} not found")
        if game.user_id != user_id:
            raise GameBelongsToAnotherUserError(f"Game with id: {game_id} belongs to another user")
        if game.end_time is not None:
            raise GameAlreadyCompletedError(f"Game with id: {game.id} is already completed.")
        result_message, correct_wordset = get_result(game, played_words)
        self.game_repository.increment_turn_count(game_id=game.id)
        if correct_wordset:
            self.game_repository.add_completed_wordset(game_id, correct_wordset.id)
            if len(game.completed_wordsets) == len(game.gameset.wordsets) - 1:
                result_message = ResultMessage.COMPLETED
                self.game_repository.add_game_end_time(game_id=game.id, end_time=datetime.now())
        game = self.game_repository.get_by_id(game_id)
        words_remaining = []
        completed_wordsets = []
        for wordset in game.gameset.wordsets:
            if wordset.id not in game.completed_wordsets:
                for word in wordset.words:
                    words_remaining.append(word.word)
            else:
                completed_wordsets.append(wordset)
        random.shuffle(words_remaining)
        game_status = GameStatus(game_name=game.gameset.name,
                                 start_time=game.start_time,
                                 end_time=game.end_time,
                                 words_remaining=words_remaining,
                                 wordsets_completed=completed_wordsets,
                                 turn_count=game.turn_count)
        return PlayResult(game_id=game.id, game_status=game_status, result_message=result_message)

    def get_available_gamesets(self):
        gamesets = self.gameset_repository.get_all()
        play_gamesets = []
        for gameset in gamesets:
            play_gamesets.append(PlayGameSet(id=gameset.id, name=gameset.name))
        return play_gamesets
